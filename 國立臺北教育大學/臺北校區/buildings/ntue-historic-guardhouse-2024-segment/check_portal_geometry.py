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
rays=[{'label': 'large_window_recess', 'origin': [30, -62, 22], 'direction': [0, 1, 0]}, {'label': 'subfloor_vent_recess', 'origin': [19, -60, 6], 'direction': [0, 1, 0]}, {'label': 'sheet_hood_thickness_and_void', 'origin': [35, -53, 50], 'direction': [0, 0, -1]}]
for r in rays:r['intersections_mm']=hits(r['origin'],r['direction'])
assert abs(rays[0]['intersections_mm'][0][1]+46)<1e-4
assert abs(rays[1]['intersections_mm'][0][1]+46.5)<1e-4
assert abs(rays[2]['intersections_mm'][0][2]-44.571429)<1e-4
assert abs(rays[2]['intersections_mm'][1][2]-42.571429)<1e-4
measures={'main_window_recess_mm':2.5,'subfloor_recess_mm':2,'sheet_hood_vertical_thickness_mm':2,'full_interior_reconstructed':False}
report={'stl_sha256':hashlib.sha256((M/'model.stl').read_bytes()).hexdigest(),'method':'Moller-Trumbore original STL triangles; process=False, no repair; equal-face duplicates collapsed 1e-5 mm','units':'model millimetres, not real surveyed values','measurements':measures,'rays':rays,'passed':True}
(M/'portal-ray-proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
