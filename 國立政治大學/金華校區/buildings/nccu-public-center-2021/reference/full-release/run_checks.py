"""Full source-replay QA. Records all strict failures and exits nonzero on any failure."""
from pathlib import Path
import json,os,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parent
os.environ['PYTHONDONTWRITEBYTECODE']='1'
results=[]
MODE=['-B']+(['-O'] if sys.flags.optimize else [])
def run(name,args):
    p=subprocess.run(args,cwd=R);results.append({'gate':name,'returncode':p.returncode});return p.returncode
with tempfile.TemporaryDirectory(prefix='nccu-raw-qa-') as td:
    out=Path(td)/'results'
    run('original_geometry',[sys.executable,*MODE,str(R/'verification/run_qa.py'),'--stl',str(R/'model.stl'),'--out',str(out),'--expected-longest-mm','150'])
    # Keep reports and complete compressed evidence, never runtime logs or fixtures.
    for p in sorted(out.rglob('*')):
        if p.is_file() and (p.suffix=='.json' or p.name.endswith('.gz')):
            target=R/'qa'/p.relative_to(out);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
run('exact_original_intersections',[sys.executable,*MODE,str(R/'check_original_intersections.py'),'--stl',str(R/'model.stl'),'--out',str(R/'qa/intersections/original-intersections.json')])
with tempfile.TemporaryDirectory(prefix='nccu-intersection-controls-') as td:
    out=Path(td)
    run('intersection_controls',[sys.executable,*MODE,str(R/'check_intersection_controls.py'),'--out-dir',str(out)])
    for p in sorted(out.rglob('*')):
        if p.is_file() and (p.suffix=='.json' or p.name.endswith('.gz')):
            target=R/'qa/intersection-controls'/p.relative_to(out);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
for script in ['check_architectural_features.py','check_verification_gates.py','diagnose_boundaries.py','check_root_repairs.py']:
    run(script,[sys.executable,*MODE,str(R/script)])
run('saved_scene',['blender','-b',str(R/'scene.blend'),'-t','1','--python-exit-code','1','--python',str(R/'probe_scene.py')])
run('isolated_full_replay',[sys.executable,*MODE,str(R/'check_reproducibility.py'),'--render'])
run('fresh_artifact_scan',[sys.executable,*MODE,str(R/'check_artifacts.py')])
run('bind_current_payload',[sys.executable,*MODE,str(R/'write_validation_manifest.py')])
run('pre_control_integrity',[sys.executable,*MODE,str(R/'validate_model.py'),'--integrity-only'])
run('aggregate_negative_controls',[sys.executable,*MODE,str(R/'check_aggregate_controls.py')])
run('rebind_after_controls',[sys.executable,*MODE,str(R/'write_validation_manifest.py')])
run('final_aggregate',[sys.executable,*MODE,str(R/'validate_model.py')])
print(json.dumps({'all_commands_zero':all(q['returncode']==0 for q in results),'commands':results},indent=2))
raise SystemExit(0 if all(q['returncode']==0 for q in results) else 1)
