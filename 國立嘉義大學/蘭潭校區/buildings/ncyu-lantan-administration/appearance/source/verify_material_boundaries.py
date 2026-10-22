from pathlib import Path
import struct,json,numpy as np
p=Path(__file__).resolve().parents[1];b=(p.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0];r=[];eps=.0002
# Independent loop deliberately does not import build classifier.
for x in [-47,47]:
 for xx in [x-12,x-4,x+4,x+12]:
  for yy in [-30,-20,-10,0,10,20,30]:
   if not(abs(xx)>46 or yy<0):continue
   ids=[];area=0;triangles=[]
   for i in range(n):
    q=struct.unpack_from('<12fH',b,84+i*50);v=np.array(q[3:12]).reshape(3,3)
    if q[2]>.99 and all(abs(vv[2]-47.5)<eps and xx-3.25-eps<=vv[0]<=xx+3.25+eps and yy-4.25-eps<=vv[1]<=yy+4.25+eps for vv in v):
     ids.append(i);area+=float(np.linalg.norm(np.cross(v[1]-v[0],v[2]-v[0]))/2);triangles.append({'index':i,'vertices':v.tolist()})
   assert len(ids)==2 and area==55.25
   r.append(dict(center=[xx,yy],z=47.5,x=[xx-3.25,xx+3.25],y=[yy-4.25,yy+4.25],material=1,ids=ids,count=len(ids),area_mm2=area,triangles=triangles))
m=json.loads((p/'face-materials.json').read_text())['face_material_indices'];ids=[i for g in r for i in g['ids']]
assert len(ids)==len(set(ids))==80 and set(ids)=={i for i,c in enumerate(m) if c}
assert n==4248 and sum(g['area_mm2'] for g in r)==2210
(p/'qa/material-boundaries.json').write_text(json.dumps({'groups':r,'face_count':n,'colored_faces':80,'neutral_faces':4168,'total_area_mm2':2210,'all_vertex_plane_and_finite_domain':True,'upward_normals_checked':True,'epsilon_mm':eps,'no_subdivision':True,'not_actual_pv_panel_count':True},indent=2)+'\n')
