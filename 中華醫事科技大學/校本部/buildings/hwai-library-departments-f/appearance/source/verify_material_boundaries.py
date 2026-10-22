"""Independent finite facet endpoint proof, with normalized radius per height."""
from pathlib import Path
import json,struct,math,numpy as np
A=Path(__file__).resolve().parents[1];raw=(A.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0];t=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)]).reshape(n,3,3);c=np.array(json.loads((A/'face-materials.json').read_text())['face_material_indices']);eps=.00015
selected=[];records=[]
for i,tri in enumerate(t):
 if min(tri[:,0])<34-eps or min(tri[:,2])<64-eps or max(tri[:,2])>68.5+eps:continue
 normal=np.cross(tri[1]-tri[0],tri[2]-tri[0]);normal/=np.linalg.norm(normal)
 if normal[2]<=0:continue
 radii=13-(tri[:,2]-64)*4/4.5;xy=(tri[:,:2]-[34,-49])/radii[:,None]
 for k in range(72):
  a=np.array([math.cos(k*math.tau/72),math.sin(k*math.tau/72)]);b=np.array([math.cos((k+1)*math.tau/72),math.sin((k+1)*math.tau/72)]);edge=b-a;d=xy-a;u=d@edge/(edge@edge);distance=np.abs(d[:,0]*edge[1]-d[:,1]*edge[0])/np.linalg.norm(edge)
  out=np.array([edge[1],-edge[0]])/np.linalg.norm(edge);normal_expected=np.r_[out,4/4.5*math.cos(math.pi/72)];normal_expected/=np.linalg.norm(normal_expected)
  if distance.max()<eps/9 and min(u)>=-eps and max(u)<=1+eps and normal@normal_expected>1-eps:
   selected.append(i);records.append({'face':i,'facet':k,'max_normalized_edge_error':float(distance.max()),'u_range':[float(min(u)),float(max(u))]});break
assert set(selected)==set(np.where(c==1)[0]);assert len(selected)==76
r={'method':'Independent radius-normalized finite 72-gon edge endpoint projection and slope unit normal','full_triangle_membership_only':True,'no_centroid_or_subdivision':True,'colored_faces':len(selected),'neutral_faces':int((c==0).sum()),'top_west_shoulders_glass_other_roofs_excluded':True,'facet_checks':records}
(A/'qa/material-boundaries.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS 76 complete finite slope faces')
