"""Build an explicit publication evidence copy; original private evidence is untouched.
No uploads or remote writes. Science reports and numeric data retain exact bytes.
"""
import argparse,hashlib,json,shutil
from pathlib import Path

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def require(v,m):
 if not v:raise RuntimeError(m)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--qa',type=Path,required=True);ap.add_argument('--postflight',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();qa=a.qa.resolve();out=a.out.resolve();require(not out.exists(),'Refuse existing public evidence output');out.mkdir(parents=True);rows=[];omitted=[];selected={}
 post=json.loads(a.postflight.read_text());require(post['bounded_verification_passed'] is True and post['original_numerical_strict_passed'] is False,'Postflight not accepted');controls=json.loads((qa/'final-controls-v17/final-control-summary.json').read_text());require(controls['passed'] is True,'Final tool controls failed')
 def add(src,dst=None):
  src=Path(src);relative=str(src.relative_to(qa));dst=dst or relative;require('..' not in Path(dst).parts and not Path(dst).is_absolute(),'Nonlocal public destination');require(src.is_file() and '__pycache__' not in src.parts,'Invalid copy source');require(dst not in selected or selected[dst]==src,'Public destination collision');selected[dst]=src
 def tree(prefix,dest=None,skip_logs=True):
  base=qa/prefix
  for p in sorted(base.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc':continue
   rel=p.relative_to(base)
   if skip_logs and (p.suffix=='.log' or p.name in ['stdout.txt','stderr.txt']):omitted.append({'source_relative_path':str(p.relative_to(qa)),'sha256':sha(p),'reason':'Routine execution log; complete structured results and replay tools retained. Private original unchanged.'});continue
   add(p,str(Path(dest or prefix)/rel))
 tree('resume-v17/geometry')
 add(qa/'resume-v17/referenced-completed-stages.json','results/recovery-provenance.json')
 tree('resume-v17/source-scene-reproduction','results/source-scene')
 add(qa/'resume-v17/saved-blend-rerenders/blend-rerender-audit.json','results/blend-rerender-audit.json')
 for name in ['render-manifest.json','metadata-cleanup-binding.json']:add(qa/'resume-v17/public-previews'/name,'preview-binding/'+name)
 tree('final-v17/frozen/verification','verification')
 tree('final-v17/frozen/independent-tools','independent-tools')
 for name in ['resume_independent_candidate.py','postflight_acceptance.py','run_final_tool_controls.py','assemble_public_evidence.py']:add(qa/'independent-tools'/name)
 tree('final-controls-v17','final-controls-v17')
 copylist=json.loads((qa/'predicate-review/PUBLIC_CONTROL_COPYLIST.json').read_text())
 for rel in copylist['required_files']:
  if rel in ['predicate-review/PUBLIC_CONTROL_COPYLIST.json','predicate-review/PUBLIC_CONTROL_README.md']:continue
  if rel.startswith(('predicate-review/png-final-normal/','predicate-review/png-final-optimized/')):continue
  p=qa/rel
  if p.suffix=='.log':omitted.append({'source_relative_path':rel,'sha256':sha(p),'reason':'Routine control stdout; per-case fixtures/results and replay script retained. Private original unchanged.'});continue
  add(p)
 for name in ['test_current_aggregate.py','test_exact_ray_diagnosis.py','test_original_hex_box.py']:add(qa/'audit'/name)
 add(qa/'predicate-review/review_png_compare_public.py')
 tree('audit/original-hex-box')
 tree('audit/generic-controls')
 tree('tooling-patched')
 # Compact explanations are derived from the twelve preserved exact ray proofs.
 for name in ['FLAGGED_RAY_EXPLANATIONS.md','FLAGGED_RAY_EXPLANATIONS.json']:
  p=qa/'predicate-review'/name
  if p.is_file():add(p,'results/'+name)
 # Each scientific artifact is copied verbatim. Reject private execution paths in
 # structured/text evidence rather than silently rewriting a scientific report.
 workspace=str(qa.parent).encode()
 for dest,src in sorted(selected.items()):
  digest=sha(src);target=out/dest;target.parent.mkdir(parents=True,exist_ok=True)
  if src.suffix in ['.json','.md','.py','.csv','.jsonl','.txt']:require(workspace not in src.read_bytes(),'Private absolute workspace path in selected artifact: '+str(src.relative_to(qa)))
  shutil.copyfile(src,target);require(sha(target)==digest and sha(src)==digest,'Copy/source integrity mismatch');rows.append({'source_relative_path':str(src.relative_to(qa)),'public_relative_path':dest,'bytes':target.stat().st_size,'sha256':digest,'transformation':'identity'})
 # Publication summaries are explicitly new derivatives, not edited producer JSON.
 public_result={k:v for k,v in post.items() if k not in ['evidence_inventory','optimization_level']};public_result['private_full_postflight_report_sha256']=sha(a.postflight);public_result['scope_of_this_file']='Public summary derived from the complete private postflight. Original scientific producer reports are included unchanged; this summary omits the private frozen-input inventory.'
 (out/'QA-RESULT.json').write_text(json.dumps(public_result,indent=2,allow_nan=False)+'\n')
 execution=json.loads((qa/'resume-v17/resumed-execution-summary.json').read_text());logical={'original_execution_summary_sha256':sha(qa/'resume-v17/resumed-execution-summary.json'),'completed':execution['completed'],'original_numerical_strict_passed':False,'stages':[{'name':r['name'],'returncode':r['returncode'],'elapsed_seconds':r['elapsed_seconds'],'private_log_sha256':r['log_sha256']} for r in execution['executions']],'recovery':'Normal raw and section stages completed before a transport interruption and were explicitly reused by their frozen hashes. Remaining normal stages and the complete optimized run executed in a fresh directory. The incomplete older run remains private; its process state could not be directly determined and its stagnant partial output was monitored throughout recovery.'}
 (out/'EXECUTION-METHOD.json').write_text(json.dumps(logical,indent=2,allow_nan=False)+'\n')
 (out/'PUBLICATION-BINDING.json').write_text(json.dumps({'purpose':'Exact-byte publication copies of final scientific evidence and final-version controls. No originals were modified. Routine stdout and historical incomplete/development runs stay private.','assembly_source_sha256':sha(__file__),'stl_sha256':post['stl_sha256'],'files':rows,'omitted_routine_logs':omitted,'public_previews':'Separate eleven cleaned PNGs, bound by preview-binding/render-manifest.json. Their raw originals and raw rerenders remain private; all removed fields and surviving-byte proofs are in the included render audit.'},indent=2,allow_nan=False)+'\n')
 for row in rows:require(sha(qa/row['source_relative_path'])==row['sha256'] and sha(out/row['public_relative_path'])==row['sha256'],'Final source/public copy recheck mismatch')
 files={str(p.relative_to(out)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(out.rglob('*')) if p.is_file()};(out/'FILES-SHA256.json').write_text(json.dumps(files,indent=2,allow_nan=False)+'\n');print(json.dumps({'files':len(files),'verbatim_evidence_files':len(rows),'omitted_routine_logs':len(omitted),'public_output_name':out.name}));return 0
if __name__=='__main__':raise SystemExit(main())
