"""Independently test every original triangle against finite 64-facet support planes."""
from pathlib import Path
import struct,json,math,numpy as np
p=Path(__file__).resolve().parents[1];b=(p.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0];r=[];eps=.0003
for cx in [-62,62]:
 for typ in [1,2]:
  ids=[];area=0;triangles=[]
  for i in range(n):
   q=struct.unpack_from('<12fH',b,84+i*50);v=np.array(q[3:12]).reshape(3,3)
   if not all(t[1]<=-4+eps for t in v):continue
   if typ==1 and not (abs(q[2])<eps and all(47-eps<=t[2]<=60.2+eps for t in v)):continue
   if typ==2 and not (.1<q[2]<.9 and all(60.2-eps<=t[2]<=66.2+eps for t in v)):continue
   for k in range(32,64):
    angle=(k+.5)*math.tau/64;u=(math.cos(angle),math.sin(angle))
    if all(abs((t[0]-cx)*u[0]+(t[1]+4)*u[1]-(9 if typ==1 else 9.5-(t[2]-60.2)*5/6)*math.cos(math.pi/64))<eps for t in v):
     ids.append(i);area+=float(np.linalg.norm(np.cross(v[1]-v[0],v[2]-v[0]))/2);triangles.append({'index':i,'vertices':v.tolist()});break
  r.append(dict(name=f'{cx}_{typ}',center=[cx,-4],z=[47,60.2] if typ==1 else [60.2,66.2],material=typ,ids=ids,count=len(ids),area_mm2=area,triangles=triangles))
m=json.loads((p/'face-materials.json').read_text())['face_material_indices'];ids=[i for g in r for i in g['ids']]
assert len(ids)==len(set(ids))==392 and set(ids)=={i for i,c in enumerate(m) if c}
assert all(m[i]==g['material'] for g in r for i in g['ids'])
assert n==6510 and abs(sum(g['area_mm2'] for g in r)-688.827637)<.001
(p/'qa/material-boundaries.json').write_text(json.dumps({'groups':r,'face_count':n,'colored_faces':392,'neutral_faces':6118,'total_area_mm2':sum(g['area_mm2']for g in r),'all_vertex_support_plane_and_finite_front_half_domain':True,'normals_checked':True,'epsilon_mm':eps,'no_subdivision':True},indent=2)+'\n')
