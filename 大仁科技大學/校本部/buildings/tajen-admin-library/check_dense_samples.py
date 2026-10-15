"""Stream all original triangle samples directly into gzip; no giant plain CSV copy."""
from pathlib import Path
import trimesh,numpy as np,subprocess,tempfile,gzip,json,hashlib
R=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as td:
 t=Path(td);m=trimesh.load(R/'model.stl',process=False);m.triangles.astype('float64').tofile(t/'triangles.bin')
 subprocess.run(['g++','-O3','-std=c++17',str(R/'dense_ray.cpp'),'-o',str(t/'dense_ray')],check=True)
 h=hashlib.sha256();proc=subprocess.Popen([str(t/'dense_ray'),str(t/'triangles.bin'),'/dev/stdout'],stdout=subprocess.PIPE)
 with (R/'dense-samples.csv.gz').open('wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0,compresslevel=6) as dst:
  while True:
   chunk=proc.stdout.read(1024*1024)
   if not chunk:break
   h.update(chunk);dst.write(chunk)
 assert proc.wait()==0
(R/'dense-sampling-binding.json').write_text(json.dumps({'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'raw_csv_sha256':h.hexdigest(),'csv_gzip_sha256':hashlib.sha256((R/'dense-samples.csv.gz').read_bytes()).hexdigest(),'triangle_count':len(m.faces),'sample_count':len(m.faces)*7,'storage':'raw output streamed directly into gzip, all values retained','limits':'All first segments and later air gaps retained. Short chords require separate source/root interpretation, not automatic failure or exemption.'},indent=2))
