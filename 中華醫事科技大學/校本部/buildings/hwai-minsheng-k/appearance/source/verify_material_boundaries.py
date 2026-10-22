"""Independent polygon-edge parametrization; no use of builder classification."""
from pathlib import Path
import json,struct,math,numpy as np
A=Path(__file__).resolve().parents[1];raw=(A.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0];t=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)]).reshape(n,3,3);c=np.array(json.loads((A/'face-materials.json').read_text())['face_material_indices']);eps=.00015
selected=set();layers={};records=[]
for z in [72.8,85.8,98.8]:
 ids=[]
 for i,tri in enumerate(t):
  if min(tri[:,2])<z-eps or max(tri[:,2])>z+3+eps:continue
  norm=np.cross(tri[1]-tri[0],tri[2]-tri[0]);norm/=np.linalg.norm(norm)
  if abs(norm[2])>eps:continue
  for k in range(48):
   a=np.array([48+9*math.cos(k*math.tau/48),-8+9*math.sin(k*math.tau/48)]);b=np.array([48+9*math.cos((k+1)*math.tau/48),-8+9*math.sin((k+1)*math.tau/48)]);e=b-a;d=tri[:,:2]-a
   u=d@e/(e@e);distance=np.abs(d[:,0]*e[1]-d[:,1]*e[0])/np.linalg.norm(e);out=np.array([e[1],-e[0]])/np.linalg.norm(e)
   if distance.max()<eps and min(u)>=-eps and max(u)<=1+eps and norm[:2]@out>1-eps:
    ids.append(i);records.append({'face':i,'layer_z':z,'facet':k,'max_plane_error_mm':float(distance.max()),'edge_parameter_range':[float(min(u)),float(max(u))]});break
 assert len(ids)==36,(z,len(ids));layers[str(z)]=ids;selected.update(ids)
assert selected==set(np.where(c==1)[0]);assert len(selected)==108
r={'method':'Independent 48-gon edge endpoint projection and signed outward unit normal; every vertex on same finite outer facet','full_triangle_membership_only':True,'no_centroid_or_subdivision':True,'layers':layers,'colored_faces':108,'neutral_faces':int((c==0).sum()),'inner_arcs_caps_undersides_end_faces_excluded':True,'scout_delta_faces':[2640,2758,2876],'scout_delta_reason':'Initial raw normal-z tolerance rejected float32-rounded small triangles; finite facet proof confirms entire outer surface','facet_checks':records}
(A/'qa/material-boundaries.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS independent 48-edge facet proof: 108 full triangles')
