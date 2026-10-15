#!/usr/bin/env python3
"""Recompute model and all author evidence in a writable copy of this package.
Strict morphology and exact-boundary overlap are preserved false diagnostics.
Only the separately bounded complete evidence can pass the qualified gate.
"""
from pathlib import Path
import argparse,json,subprocess,sys,shutil
HERE=Path(__file__).resolve().parent

def main():
 a=argparse.ArgumentParser();a.add_argument('--blender',default='blender');x=a.parse_args();py=sys.executable;commands=[]
 def run(args,expected=0):
  cmd=[str(v) for v in args];r=subprocess.run(cmd,cwd=HERE);commands.append({'command':cmd,'exit_code':r.returncode,'expected_exit_code':expected,'expected_result':r.returncode==expected})
  if r.returncode!=expected:raise RuntimeError(f'Unexpected gate result: {cmd[1:]}')
 try:
  run([py,'build.py']);run([py,'qa.py'],expected=1)
  s=json.loads((HERE/'output/qa-sections.json').read_text())
  if s['passed'] or s['section_failures'] or s['split_or_vanished'] or not s['component_failures']:raise RuntimeError('Strict result is not solely the retained opening-loss diagnostic')
  run([py,'check_curvature.py']);run([py,'check_qa_regression.py'])
  run([py,'check_root_supports.py']);run([py,'check_root_clearance.py'])
  run([py,'check_root_loss_polygons.py','--stl','output/model.stl'],expected=1)
  run([py,'check_root_section_connections.py']);run([py,'check_root_complete_loss_linkage.py']);run([py,'check_root_controls.py'])
  run([py,'check_dense_tests.py']);run([py,'check_dense_surface.py','--out','dense_evidence','--stl','output/model.stl','--threads','2'])
  run([py,'check_dense_minimum_winding.py','--out','dense_evidence','--stl','output/model.stl'])
  run([py,'dense_transcode_events.py','--out','dense_evidence'])
  for out in ['output','reproduction']:
   if out=='reproduction':run([py,'build.py','--out',out])
   run([x.blender,'-b','-t','1','--python-exit-code','1','--python','render.py','--',out])
   run([x.blender,'-b','-t','1','--python-exit-code','1','--python','audit_blend.py','--',out])
   run([x.blender,'-b','-t','1','--python-exit-code','1','--python','audit_scene_privacy.py','--',out])
  run([py,'check_reproduction.py']);run([py,'check_qualified_evidence.py'])
  result={'author_reproduction_passed':True,'independent_review_implied':False,'strict_morphology_passed':False,'commands':commands}
 except Exception as e:
  result={'author_reproduction_passed':False,'independent_review_implied':False,'failure':str(e),'commands':commands}
 (HERE/'output/reproduction-run.json').write_text(json.dumps(result,indent=2)+'\n');return result['author_reproduction_passed']
if __name__=='__main__':raise SystemExit(0 if main() else 1)
