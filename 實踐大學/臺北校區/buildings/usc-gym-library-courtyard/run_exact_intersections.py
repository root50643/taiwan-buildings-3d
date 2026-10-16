"""Invoke the unmodified exact-contact checker with detached source provenance."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=R/'verification/check_original_intersections.py';stl=R/'model.stl';out=R/'qa/current/intersections/original-intersections.json'
before={'checker':sha(source),'stl':sha(stl)}
mode=['-B']+(['-'+'O'*sys.flags.optimize] if sys.flags.optimize else [])
args=[sys.executable,*mode,'verification/check_original_intersections.py','--stl','model.stl','--out','qa/current/intersections/original-intersections.json','--expected-sha256',before['stl']]
proc=subprocess.run(args,cwd=R,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1'))
after={'checker':sha(source),'stl':sha(stl)}
q=json.loads(out.read_text()) if out.is_file() else {}
report={'python_optimization_level':sys.flags.optimize,'passed':proc.returncode==0 and q.get('passed') is True and before==after,'exit_code':proc.returncode,'stl_sha256':before['stl'],'checker_source_sha256':before['checker'],'wrapper_source_sha256':sha(__file__),'sources_unchanged_during_run':before==after,'report_sha256':sha(out) if out.is_file() else None,'command':['python']+args[1:]}
(R/'exact-invocation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)
