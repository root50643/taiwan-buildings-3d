"""Actually slice every physical STL with PrusaSlicer 2.9.6, preserving each run.

Outputs are QA toolpaths only. Profile deliberately lacks machine start/end code.
"""
import argparse, datetime, hashlib, json, os, re, subprocess, time, shutil
from pathlib import Path

SLICER=os.environ.get('PRUSASLICER_EXE') or shutil.which('prusa-slicer-console') or shutil.which('prusa-slicer-console.exe') or 'prusa-slicer-console'
PROFILE='''# Generic single-material QA profile; not machine-ready; millimetres
printer_technology = FFF
bed_shape = 0x0,220x0,220x220,0x220
max_print_height = 200
gcode_flavor = marlin2
nozzle_diameter = 0.4
filament_diameter = 1.75
filament_type = PLA
filament_density = 1.24
extrusion_multiplier = 1
layer_height = 0.2
first_layer_height = 0.2
perimeters = 3
top_solid_layers = 4
bottom_solid_layers = 4
fill_density = 15%
fill_pattern = rectilinear
perimeter_generator = arachne
extrusion_width = 0.45
first_layer_extrusion_width = 0.45
perimeter_extrusion_width = 0.45
external_perimeter_extrusion_width = 0.45
infill_extrusion_width = 0.45
solid_infill_extrusion_width = 0.45
top_infill_extrusion_width = 0.45
support_material_extrusion_width = 0.4
temperature = 205
first_layer_temperature = 205
bed_temperature = 60
first_layer_bed_temperature = 60
perimeter_speed = 35
external_perimeter_speed = 25
infill_speed = 55
solid_infill_speed = 40
top_solid_infill_speed = 30
bridge_speed = 20
first_layer_speed = 20
travel_speed = 150
retract_length = 0.8
retract_speed = 30
cooling = 1
fan_always_on = 1
min_fan_speed = 100
max_fan_speed = 100
disable_fan_first_layers = 1
skirts = 1
skirt_distance = 3
brim_width = 0
support_material_style = snug
support_material_threshold = 45
support_material_buildplate_only = 1
support_material_contact_distance = 0.2
support_material_spacing = 2
support_material_interface_layers = 3
start_gcode =
end_gcode =
before_layer_gcode =
layer_gcode =
gcode_comments = 1
remaining_times = 0
notes = QA ONLY - NOT MACHINE READY - no physical print or fit test
'''

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')

def scrub(text, root):
    # Gcode, logs and JSON carry no host user directory. STL basename is sufficient.
    for value in [str(root),str(root).replace('\\','/'),str(Path.home()),str(Path.home()).replace('\\','/')]:
        text=text.replace(value,'[local]')
    lines=[]
    for line in text.splitlines(keepends=True):
        if 'Loading MESA OpenGL library:' in line:
            line='Loading MESA OpenGL library: [slicer]/mesa/opengl32.dll\n'
        elif ('Exporting G-code to ' in line or 'Slicing result exported to ' in line) and ('[local]' in line or re.search(r'[A-Za-z]:[\\/]',line)):
            marker='Exporting G-code to ' if 'Exporting G-code to ' in line else 'Slicing result exported to '
            prefix,path=line.split(marker,1);base=re.split(r'[\\/]',path.strip())[-1]
            line=prefix+marker+'[output]/'+base+'\n'
        else:
            line=re.sub(r'(?i)\[local\][\\/][^\r\n]*','[local path redacted]',line)
            line=re.sub(r'[A-Za-z]:[\\/](?:Users|Documents)[\\/][^\r\n]*','[local path redacted]',line)
        lines.append(line)
    text=''.join(lines)
    return text

def inspect_gcode(path):
    text=path.read_text(encoding='utf-8',errors='replace')
    layer_heights=[float(x) for x in re.findall(r'^;Z:([-\d.]+)',text,re.M)]
    types={}
    for typ in re.findall(r'^;TYPE:(.*)',text,re.M):types[typ]=types.get(typ,0)+1
    # Parse extruding movement and its bed extents, not merely header metadata.
    xyz={'X':0.,'Y':0.,'Z':0.,'E':0.};absolute_e=True;absolute_xyz=True
    mins=[float('inf')]*3;maxs=[-float('inf')]*3;extrusions=0;total_pos_e=0.;role=''
    roles_e={};layer_e={};active_z=0.
    for line in text.splitlines():
        if line.startswith(';TYPE:'):role=line[6:]
        if line.startswith(';Z:'):active_z=float(line[3:])
        code=line.split(';')[0].strip()
        if code=='M82':absolute_e=True
        if code=='M83':absolute_e=False
        if code=='G90':absolute_xyz=True
        if code=='G91':absolute_xyz=False
        if not code.startswith(('G0 ','G1 ','G92 ')):continue
        vals={k:float(v) for k,v in re.findall(r'([XYZE])([-+\d.]+)',code)}
        if code.startswith('G92 '):xyz.update(vals);continue
        old=xyz.copy()
        for k,v in vals.items():xyz[k]=v if (absolute_e if k=='E' else absolute_xyz) else xyz[k]+v
        de=xyz['E']-old['E'] if 'E' in vals else 0.
        if de>1e-8 and any(k in vals for k in 'XY'):
            extrusions+=1;total_pos_e+=de;roles_e[role]=roles_e.get(role,0.)+de;layer_e[str(active_z)]=layer_e.get(str(active_z),0.)+de
            for i,k in enumerate('XYZ'):mins[i]=min(mins[i],old[k],xyz[k]);maxs[i]=max(maxs[i],old[k],xyz[k])
    estimates={}
    for key in ['estimated printing time','filament used','total filament used']:
        estimates[key]=re.findall(r'^; '+re.escape(key)+r'.*$',text,re.M)
    return {'layer_count':text.count(';LAYER_CHANGE'),'z_min_mm':min(layer_heights) if layer_heights else None,'z_max_mm':max(layer_heights) if layer_heights else None,'layer_z_values_mm':layer_heights,'extruding_move_count':extrusions,'extrusion_bounds_mm':[mins,maxs] if extrusions else None,'positive_extrusion_mm':total_pos_e,'roles':types,'extrusion_mm_by_role':roles_e,'extrusion_mm_by_layer':layer_e,'estimates':estimates,'private_absolute_path_found':bool(re.search(r'[A-Za-z]:[\\/](?:Users|Documents)[\\/]',text)),'qa_only':True}

