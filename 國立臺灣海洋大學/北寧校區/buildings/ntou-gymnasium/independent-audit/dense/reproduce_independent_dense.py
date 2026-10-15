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
raw=(B/'model.stl').read_bytes();assert hashlib.sha256(raw).hexdigest()=='752b4c147bd18874b1c49890596c260e58015520f71f60cebc6ee6144700ef49'
with tempfile.TemporaryDirectory(prefix='ntou-independent-')as t:
 W=Path(t);T=np.frombuffer(raw,offset=84,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])['v'].astype(float);T.tofile(W/'ntou-revision-dense-triangles.bin')
 for f in D.glob('*.py.in'):(W/f.name.removesuffix('.in')).write_text(f.read_text().replace('@WORK@',str(W)))
 shutil.copyfile(W/'ray-parser.py',W/'npust-yukang-dense-roots.py')
 for src,exe in [('dense-original.cpp','dense-original'),('strict-rays.cpp','cmu-dense-strict'),('winding-original.cpp','cmu-dense-flag-winding-omp')]:subprocess.run(['g++','-O2','-std=c++17','-fopenmp',str(D/src),'-o',str(W/exe)],check=True)
 env=dict(os.environ,OMP_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
 def run(args):subprocess.run([str(x)for x in args],check=True,env=env)
 run([W/'dense-original',W/'ntou-revision-dense-triangles.bin',W/'ntou-revision-dense.csv'])
 for n in ['short-roots','local-patches','root-controls']:run([sys.executable,W/f'ntou-revision-{n}.py'])
 def finite(x):
  if isinstance(x,float)and not np.isfinite(x):return None
  if isinstance(x,dict):return {k:finite(v)for k,v in x.items()}
  if isinstance(x,list):return [finite(v)for v in x]
  return x
 index=[]
 for f in sorted(W.glob('ntou-revision-*')):
  if f.suffix not in ['.json','.gz','.csv']:continue
  data=gzip.decompress(f.read_bytes())if f.suffix=='.gz'else f.read_bytes()
  if f.name.endswith(('.json','.json.gz')):data=json.dumps(finite(json.loads(data)),ensure_ascii=False,allow_nan=False).encode()
  out=a.output/(f.name if f.suffix=='.gz'else f.name+'.gz')
  with out.open('wb')as dest:
   with gzip.GzipFile(filename='',fileobj=dest,mode='wb',mtime=0)as g:g.write(data)
  index.append({'path':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'decompressed_sha256':hashlib.sha256(data).hexdigest()})
 (a.output/'reproduction-index.json').write_text(json.dumps({'stl_sha256':hashlib.sha256(raw).hexdigest(),'original_triangles':len(T),'files':index,'nonfinite_policy':'JSON null for unbounded after-air / absent third event; original CSV infinity and event absence preserved. Never zero thickness.','strict_warnings_not_overridden':True,'no_global_minimum_wall_or_print_guarantee':True},indent=2))
print('Completed finite reproduction; no automatic exception or physical-print approval.')
