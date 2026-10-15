"""All original triangle barycentric normal first segments. Finite sampling, not wall proof."""
from pathlib import Path
import trimesh,numpy as np,subprocess,tempfile,gzip,shutil,json,hashlib
R=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as td:
 t=Path(td);m=trimesh.load(R/'model.stl',process=False);m.triangles.astype('float64').tofile(t/'triangles.bin')
 subprocess.run(['g++','-O3','-std=c++17',str(R/'dense_ray.cpp'),'-o',str(t/'dense_ray')],check=True)
 subprocess.run([str(t/'dense_ray'),str(t/'triangles.bin'),str(t/'samples.csv')],check=True)
 raw_csv_sha=hashlib.sha256((t/'samples.csv').read_bytes()).hexdigest()
 with (t/'samples.csv').open('rb') as src,(R/'dense-samples.csv.gz').open('wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0,compresslevel=6) as dst:shutil.copyfileobj(src,dst)
(R/'dense-sampling-binding.json').write_text(json.dumps({'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'raw_csv_sha256':raw_csv_sha,'csv_gzip_sha256':hashlib.sha256((R/'dense-samples.csv.gz').read_bytes()).hexdigest(),'triangle_count':len(m.faces),'sample_count':len(m.faces)*7,'limits':'All first segments and later air gaps retained. Counts of short chords are not automatic failures or exemptions; classify real corners, backed relief and thin bands separately.'},indent=2))
