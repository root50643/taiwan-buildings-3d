#!/usr/bin/env python3
"""Capture real full/exact producer exits. Caller owns the one shared flock; no lock here."""
import argparse, hashlib, json, math, os, pathlib, re, subprocess, sys, time
P=pathlib.Path
PYTHON=P(__file__).resolve().parents[2]/'modeling-toolchain/.venv/bin/python'
def require(ok,msg):
    if not ok: raise RuntimeError(msg)
def sha(p):
    with P(p).open('rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def inventory(qa):return {str(p.relative_to(qa)):sha(p) for d in ('tools','verification','render-tools') for p in sorted((qa/d).iterdir()) if p.suffix in ('.py','.cpp')}
def validate_contract(a):
    require(sys.executable==str(PYTHON) or P(sys.executable).resolve()==PYTHON.resolve(),'Use selected modeling-toolchain Python')
    require(type(a.expected_stl_sha256) is str and re.fullmatch('[0-9a-f]{64}',a.expected_stl_sha256),'Expected STL SHA256 required')
    require(type(a.expected_longest_mm) in (int,float) and math.isfinite(a.expected_longest_mm) and a.expected_longest_mm>0,'Finite positive expected extent required')
    require(type(a.revision) is str and re.fullmatch('v[0-9]+',a.revision),'Canonical vN revision required')
    require(sha(a.tooling_manifest)==a.expected_tooling_manifest_sha256,'Tooling manifest hash differs')
    source=json.loads(a.tooling_manifest.read_bytes());require(source.get('passed') is True and source.get('source_bytes_unchanged') is True,'Completed original tool reuse preflight required')
    expected={name:row['sha256'] for name,row in source['sources'].items()};require(len(expected)==28 and inventory(a.qa_root)==expected,'Exact tested 28-tool roster differs')
    require(sha(a.stl)==a.expected_stl_sha256,'STL hash differs')
    require(a.stl.name=='model.stl' and a.stl.parent.name==a.revision and a.stl.parent.parent.name=='models','Capture must target exact models/vN/model.stl')
    return expected
BOOT='''import sys,os,json,runpy,hashlib,pathlib
p=pathlib.Path(sys.argv[1]);target=pathlib.Path(sys.argv[2]);args=sys.argv[3:]
p.write_text(json.dumps({'optimization_level':sys.flags.optimize,'cpu_affinity':sorted(os.sched_getaffinity(0)),'python_executable':sys.executable,'target':str(target),'target_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'target_arguments':args},indent=2)+'\\n')
sys.path.insert(0,str(target.parent));sys.argv=[str(target),*args]
runpy.run_path(str(target),run_name='__main__')
'''
def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--kind',choices=['full','exact'],required=True);ap.add_argument('--mode',choices=['normal','optimized'],required=True)
    ap.add_argument('--stl',type=P,required=True);ap.add_argument('--out',type=P,required=True);ap.add_argument('--capture',type=P,required=True)
    ap.add_argument('--full',type=P,help='Completed full-QA root, required only for exact')
    ap.add_argument('--qa-root',type=P,required=True);ap.add_argument('--revision',required=True);ap.add_argument('--expected-stl-sha256',required=True);ap.add_argument('--expected-longest-mm',type=float,required=True)
    ap.add_argument('--tooling-manifest',type=P,required=True);ap.add_argument('--expected-tooling-manifest-sha256',required=True)
    a=ap.parse_args(argv);a.stl=a.stl.resolve();a.out=a.out.resolve();a.capture=a.capture.resolve();a.qa_root=a.qa_root.resolve();a.tooling_manifest=a.tooling_manifest.resolve();QA=a.qa_root;SHA=a.expected_stl_sha256
    require(not a.capture.exists() and not a.out.exists(),'Capture and producer output must both be NEW')
    require(len(os.sched_getaffinity(0))==1,'Caller must apply taskset to one allowed CPU')
    tested=validate_contract(a)
    require(a.out!=a.capture and a.out not in a.capture.parents and a.capture not in a.out.parents,'Capture/output must be separate trees')
    opt=0 if a.mode=='normal' else 1
    if a.kind=='full':
        require(opt==0 and a.full is None,'Full wrapper must start normal and itself runs BOTH modes')
        target=QA/'tools/run_full_qa.py';args=['--stl',str(a.stl),'--expected-sha256',SHA,'--expected-longest-mm',str(a.expected_longest_mm),'--out',str(a.out)];report=a.out/'full-qa-summary.json'
    else:
        require(a.full is not None,'Exact requires completed --full root');a.full=a.full.resolve();base=a.full/a.mode;std=base/'standard';dense=std/'dense/dense-check.json'
        target=QA/'tools/diagnose_recorded_cpp_rays.py';args=['--stl',str(a.stl),'--expected-sha256',SHA,'--flags',str(std/'dense/dense-flagged-samples.json.gz'),'--dense-report',str(dense),'--raw-report',str(std/'raw/raw-mesh-check.json'),'--intersections-report',str(base/'intersections.json'),'--out',str(a.out)];report=a.out/'exact-recorded-ray-summary.json'
        for path in (std/'raw/raw-mesh-check.json',base/'intersections.json'):
            r=json.loads(path.read_text());require(r.get('passed') is True and r.get('strict_passed') is True and r.get('stl_sha256')==SHA,'Exact prerequisite failed: '+str(path))
        r=json.loads(dense.read_text());require(r.get('strict_passed') is False and type(r.get('under_0p8mm_count')) is int and r['under_0p8mm_count']==0 and type(r.get('flagged_sample_count')) is int and r['flagged_sample_count']>0,'Exact route requires zero short rays and positive original flags')
    before=inventory(QA);a.capture.mkdir(parents=True);bootstrap=a.capture/'runtime_launcher.py';bootstrap.write_text(BOOT);runtime=a.capture/'runtime.json'
    env=os.environ.copy();env.pop('PYTHONOPTIMIZE',None)
    for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[k]='1'
    env['PYTHONDONTWRITEBYTECODE']='1';command=[str(PYTHON),'-B',*(['-O'] if opt else []),str(bootstrap),str(runtime),str(target),*args]
    rec={'schema':'original-stl-producer-capture-v1','revision':a.revision,'expected_longest_mm':a.expected_longest_mm,'tooling_manifest_sha256':sha(a.tooling_manifest),'kind':a.kind,'mode':a.mode,'stl_path':str(a.stl),'stl_sha256':SHA,'producer_output':str(a.out),'full_root':str(a.full) if a.full else None,'command':command,'target_arguments':args,'target':str(target),'target_sha256':sha(target),'capture_source_sha256':sha(__file__),'bootstrap_sha256':sha(bootstrap),'tool_sources_before':before,'started_unix':time.time(),'caller_lock_policy':'External exclusive qa/.heavy.lock; capture does not acquire it','cpu_affinity':sorted(os.sched_getaffinity(0)),'completed':False}
    write(a.capture/'execution-progress.json',rec)
    try:
        with (a.capture/'stdout.txt').open('wb') as out,(a.capture/'stderr.txt').open('wb') as err:code=subprocess.run(command,stdout=out,stderr=err,env=env).returncode
        rec['returncode']=code;rr=json.loads(runtime.read_text());require(type(rr['optimization_level']) is int and rr['optimization_level']==opt,'Actual optimization mode mismatch');require(rr['cpu_affinity']==rec['cpu_affinity'] and len(rr['cpu_affinity'])==1,'Runtime CPU binding differs');require(rr['target_sha256']==rec['target_sha256'] and rr['target_arguments']==args,'Runtime producer binding differs')
        rec['runtime']=rr;rec['runtime_sha256']=sha(runtime);rec['tool_sources_after']=inventory(QA);require(rec['tool_sources_after']==before==tested and sha(a.stl)==SHA and sha(a.tooling_manifest)==a.expected_tooling_manifest_sha256,'Original sources/STL changed during producer');require(report.is_file(),'Producer summary missing')
        rec['report_path']=str(report);rec['report_sha256']=sha(report);rec['completed']=True
    except Exception as e:rec.update(error_type=type(e).__name__,error=str(e))
    rec['finished_unix']=time.time();rec['stdout_sha256']=sha(a.capture/'stdout.txt');rec['stderr_sha256']=sha(a.capture/'stderr.txt');write(a.capture/'execution.json',rec)
    print(json.dumps({'capture':str(a.capture/'execution.json'),'completed':rec['completed'],'producer_returncode':rec.get('returncode')}),flush=True)
    return rec.get('returncode',2) if rec['completed'] else 2
if __name__=='__main__':raise SystemExit(main())
