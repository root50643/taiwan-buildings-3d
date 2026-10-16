"""Replay final-version small controls only, binding exact sources and inputs."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def require(x,m):
 if not x:raise RuntimeError(m)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--qa',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();qa=a.qa.resolve();out=a.out.resolve();require(not out.exists(),'Refuse existing control output');out.mkdir(parents=True)
 env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',BWBC_VERIFICATION_DIR=str(qa/'final-v17/frozen/verification'));env.pop('PYTHONOPTIMIZE',None)
 report={'passed':False,'executions':[],'purpose':'Final-version synthetic predicate/original-hex controls and aggregate packaging controls. Positive-fixture report injection tests packaging only; it does not re-claim geometry.','source_sha256':sha(__file__)}
 try:
  inventory=json.loads((qa/'final-v17/independent-tool-inventory.json').read_text());inputs={}
  for name,digest in inventory.items():require(sha(qa/'independent-tools'/name)==digest,'Current helper differs from frozen helper');inputs['independent-tools/'+name]=digest
  for p in (qa/'final-v17/frozen/verification').glob('*'):
   if p.is_file():inputs[str(p.relative_to(qa))]=sha(p)
  for name in ['test_current_aggregate.py','test_exact_ray_diagnosis.py','test_original_hex_box.py']:inputs['audit/'+name]=sha(qa/'audit'/name)
  for name in ['review_png_compare_public.py','png_fixture_helpers.py']:inputs['predicate-review/'+name]=sha(qa/'predicate-review'/name)
  for prefix in ['audit/generic-controls','audit/original-hex-box']:
   for p in (qa/prefix).rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts:inputs[str(p.relative_to(qa))]=sha(p)
  for mode,opts in [('normal',[]),('optimized',['-O'])]:
   for name,script,args,filename,count in [('aggregate','test_current_aggregate.py',['--out',out/('aggregate-'+mode)],'unit-test-summary.json',21),('exact-predicates','test_exact_ray_diagnosis.py',[out/('exact-predicates-'+mode+'.json')],None,373),('original-hex','test_original_hex_box.py',[out/('original-hex-'+mode+'.json')],None,120)]:
    cmd=[sys.executable,'-B',*opts,qa/'audit'/script,*args];cmd=list(map(str,cmd));log=out/(name+'-'+mode+'.log')
    with log.open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
    path=out/('aggregate-'+mode)/filename if filename else out/(name+'-'+mode+'.json');require(r.returncode==0 and path.is_file(),'Control subprocess failed: '+name+'/'+mode);d=json.loads(path.read_text());require(d['passed'] is True and d['optimization_level']==(0 if mode=='normal' else 1),'Control success/mode differs');require(d.get('case_count',d.get('original_ray_count'))==count,'Control count differs')
    row={'control':name,'mode':mode,'returncode':r.returncode,'report_file':str(path.relative_to(out)),'report_sha256':sha(path),'log_file':log.name,'log_sha256':sha(log),'script':str((qa/'audit'/script).relative_to(qa)),'script_sha256':inputs['audit/'+script],'cases':count};report['executions'].append(row);print(json.dumps(row),flush=True)
  for mode,opts in [('normal',[]),('optimized',['-O'])]:
   script=qa/'predicate-review/review_png_compare_public.py';dest=out/('png-compare-'+mode);log=out/('png-compare-'+mode+'.log');cmd=[sys.executable,'-B',*opts,str(script),'--module',str(qa/'final-v17/frozen/independent-tools/png_exact_compare.py'),'--out',str(dest)]
   with log.open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
   require(r.returncode==0,'Public PNG comparator controls failed');p=dest/'results.json';d=json.loads(p.read_text());priorpath=qa/'predicate-review'/('png-final-'+mode)/'results.json';inputs[str(priorpath.relative_to(qa))]=sha(priorpath);prior=json.loads(priorpath.read_text());require(d['case_count']==d['passed_count']==242 and d['failed']==[] and d['optimized']==(mode=='optimized') and d['module_sha256']==inventory['png_exact_compare.py'],'PNG control report identity/count');require(d['cases']==prior['cases'],'Scientific PNG cases differ from prior final review')
   report['executions'].append({'control':'png-comparator-pathless-report','mode':mode,'returncode':0,'report_file':str(p.relative_to(out)),'report_sha256':sha(p),'log_file':log.name,'log_sha256':sha(log),'script':'predicate-review/review_png_compare_public.py','script_sha256':inputs['predicate-review/review_png_compare_public.py'],'cases':242,'scientific_cases_identical_to_prior_review':True,'prior_private_report_sha256':inputs[str(priorpath.relative_to(qa))]});print(json.dumps({'stage':'png-comparator-pathless-report','mode':mode,'passed':True}),flush=True)
  require(all(sha(qa/name)==digest for name,digest in inputs.items()),'Control input/source changed');require(sha(__file__)==report['source_sha256'],'Control runner changed');report.update(passed=True,source_and_input_sha256=inputs,total_control_cases=sum(r['cases'] for r in report['executions']))
 except Exception as e:report.update(passed=False,error_type=type(e).__name__,error=str(e))
 (out/'final-control-summary.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
