from pathlib import Path
import numpy as np,json,struct
from build_appearance import regions
A=Path(__file__).resolve().parents[1];raw=(A.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0];t=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)]).reshape(n,3,3);m=json.loads((A/'face-materials.json').read_text())['face_material_indices'];e=2e-5;out=[];ids=[]
for name,x0,x1,z0,z1 in regions():
 found=[]
 for i,v in enumerate(t):
  normal=np.cross(v[1]-v[0],v[2]-v[0])
  if normal[1]<0 and all(abs(y+60.32)<e and x0-e<=x<=x1+e and z0-e<=z<=z1+e for x,y,z in v):found.append(i)
 ids+=found;v=t[found];out.append(dict(name=name,rectangle_xz=[x0,x1,z0,z1],canonical_stl_ids=found,triangles=v.tolist(),area_mm2=float(np.linalg.norm(np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]),axis=1).sum()/2)))
assert len(ids)==len(set(ids))==54 and set(ids)=={i for i,c in enumerate(m) if c==1};assert all(c==0 for i,c in enumerate(m) if i not in ids)
area=sum(r['area_mm2'] for r in out);assert abs(area-827.71692)<.001
(A/'qa/material-boundaries.json').write_text(json.dumps(dict(original_faces=n,colored_faces=54,neutral_faces=n-54,regions=out,area_mm2=area,support_plane_y=-60.32,all_three_vertices_finite_plane_checked=True,no_subdivision=True,no_centroid_selection=True,epsilon_mm=e),indent=2)+'\n')
