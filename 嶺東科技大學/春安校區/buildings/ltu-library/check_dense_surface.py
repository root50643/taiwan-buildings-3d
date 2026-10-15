"""Every original STL face, ten barycentric original-normal first intervals.
Raw CSV is gzip-compressed without dropping rows. Fixed parity controls are only a numerical
screen; any flags require original-triangle high-precision review, never repair.
"""
from pathlib import Path
import tempfile,subprocess,csv,gzip,shutil,json,hashlib
import numpy as np,trimesh
from original_rays import OriginalRays
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',process=False);T=m.triangles;N=m.face_normals;ray=OriginalRays(m)
W=np.array([[1/3]*3,[.98,.01,.01],[.01,.98,.01],[.01,.01,.98],[.495,.495,.01],[.01,.495,.495],[.495,.01,.495],[.49,.49,.02],[.49,.02,.49],[.02,.49,.49]])
short=[];flags=[];count=0;entryok=True;minchord=float('inf')
with tempfile.TemporaryDirectory()as td:
 D=Path(td);np.asarray(T,dtype='<f8').tofile(D/'triangles.bin');subprocess.run(['g++','-O3','-std=c++17',str(R/'dense_original.cpp'),'-o',str(D/'dense')],check=True);subprocess.run([str(D/'dense'),str(D/'triangles.bin'),str(D/'all.csv')],check=True)
 with open(D/'all.csv')as f:
  for q in csv.DictReader(f):
   count+=1;i=int(q['face']);s=int(q['sample']);p=W[s]@T[i];n=N[i];v=float(q['first_solid']);minchord=min(minchord,v);entryok=entryok and abs(float(q['entry'])-1e-5)<1e-7 and v>0
   if [int(q[k])for k in ['inside_control','outside_control','mid_control','after_exit_control']]!=[1,0,1,0]:flags.append(q)
   if v<.8:
    h=ray.hits(p+n*1e-6,-n)
    short.append(dict(original_triangle_index=i,sample_index=s,surface_point_mm=p.tolist(),original_outward_normal=n.tolist(),first_solid_chord_mm=h[1][0]-h[0][0],all_ray_intersections_mm_face=h,original_cpp_row=q))
 with open(D/'all.csv','rb')as f,gzip.open(R/'dense-original.csv.gz','wb')as g:shutil.copyfileobj(f,g)
 rawsha=hashlib.sha256((D/'all.csv').read_bytes()).hexdigest()
 with gzip.open(R/'dense-original.csv.gz','rb')as f:assert hashlib.sha256(f.read()).hexdigest()==rawsha
checks={'every_original_face_ten_samples':count==len(T)*10,'all_surface_entries_at_declared_offset':bool(entryok),'all_fixed_direction_parity_codes_expected':not flags,'all_first_chords_ge_0p8mm':not short}
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),original_triangles=len(T),samples=count,uncompressed_csv_sha256=rawsha,minimum_first_chord_mm=minchord,under_0p8mm_count=len(short),flags=flags,checks=checks,passed=all(checks.values()),short_chords=short,limits='Finite original-normal sample screen, not global wall thickness. Short chords require real local root/air evidence. Strict false remains until any specific independent exception.')
(R/'dense-short-chords.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items()if k not in ['short_chords','flags']});raise SystemExit(0 if r['passed']else 1)
