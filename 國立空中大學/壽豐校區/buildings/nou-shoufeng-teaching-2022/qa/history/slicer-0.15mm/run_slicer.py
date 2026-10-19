"""Reproduce isolated, full-scale candidate QA slices; G-code is NOT machine-ready.

Example: python run_slicer.py --slicer /path/to/prusa-slicer-console.exe \
  --base-config /path/to/qa-base.ini --work /path/to/isolated-work
Only XY centering is applied. Each STL retains its supplied orientation and scale.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, re, shutil, subprocess, sys

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--slicer', type=Path, required=True)
    p.add_argument('--base-config', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--part', action='append', help='Update only named part(s); verify and retain unchanged previous slices.')
    a = p.parse_args()
    root, work = a.root.resolve(), a.work.resolve()
    qa = root / 'qa'; out = qa / 'slicer'; out.mkdir(parents=True, exist_ok=True)
    staging = work / 'slicer-staging'; staging.mkdir(parents=True, exist_ok=True)
    datadir = work / 'slicer-tools' / 'nou-data'; datadir.mkdir(parents=True, exist_ok=True)
    params = json.loads((root / 'parameters.json').read_text(encoding='utf-8'))
    config = dict(line.split(' = ', 1) for line in a.base_config.read_text(encoding='utf-8').splitlines()
                  if ' = ' in line and not line.startswith('#'))
    changes = {
        'layer_height':'0.15','first_layer_height':'0.15','nozzle_diameter':'0.4',
        'perimeters':'3','fill_density':'100%','fill_pattern':'rectilinear',
        'top_solid_layers':'4','bottom_solid_layers':'4','brim_width':'3',
        'support_material':'0','support_material_auto':'0','raft_layers':'0',
        'skirts':'0','gcode_comments':'1','binary_gcode':'0','temperature':'0',
        'first_layer_temperature':'0','bed_temperature':'0','first_layer_bed_temperature':'0',
        'autoemit_temperature_commands':'0',
        'start_gcode':'; QA ONLY - NOT MACHINE READY - no machine startup supplied',
        'end_gcode':'; QA ONLY - no machine shutdown supplied',
        'start_filament_gcode':'','end_filament_gcode':'',
        'notes':'QA ONLY; uncalibrated generic profile; never send directly to a printer',
    }
    for key in config:
        if key.endswith('extrusion_width'):
            changes[key] = '0.45'
    config.update(changes)
    config_path = out / 'qa-0p15mm.ini'
    config_path.write_text('# Isolated PrusaSlicer candidate QA; NOT MACHINE READY\n' +
                           '\n'.join(f'{k} = {v}' for k,v in sorted(config.items()))+'\n', encoding='utf-8')
    stage_config = staging / 'qa-0p15mm.ini'; shutil.copyfile(config_path, stage_config)
    record = {
        'schema':1,'purpose':'Manufacturability QA only; G-code is NOT machine-ready',
        'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'slicer_executable':str(a.slicer.resolve()), 'slicer_executable_sha256':sha(a.slicer),
        'base_config_sha256':sha(a.base_config),'qa_config_sha256':sha(config_path),
        'settings':changes,'bed_mm':[220,220],
        'orientation_policy':'Each of nine original STL print orientations, scale=100%; XY center only.',
        'temperature_and_machine_limitations':'Temperatures zero; no startup/shutdown or machine calibration. QA only.',
        'parameters_sha256':sha(root/'parameters.json'),'runs':[],
        'physical_validation':'No test print, support removal, or physical fit test has been performed.'}
    if a.part:
        old=json.loads((qa/'slicer-run-record.json').read_text(encoding='utf-8'))
        selected=set(a.part)
        names={v['name'] for v in params['parts']}
        if not selected <= names: raise RuntimeError('Unknown selected part')
        record['previous_parameters_sha256']=old['parameters_sha256']
        record['runs']=[v for v in old['runs'] if v['part'] not in selected]
        for run in record['runs']:
            part=next(v for v in params['parts'] if v['name']==run['part'])
            if sha(root/'models'/part['stl'])!=run['input_stl_sha256'] or part['sha256']!=run['input_stl_sha256']:
                raise RuntimeError('Unselected part changed: '+part['name'])
            if sha(qa/run['gcode'])!=run['gcode_sha256']: raise RuntimeError('Retained G-code changed')
        if old['qa_config_sha256']!=record['qa_config_sha256']: raise RuntimeError('Configuration changed; re-slice all parts')
        record['revision_note']='Only selected changed part(s) re-sliced; other inputs and G-code checksums verified unchanged.'
    else:selected={v['name'] for v in params['parts']}
    for part in params['parts']:
        if part['name'] not in selected: continue
        source = root/'models'/part['stl']; name = part['name']; staged = staging/(name+'.stl')
        before = sha(source)
        if before != part['sha256']:
            raise RuntimeError('STL checksum differs from parameters: '+name)
        shutil.copyfile(source, staged)
        staged_gcode = staging/(name+'.gcode')
        cmd = [str(a.slicer.resolve()),'--datadir',str(datadir),'--load',str(stage_config),
               '--threads','2','--loglevel','2','--scale','100%','--center','110,110',
               '--info','--export-gcode','--output',str(staged_gcode),str(staged)]
        started = datetime.datetime.now(datetime.timezone.utc)
        result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                encoding='utf-8', errors='replace')
        log_path = out/(name+'.log'); log_path.write_text(result.stdout, encoding='utf-8')
        final_gcode = out/(name+'.gcode')
        if staged_gcode.exists(): shutil.copyfile(staged_gcode,final_gcode)
        item = {'part':name,'input_stl_sha256':before,'stl_unchanged_after_slice':sha(source)==before,
                'command':cmd,'exit_code':result.returncode,
                'elapsed_seconds':(datetime.datetime.now(datetime.timezone.utc)-started).total_seconds(),
                'log':'slicer/'+log_path.name,'log_sha256':sha(log_path),
                'warnings':[s for s in result.stdout.splitlines() if re.search(r'warn|error|repair|non.manifold|failed',s,re.I)],
                'model_info':{m.group(1):m.group(2) for m in re.finditer(r'^([a-zA-Z0-9_]+)\s*=\s*(.*)$',result.stdout,re.M)},
                'gcode':'slicer/'+final_gcode.name if final_gcode.exists() else None,
                'gcode_sha256':sha(final_gcode) if final_gcode.exists() else None,
                'gcode_bytes':final_gcode.stat().st_size if final_gcode.exists() else 0,
                'source_print_bounds_mm':part['print_bounds_mm']}
        record['runs'].append(item)
        record['runs'].sort(key=lambda v:v['part'])
        (qa/'slicer-run-record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
        print(json.dumps({'part':name,'exit_code':result.returncode,'warnings':item['warnings'],
                          'gcode_bytes':item['gcode_bytes']}), flush=True)
    record['parameters_unchanged_after_slicing'] = sha(root/'parameters.json')==record['parameters_sha256']
    record['all_nine_exported'] = len(record['runs'])==9 and all(r['exit_code']==0 and r['gcode_bytes']>0 for r in record['runs'])
    (qa/'slicer-run-record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    return 0 if record['all_nine_exported'] else 1

if __name__=='__main__':
    sys.exit(main())
