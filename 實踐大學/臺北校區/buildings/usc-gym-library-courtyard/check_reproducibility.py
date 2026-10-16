"""Rebuild the source geometry in an isolated directory and compare exact bytes."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='usc-rebuild-') as td:
 env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
 mode=['-B']+(['-'+'O'*sys.flags.optimize] if sys.flags.optimize else [])
 proc=subprocess.run([sys.executable,*mode,str(R/'build_model.py'),'--output-dir',td],env=env,capture_output=True,text=True)
 q=Path(td)/'model.stl';same=proc.returncode==0 and q.exists() and q.read_bytes()==(R/'model.stl').read_bytes()
 report={'passed':same,'python_optimization_level':sys.flags.optimize,'child_python_flags':mode,'build_exit_code':proc.returncode,'stl_sha256':sha(R/'model.stl'),'rebuilt_stl_sha256':sha(q) if q.exists() else None,'build_source_sha256':sha(R/'build_model.py'),'parameters_sha256':sha(R/'parameters.json'),'stdout':proc.stdout,'stderr':proc.stderr,'method':'Fresh source CSG construction and byte-for-byte binary-STL comparison; no reuse of cached mesh.'}
(R/'reproducibility.json').write_text(json.dumps(report,indent=2)+'\n');print({'passed':same});raise SystemExit(0 if same else 1)
