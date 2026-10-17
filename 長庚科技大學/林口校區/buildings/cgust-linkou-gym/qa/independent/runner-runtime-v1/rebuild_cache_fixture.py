"""Bitwise reconstruction of the tiny negative cache fixture using original logical filename."""
from pathlib import Path
import sys,json,hashlib,os,py_compile,shutil

def require(v,m):
 if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=sys.argv[sys.argv.index('--')+1:];source,original,out=map(lambda p:Path(p).absolute(),a);require(not out.exists() and sys.dont_write_bytecode is True and sorted(os.sched_getaffinity(0))==[0],'Fresh controlled rebuild required');source_hash=sha(source);original_hash=sha(original);out.mkdir(parents=True);shutil.copyfile(source,out/'fixture.py');os.utime(out/'fixture.py',(0,0));os.chdir(out);py_compile.compile('fixture.py',cfile='rebuilt.pyc',dfile='fixture.py',doraise=True,invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
require(sha('rebuilt.pyc')==original_hash and Path('rebuilt.pyc').read_bytes()==original.read_bytes(),'Cache bitwise reconstruction differs');require(sha(source)==source_hash and sha(original)==original_hash,'Original fixture changed');r={'passed':True,'source_unchanged':True,'original_cache_unchanged':True,'source_sha256':source_hash,'original_cache_sha256':original_hash,'rebuilt_cache_sha256':sha('rebuilt.pyc'),'bitwise_identical':True,'logical_code_filename':'fixture.py','source_mtime_epoch':0,'python_version':sys.version.split()[0],'cpu_affinity':sorted(os.sched_getaffinity(0)),'checker_sha256':sha(__file__),'scope':'Tiny synthetic cache control only. Complete original fixture retained privately; this recipe actually reconstructs its bytes without a private absolute code filename.'};Path('results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':True,'bitwise_identical':True}))
