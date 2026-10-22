from pathlib import Path
import struct,json,numpy as np
from build_appearance import DOMAINS
p=Path(__file__).resolve().parents[1];b=(p.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0];r=[];eps=.0002
for name,y,x0,x1,z0,z1,c in DOMAINS:
 ids=[];area=0;triangles=[]
 for i in range(n):
  q=struct.unpack_from('<12fH',b,84+i*50);v=np.array(q[3:12]).reshape(3,3)
  if q[1]<-.99 and all(abs(vv[1]-y)<eps and x0-eps<=vv[0]<=x1+eps and z0-eps<=vv[2]<=z1+eps for vv in v):
   ids.append(i);area+=float(np.linalg.norm(np.cross(v[1]-v[0],v[2]-v[0]))/2);triangles.append({'index':i,'vertices':v.tolist()})
 r.append(dict(name=name,y=y,x=[x0,x1],z=[z0,z1],material=c,ids=ids,count=len(ids),area_mm2=area,triangles=triangles))
m=json.loads((p/'face-materials.json').read_text())['face_material_indices'];ids=[i for g in r for i in g['ids']]
assert len(ids)==len(set(ids))==14 and set(ids)=={i for i,c in enumerate(m) if c}
assert all(m[i]==g['material'] for g in r for i in g['ids'])
assert n==8666 and abs(sum(g['area_mm2'] for g in r)-1263.87546)<.001
(p/'qa/material-boundaries.json').write_text(json.dumps({'groups':r,'face_count':n,'colored_faces':14,'neutral_faces':8652,'total_area_mm2':sum(g['area_mm2']for g in r),'all_vertex_plane_and_finite_domain':True,'front_normals_checked':True,'epsilon_mm':eps,'no_subdivision':True},indent=2)+'\n')
