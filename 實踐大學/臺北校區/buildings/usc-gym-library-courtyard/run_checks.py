"""Re-run all current geometry gates and evidence bindings, without cached passes.
Use --render to also regenerate scene and all nine previews before aggregate validation.
"""
from pathlib import Path
import argparse,os,subprocess,sys,json,time,shutil
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');a=ap.parse_args()
env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
py=[sys.executable,'-B']+(['-'+'O'*sys.flags.optimize] if sys.flags.optimize else [])
commands=[
 [*py,'verification/run_qa.py','--stl','model.stl','--out','qa/current','--expected-longest-mm','200'],
 [*py,'run_exact_intersections.py'],
 [*py,'verification/check_intersection_controls.py','--out-dir','qa/current/intersection-controls'],
 [*py,'check_reproducibility.py'],[*py,'check_architectural_features.py']]
if a.render:commands.append(['blender','-b','-t','1','--python-exit-code','1','--python','render_preview.py'])
commands += [['blender','-b','scene.blend','-t','1','--python-exit-code','1','--python','probe_scene.py'],[*py,'check_compression_controls.py'],[*py,'validate_model.py'],[*py,'check_aggregate_controls.py'],[*py,'check_runner_controls.py']]
codes=[];rows=[];archive=R/'qa/rerun-history'/str(time.time_ns())
for cmd in commands:
 required=[]
 if cmd[0]=='blender':
  required=[R/('render-manifest.json' if 'render_preview.py' in cmd else 'scene-check.json')]
  for report in required:
   if report.exists():
    archive.mkdir(parents=True,exist_ok=True);shutil.move(str(report),str(archive/report.name))
 print('RUN',*cmd,flush=True);p=subprocess.run(cmd,cwd=R,env=env)
 fresh=all(report.is_file() for report in required);code=p.returncode if p.returncode else (0 if fresh else 1);codes.append(code)
 rows.append({'command':['python' if arg==sys.executable else arg for arg in cmd],'exit_code':p.returncode,'required_new_reports':[report.name for report in required],'new_reports_present':fresh,'passed':code==0})
(R/'pipeline-run.json').write_text(json.dumps({'passed':all(x==0 for x in codes),'python_optimization_level':sys.flags.optimize,'stages':rows},indent=2)+'\n')
raise SystemExit(0 if all(x==0 for x in codes) else 1)
