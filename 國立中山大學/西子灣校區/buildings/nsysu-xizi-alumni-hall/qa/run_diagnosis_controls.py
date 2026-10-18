"""Synthetic controls for the local exact rational flag diagnosis."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import trimesh
from flag_diagnosis import exact_controls

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--json',type=Path,required=True)
args=parser.parse_args()
report=exact_controls()
report['diagnostic_script_sha256']=hashlib.sha256((Path(__file__).resolve().parent/'flag_diagnosis.py').read_bytes()).hexdigest()
args.json.parent.mkdir(parents=True,exist_ok=True)
artifacts=args.json.parent/'guard-controls'
artifacts.mkdir(exist_ok=True)
script=Path(__file__).resolve().parent/'flag_diagnosis.py'
base=trimesh.Trimesh(vertices=[(0,0,0),(2,0,0),(0,2,0),(0,0,2)],faces=[(0,1,2),(0,1,3)],process=False)
base_path=artifacts/'shared_edge.stl'
base_path.write_bytes(trimesh.exchange.stl.export_stl(base))
digest=hashlib.sha256(base_path.read_bytes()).hexdigest()
degenerate=trimesh.Trimesh(vertices=[(0,0,0),(2,0,0),(0,2,0),(1,0,0)],faces=[(0,1,2),(0,1,3)],process=False)
deg_path=artifacts/'degenerate.stl'
deg_path.write_bytes(trimesh.exchange.stl.export_stl(degenerate))
crossing=trimesh.Trimesh(vertices=[(0,0,0),(2,0,0),(0,2,0),(0.5,0.5,-1),(0.5,0.5,1),(1.5,0.5,0)],faces=[(0,1,2),(3,4,5)],process=False)
cross_path=artifacts/'crossing.stl'
cross_path.write_bytes(trimesh.exchange.stl.export_stl(crossing))
cases={
 'valid_shared_edge':(base_path,digest,[{'faces':[0,1]}],0),
 'wrong_input_hash':(base_path,'0'*64,[{'faces':[0,1]}],1),
 'empty_flag_list':(base_path,digest,[],1),
 'duplicate_reversed_pair':(base_path,digest,[{'faces':[0,1]},{'faces':[1,0]}],1),
 'out_of_range_face':(base_path,digest,[{'faces':[0,2]}],1),
 'degenerate_mesh':(deg_path,hashlib.sha256(deg_path.read_bytes()).hexdigest(),[{'faces':[0,1]}],1),
 'unexpected_exact_crossing':(cross_path,hashlib.sha256(cross_path.read_bytes()).hexdigest(),[{'faces':[0,1]}],1),
}
report['cli_guard_controls']={}
for name,(mesh_path,sha,flags,status) in cases.items():
    source_path=artifacts/f'{name}.input.json'
    output_path=artifacts/f'{name}.result.json'
    source_path.write_text(json.dumps({'sha256':sha,'self_intersections':{'unexpected_contacts_or_intersections':flags}},indent=2),encoding='utf-8')
    run=subprocess.run([sys.executable,str(script),str(mesh_path),str(source_path),'--json',str(output_path)],capture_output=True,text=True,encoding='utf-8')
    result=json.loads(output_path.read_text(encoding='utf-8')) if output_path.exists() else {}
    report['cli_guard_controls'][name]={'expected_exit_status':status,'actual_exit_status':run.returncode,
        'expectation_passed':run.returncode==status,'guard_errors':result.get('guard_errors'),
        'passes_flag_diagnosis':result.get('passes_flag_diagnosis'),'stderr':run.stderr,
        'result_file':output_path.relative_to(args.json.parent).as_posix()}
report['all_control_expectations_passed']=bool(report['all_control_expectations_passed'] and all(r['expectation_passed'] for r in report['cli_guard_controls'].values()))
args.json.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'all_control_expectations_passed':report['all_control_expectations_passed'],
                  'cases':{k:v['expectation_passed'] for k,v in report['controls'].items()},
                  'cli_guard_cases':report['cli_guard_controls']},indent=2))
raise SystemExit(0 if report['all_control_expectations_passed'] else 1)
