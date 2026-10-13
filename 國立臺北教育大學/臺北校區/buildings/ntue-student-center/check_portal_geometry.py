from pathlib import Path
import json, hashlib
import numpy as np
import trimesh
M=Path(__file__).resolve().parent; mesh=trimesh.load(M/'model.stl',process=False)
def hits(o,d):
 o=np.array(o,float);d=np.array(d,float);t=mesh.triangles;e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);a=np.einsum('ij,ij->i',e1,h);safe=np.abs(a)>1e-9;f=np.zeros_like(a);f[safe]=1/a[safe];s=o-t[:,0];u=f*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=f*np.einsum('j,ij->i',d,q);dist=f*np.einsum('ij,ij->i',e2,q);ok=safe&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(dist>=0)
 ds=[]
 for x in sorted(dist[ok]):
  if not ds or x-ds[-1]>1e-5:ds.append(float(x))
 return (o+np.array(ds)[:,None]*d).round(6).tolist()
rays=[{'label': 'ground_entry_depth', 'origin': [0, -72, 10], 'direction': [0, 1, 0]}, {'label': 'ground_portal_clear_height', 'origin': [0, -49, 20], 'direction': [0, 0, -1]}, {'label': 'second_portal_depth', 'origin': [0, -72, 26], 'direction': [0, 1, 0]}, {'label': 'upper_balcony_void', 'origin': [20, -52, 52], 'direction': [0, 0, -1]}]
for r in rays:r['intersections_mm']=hits(r['origin'],r['direction'])
assert abs(rays[0]['intersections_mm'][0][1]+37)<1e-4
assert [q[2] for q in rays[1]['intersections_mm']]==[19.,3.,0.]
assert abs(rays[2]['intersections_mm'][0][1]+37)<1e-4
assert abs(rays[3]['intersections_mm'][0][2]-51)<1e-4
assert abs(rays[3]['intersections_mm'][1][2]-37.3)<1e-4
measures={'ground_entry_depth_from_front_pier_mm':19,'ground_entry_clear_height_mm':16,'second_entry_depth_from_front_pier_mm':19,'balcony_clear_height_mm':13.7}
report={'stl_sha256':hashlib.sha256((M/'model.stl').read_bytes()).hexdigest(),'method':'Moller-Trumbore original STL triangles; process=False, no repair; equal-face duplicates collapsed 1e-5 mm','units':'model millimetres, not real surveyed values','measurements':measures,'rays':rays,'passed':True}
(M/'portal-ray-proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
