"""Mock only subprocess orchestration to test stale Blender-report rejection.
These controls do not claim that any model geometry or real Blender render passed.
"""
from pathlib import Path
import json,hashlib,runpy,shutil,subprocess,sys,tempfile
from unittest.mock import patch
R=Path(__file__).resolve().parent
rows=[]
for mode,render in [(m,r) for m in ['fresh_success','blender_exception','missing_fresh_report'] for r in [False,True]]:
 with tempfile.TemporaryDirectory(prefix='usc-runner-control-') as td:
  root=Path(td);shutil.copy2(R/'run_checks.py',root/'run_checks.py');(root/'scene-check.json').write_text('{"old":true}');(root/'render-manifest.json').write_text('{"old":true}')
  calls=[]
  def fake(cmd,**kwargs):
   calls.append(cmd)
   if cmd[0]=='blender':
    if mode=='blender_exception':return subprocess.CompletedProcess(cmd,1)
    if mode=='fresh_success':(root/('render-manifest.json' if 'render_preview.py' in cmd else 'scene-check.json')).write_text('{"new":true}')
   return subprocess.CompletedProcess(cmd,0)
  with patch.object(sys,'argv',['run_checks.py']+(['--render'] if render else [])),patch.object(subprocess,'run',side_effect=fake):
   try:runpy.run_path(str(root/'run_checks.py'),run_name='__main__');code=0
   except SystemExit as e:code=e.code
  q=json.loads((root/'pipeline-run.json').read_text());blender=[x for x in calls if x[0]=='blender'];expected=mode=='fresh_success'
  good=(code==0)==expected and q['passed'] is expected and bool(blender) and all('--python-exit-code' in x and x[x.index('--python-exit-code')+1]=='1' for x in blender) and len(list((root/'qa/rerun-history').rglob('scene-check.json')))==1
  rows.append({'case':mode,'with_render':render,'expected_passed':expected,'observed_passed':q['passed'],'exit_code':code,'control_passed':good})
q={'passed':all(x['control_passed'] for x in rows),'python_optimization_level':sys.flags.optimize,'controls':rows,'runner_source_sha256':hashlib.sha256((R/'run_checks.py').read_bytes()).hexdigest(),'control_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Mock subprocess orchestration only; independent geometry/render evidence is separate.'}
(R/'runner-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));raise SystemExit(0 if q['passed'] else 1)
