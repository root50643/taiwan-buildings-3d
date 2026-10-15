"""All dense first-exit after-probes: distance to unchanged original faces.
Candidates need exact plane/interval and two-sided winding; distance alone is not classification.
"""
from pathlib import Path
import csv,gzip,numpy as np,trimesh,json
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',process=False)
with gzip.open(R/'dense-original.csv.gz','rt')as f:rows=list(csv.DictReader(f))
pts=[]
for q in rows:
 n=np.array([float(q[k])for k in ['nx','ny','nz']]);p=np.array([float(q[k])for k in ['exit_x','exit_y','exit_z']]);pts.append(p-n*min(1e-5,float(q['air_after'])/4))
pts=np.array(pts);out=[]
for i in range(0,len(pts),1000):
 cp,ds,fs=trimesh.proximity.closest_point(m,pts[i:i+1000])
 for j in np.where(ds<1e-7)[0]:out.append(dict(face=int(rows[i+j]['face']),sample=int(rows[i+j]['sample']),first_solid=float(rows[i+j]['first_solid']),after_point=pts[i+j].tolist(),distance=float(ds[j]),boundary_candidate_face=int(fs[j])))
print('candidates',len(out));(R/'all-after-boundary-candidates.json').write_text(json.dumps(out,indent=2))
