"""Slice four unique print STLs; keep executable G-code outside the package.

Set PRUSA_SLICER to a PrusaSlicer 2.9.6 console executable, and PRIVATE_SLICE_DIR
to a writable directory outside this model package. No user preset is modified.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,os,re,subprocess,math,sys
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def parse_gcode(path):
    role='unspecified';xyz=np.zeros(3);e=0.;layers=0;roles={};times=[];object_z=set()
    for line in path.read_text(encoding='utf8',errors='replace').splitlines():
        if line.startswith(';LAYER_CHANGE'):layers+=1
        if line.startswith(';TYPE:'):role=line.split(':',1)[1].strip()
        if line.startswith('; estimated printing time'):times.append(line.lstrip('; '))
        code=line.split(';',1)[0].strip()
        if not code:continue
        cmd=code.split()[0]
        vals={k:float(v) for k,v in re.findall(r'([XYZE])(-?(?:\d+(?:\.\d*)?|\.\d+))',code)}
        if cmd=='G92':
            if 'E' in vals:e=vals['E']
            continue
        if cmd not in ('G0','G1'):continue
        new=xyz.copy()
        for i,k in enumerate('XYZ'):
            if k in vals:new[i]=vals[k]
        en=vals.get('E',e);de=en-e;length=float(np.linalg.norm(new[:2]-xyz[:2]))
        if de>1e-7 and length>1e-7:
            if not role.startswith('Support') and role not in ('Skirt/Brim','unspecified'):
                object_z.add(round(float(new[2]),5))
            r=roles.setdefault(role,{'extruding_xy_moves':0,'filament_mm_in_xy_moves':0.,'xy_path_mm':0.,'bounds_min_xyz':new.tolist(),'bounds_max_xyz':new.tolist()})
            r['extruding_xy_moves']+=1;r['filament_mm_in_xy_moves']+=de;r['xy_path_mm']+=length
            r['bounds_min_xyz']=np.minimum(r['bounds_min_xyz'],np.minimum(xyz,new)).tolist()
            r['bounds_max_xyz']=np.maximum(r['bounds_max_xyz'],np.maximum(xyz,new)).tolist()
        xyz=new;e=en
    return {'toolpath_layer_change_records':layers,'object_extrusion_z_count':len(object_z),'object_max_extrusion_z_mm':max(object_z) if object_z else None,'feature_extrusions':roles,'estimated_time_comments':times,
            'measurement_note':'Positive absolute-E extrusion on nonzero XY segments only; retraction-only and unretraction-only moves excluded. This is diagnostic path evidence, not a physical print.'}

def main():
    exe=Path(os.environ['PRUSA_SLICER']).resolve();private=Path(os.environ['PRIVATE_SLICE_DIR']).resolve()
    if private==ROOT or ROOT in private.parents:raise RuntimeError('Keep G-code outside the deliverable package')
    private.mkdir(parents=True,exist_ok=True)
    asm=json.loads((ROOT/'assembly.json').read_text(encoding='utf8'))
    def run(item):
        n=item['part'];support=n=='main_body';profile='diagnostic-main-support.ini' if support else 'diagnostic-no-support.ini'
        out=private/(n+'-DIAGNOSTIC-ONLY.gcode');datadir=private/(n+'-isolated-datadir');datadir.mkdir(exist_ok=True)
        args=[str(exe),'--datadir',str(datadir),'--load',str(HERE/profile),'--center','125,105','--export-gcode','--output',str(out),str(ROOT/'parts'/(n+'-print.stl'))]
        r=subprocess.run(args,text=True,encoding='utf8',errors='replace',capture_output=True,cwd=ROOT)
        raw=r.stdout+'\n'+r.stderr
        # Preserve complete diagnostics while removing private machine paths.
        clean=raw.replace(str(exe.parent),'${SLICER_DIR}').replace(str(private),'${PRIVATE_SLICE_DIR}').replace(str(ROOT),'${MODEL_PACKAGE}')
        (HERE/(n+'-slice.log')).write_text(clean,encoding='utf8')
        result={'part':n,'quantity':item['quantity'],'exit_code':r.returncode,'support_enabled':support,
          'profile':profile,'command_template':['${PRUSA_SLICER}','--datadir','${PRIVATE_SLICE_DIR}/'+datadir.name,'--load','qa/manufacturing-review/'+profile,'--center','125,105','--export-gcode','--output','${PRIVATE_SLICE_DIR}/'+out.name,'parts/'+n+'-print.stl'],
          'input_sha256':hashlib.sha256((ROOT/'parts'/(n+'-print.stl')).read_bytes()).hexdigest(),
          'warning_lines':[s for s in clean.splitlines() if re.search('warn|error|repair',s,re.I)],
          'raw_gcode_in_deliverable':False}
        if out.exists():
            result['gcode_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();result['gcode_bytes']=out.stat().st_size;result.update(parse_gcode(out))
        if r.returncode:raise RuntimeError(json.dumps(result))
        return result
    with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(run,asm['inventory']))
    summary={'slicer_version':'PrusaSlicer 2.9.6','gcode_is_machine_ready':False,'physical_print_or_fit_test':False,
      'conditions':{'nozzle_mm':.4,'layer_mm':.2,'extrusion_width_mm':.45,'perimeters':3,'infill_percent':15,'material':'generic PLA diagnostic assumption','nominal_nozzle_temperature_C':205,'bed_C':60,'bed_mm':[250,210],'center_mm':[125,105]},
      'data_policy':'Separate datadir per unique piece; full diagnostic G-code retained only outside the deliverable. Logs, explicit profiles, hashes and path summaries are in the package.',
      'results':results}
    (HERE/'slicing-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
    print(json.dumps([{k:r[k] for k in ['part','exit_code','toolpath_layer_change_records','object_extrusion_z_count','support_enabled','warning_lines','gcode_sha256']} for r in results],indent=2))

if __name__=='__main__':main()