def main():
    p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--output',required=True);p.add_argument('--slicer',default=str(SLICER));p.add_argument('--force-supports',action='store_true');p.add_argument('--run-label',default='trial-01');args=p.parse_args()
    if not Path(args.slicer).is_file(): raise FileNotFoundError('Provide PrusaSlicer console executable with --slicer or PRUSASLICER_EXE')
    manifest=Path(args.manifest).resolve();root=manifest.parent;out=Path(args.output).resolve()/args.run_label
    out.mkdir(parents=True,exist_ok=False) # Never overwrite an earlier failure.
    data=json.loads(manifest.read_text(encoding='utf-8-sig'))
    profile=out/'generic_qa_0p4mm.ini';profile.write_text(PROFILE,encoding='utf-8')
    result={'schema_version':1,'qa_only':True,'machine_ready':False,'physical_print_performed':False,'trial_fit_performed':False,'manifest_sha256':sha(manifest),'profile_sha256':sha(profile),'tool_version':'PrusaSlicer 2.9.6','tool_executable_sha256':sha(args.slicer),'parts':[]}
    for part in data['parts']:
        pid=part['id'];stl=(root/part['stl']).resolve();gcode=out/f'{pid}_QA_ONLY.gcode'
        supports=args.force_supports or part.get('supports')=='buildplate'
        cmd=[args.slicer,'--datadir',str(out/'slicer-local-settings'),'--load',str(profile),'--threads','2','--export-gcode','--center','110,110','--support-material' if supports else '--no-support-material','--output',str(gcode),str(stl)]
        brim=float(part.get('qa_brim_width_mm',0))
        if brim:cmd.extend(['--brim-width',str(brim),'--brim-type','outer_only'])
        started=time.monotonic();proc=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace')
        log=scrub(proc.stdout+'\n'+proc.stderr,root)
        (out/f'{pid}_slicer.log').write_text(log,encoding='utf-8')
        rec={'id':pid,'input_stl':part['stl'],'input_sha256':sha(stl),'exit_code':proc.returncode,'elapsed_seconds':round(time.monotonic()-started,2),'supports_enabled':supports,'supports_buildplate_only':True,'qa_brim_width_mm':brim,'output_exists':gcode.exists(),'log':f'{pid}_slicer.log','raw_flags':[]}
        rec['log_sha256']=sha(out/rec['log'])
        if proc.returncode:rec['raw_flags'].append('SLICER_NONZERO_EXIT')
        warning_lines=[l for l in log.splitlines() if not re.match(r'^\d+ => ',l) and re.search(r'(?i)warn|error|repair|empty layer|non.manifold|overhang|not fit|outside',l)]
        if warning_lines:
            rec['raw_warning_lines']=warning_lines
            rec['raw_flags'].append('SLICER_LOG_REVIEW')
        if gcode.exists():
            # Only metadata redaction, never G-code commands or geometry edits.
            source=gcode.read_text(encoding='utf-8',errors='replace');redacted=scrub(source,root)
            if source!=redacted:gcode.write_text(redacted,encoding='utf-8',newline='')
            rec['gcode_metadata_redacted']=source!=redacted;rec['gcode_sha256']=sha(gcode);rec['gcode']=gcode.name;rec['toolpath']=inspect_gcode(gcode)
            if rec['toolpath']['extruding_move_count']==0:rec['raw_flags'].append('NO_EXTRUSION')
            if rec['toolpath']['layer_count']==0:rec['raw_flags'].append('NO_LAYERS')
            if rec['toolpath']['private_absolute_path_found']:rec['raw_flags'].append('PRIVATE_PATH_IN_GCODE')
            bounds=rec['toolpath']['extrusion_bounds_mm']
            if bounds and (min(bounds[0][:2])<-0.001 or max(bounds[1][:2])>220.001):rec['raw_flags'].append('TOOLPATH_OUTSIDE_QA_BED')
        else:rec['raw_flags'].append('NO_GCODE')
        rec['slice_success']=proc.returncode==0 and gcode.exists() and rec.get('toolpath',{}).get('extruding_move_count',0)>0 and rec.get('toolpath',{}).get('layer_count',0)>0
        result['parts'].append(rec);save(out/'slicer_qa.json',result)
        print(pid,json.dumps({'slice_success':rec['slice_success'],'flags':rec['raw_flags'],'seconds':rec['elapsed_seconds']}),flush=True)
    result['all_parts_slice_success']=all(x['slice_success'] for x in result['parts'])
    result['limitations']=['Toolpaths use a generic single-material PLA QA profile, not the undecided four-toolhead configuration.','No machine start/end code; do not send these QA G-code files to a printer.','A successful slice does not prove support removal, surface quality, adhesion, strength, fit, or print success.','Buildplate-only support setting may leave enclosed overhangs unsupported; inspect geometry and overhang evidence.','Each trial remains separate, including all nonzero exits and warnings.']
    save(out/'slicer_qa.json',result)
if __name__=='__main__':main()
