"""Reproducible read-only four-cardinal-ray audit of all non-bed undersides."""
import argparse, hashlib, io, json
from pathlib import Path
import numpy as np
import trimesh
from independent_qa import rays

p=argparse.ArgumentParser();p.add_argument('stl');p.add_argument('--out',required=True);a=p.parse_args()
if Path(a.out).exists():raise FileExistsError(f'Refusing to overwrite {a.out}')
data=Path(a.stl).read_bytes();m=trimesh.load_mesh(io.BytesIO(data),file_type='stl',process=False);m.merge_vertices(digits_vertex=7)
e=max(m.extents)*1e-8
ids=np.where((m.face_normals[:,2]<-np.cos(np.pi/4))&(m.triangles_center[:,2]>m.bounds[0,2]+e*20))[0]
o=m.triangles_center[ids]+[0,0,-e*5]
d,f=rays(m,np.repeat(o,4,axis=0),np.tile([[1.,0,0],[-1.,0,0],[0,1.,0],[0,-1.,0]],(len(ids),1)))
d=d.reshape(-1,4);f=f.reshape(-1,4);rows=[]
for k in np.where(~np.any(np.isinf(d),axis=1))[0]:
    rows.append({'face':int(ids[k]),'vertices_mm':m.triangles[ids[k]].tolist(),'centroid_mm':m.triangles_center[ids[k]].tolist(),'cardinal_distances_mm':d[k].tolist(),'hit_faces':f[k].tolist()})
report={'stl_sha256':hashlib.sha256(data).hexdigest(),'directions':['+X','-X','+Y','-Y'],'underside_start_offset_mm':float(e*5),'total_underside_samples':len(ids),'samples_with_at_least_one_open_cardinal_ray':int(np.sum(np.any(np.isinf(d),axis=1))),'closed_cardinal_sample_count':len(rows),'faces':rows,'limitation':'Finite centroid ray samples; an open ray is not a proof of real support removability.'}
Path(a.out).write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
