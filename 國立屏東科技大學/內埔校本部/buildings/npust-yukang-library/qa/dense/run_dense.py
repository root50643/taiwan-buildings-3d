"""Original raw STL -> 7-point original-face probes, streamed directly to gzip."""
from pathlib import Path
import tempfile,subprocess,gzip,hashlib,json,struct,numpy as np
R=Path(__file__).parent;M=R.parents[1];raw=(M/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0]
a=np.frombuffer(raw,offset=84,dtype=[('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')]);assert len(a)==n
with tempfile.TemporaryDirectory()as td:
 t=Path(td);a['v'].astype('<f8').tofile(t/'triangles.bin')
 subprocess.run(['g++','-O2','-std=c++17',str(R/'dense-ray.cpp'),'-o',str(t/'dense')],check=True)
 with open(R/'run.log','wb')as log,open(R/'all-original.csv.gz','wb')as dest:
  proc=subprocess.Popen([str(t/'dense'),str(t/'triangles.bin'),'/dev/stdout'],stdout=subprocess.PIPE,stderr=log)
  with gzip.GzipFile(filename='',mode='wb',fileobj=dest,mtime=0,compresslevel=6)as f:
   while True:
    b=proc.stdout.read(1024*1024)
    if not b:break
    f.write(b)
  assert proc.wait()==0
(R/'input.json').write_text(json.dumps({'stl_sha256':hashlib.sha256(raw).hexdigest(),'triangles':n,'sample_count':7*n,'samples':'centroid, .98/.01/.01 permutations, .495/.495/.01 permutations','no_mesh_processing':True},indent=2))
# The raw CSV remains authoritative, including literal inf for unbounded after-air.
import csv
with gzip.open(R/'all-original.csv.gz','rt')as f,gzip.open(R/'short-original.csv.gz','wt',newline='')as out:
 reader=csv.DictReader(f);writer=csv.DictWriter(out,fieldnames=reader.fieldnames);writer.writeheader();total=short=flags=0;minimum=float('inf')
 for row in reader:
  total+=1;x=float(row['first_solid']);minimum=min(minimum,x)
  if x<.8:short+=1;writer.writerow(row)
  if tuple(int(row[k])for k in ['inside_control','outside_control','mid_control','after_exit_control'])!=(1,0,1,0):flags+=1
(R/'initial-summary.json').write_text(json.dumps({'sample_count':total,'short_under0_8':short,'control_flags':flags,'minimum_first_solid':minimum,'status':'diagnostic only; flags and short chords require first-solid/root classification; not approved'},indent=2))
