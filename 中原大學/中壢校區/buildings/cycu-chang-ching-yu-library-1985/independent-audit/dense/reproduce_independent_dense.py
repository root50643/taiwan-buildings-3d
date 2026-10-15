"""Reproduce finite raw-STL dense, first-material/air, backing and corner diagnostics.
Run in a model copy: python reproduce_independent_dense.py --model-dir PATH --output PATH.
Requires Python numpy/pandas/trimesh/rtree, a C++17 compiler and OpenMP.
Raw original warnings and failed alternative methods are retained; exit0 means the
reproduction completed, NOT that every local thickness test or printability passed.
"""
from pathlib import Path
import argparse,tempfile,subprocess,shutil,hashlib,json,gzip,os,sys
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--model-dir',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--output',type=Path,default=Path('independent-dense-reproduction'));a=p.parse_args();B=a.model_dir.resolve();D=Path(__file__).resolve().parent;a.output.mkdir(parents=True,exist_ok=True)
raw=(B/'model.stl').read_bytes();assert hashlib.sha256(raw).hexdigest()=='76939c4a6901112a66b76a6c87de5b76829de584bcac9b61e2d5b2a301a36e86'
with tempfile.TemporaryDirectory(prefix='cycu-independent-')as t:
 W=Path(t);T=np.frombuffer(raw,offset=84,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])['v'].astype(float);T.tofile(W/'cycu-library-dense-triangles.bin')
 for f in D.glob('*.py.in'):(W/f.name.removesuffix('.in')).write_text(f.read_text().replace('@WORK@',str(W)).replace('@MODEL@',str(B)))
 for name in ['npust-yukang-dense-roots.py','tajen-dense-roots.py']:shutil.copyfile(W/'ray-parser.py',W/name)
 for src,exe in [('dense-original.cpp','dense-original'),('exact-original.cpp','exact-original'),('strict-rays.cpp','cmu-dense-strict'),('winding-original.cpp','cmu-dense-flag-winding-omp')]:subprocess.run(['g++','-O2','-std=c++17','-fopenmp',str(D/src),'-o',str(W/exe)],check=True)
 env=dict(os.environ,OMP_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
 def run(args):subprocess.run([str(x)for x in args],check=True,env=env)
 def script(name):run([sys.executable,W/f'cycu-library-{name}.py'])
 run([W/'dense-original',W/'cycu-library-dense-triangles.bin',W/'cycu-library-dense.csv']);script('exact-prepare');run([W/'exact-original',W/'cycu-library-dense-triangles.bin',W/'cycu-library-exact-queries.bin',W/'cycu-library-exact-hits.csv',W/'cycu-library-exact-indices.bin']);script('exact-summarize')
 for name in ['short-roots','corner-roots','corner-edge-proof','seven-corner-check','seven-tangent-path','backing-boxes','root-controls','coplanar-independent']:script(name)
 index=[]
 for f in sorted(W.glob('cycu-library-*')):
  if f.suffix not in ['.json','.gz','.csv']:continue
  raw=f.read_bytes();out=a.output/(f.name if f.suffix=='.gz'else f.name+'.gz')
  if f.suffix=='.gz':out.write_bytes(raw)
  else:
   with out.open('wb')as dest:
    with gzip.GzipFile(filename='',fileobj=dest,mode='wb',mtime=0)as g:g.write(raw)
  gzip.decompress(out.read_bytes());index.append({'path':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'uncompressed_source_sha256':hashlib.sha256(raw).hexdigest()})
 (a.output/'reproduction-index.json').write_text(json.dumps({'stl_sha256':hashlib.sha256((B/'model.stl').read_bytes()).hexdigest(),'original_triangles':len(T),'files':index,'strict_warnings_not_overridden':True,'no_global_minimum_wall_or_print_guarantee':True},indent=2))
print('Completed finite reproduction. Consult original warnings and failed alternatives; this is not a physical-print pass.')
