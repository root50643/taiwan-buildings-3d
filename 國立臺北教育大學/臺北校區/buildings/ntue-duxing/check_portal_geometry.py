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
rays=[dict(label='main_deep_entry',origin=[45,-80,10],direction=[0,1,0]),dict(label='sloped_soffit_front',origin=[45,-58,60],direction=[0,0,-1]),dict(label='sloped_soffit_back',origin=[45,-40,60],direction=[0,0,-1]),dict(label='courtyard_colonnade_depth',origin=[0,10,8],direction=[0,-1,0]),dict(label='courtyard_colonnade_height',origin=[0,-14,30],direction=[0,0,-1])]
for r in rays:r['intersections_mm']=hits(r['origin'],r['direction'])
assert abs(rays[0]['intersections_mm'][0][1]+32.05)<1e-4
assert abs(rays[1]['intersections_mm'][1][2]-(30-6*9/31))<1e-4
assert abs(rays[2]['intersections_mm'][0][2]-(30-24*9/31))<1e-4
assert abs(rays[3]['intersections_mm'][0][1]+22.5)<1e-4
assert abs(rays[4]['intersections_mm'][1][2]-15)<1e-4
report={'stl_sha256':hashlib.sha256((M/'model.stl').read_bytes()).hexdigest(),'method':'Moller-Trumbore original STL triangles; process=False, no repair; equal-face duplicates collapsed 1e-5 mm','units':'model millimetres, not real surveyed values','main_entry_depth_mm':30.95,'soffit_front_z_mm':30-6*9/31,'soffit_back_z_mm':30-24*9/31,'colonnade_depth_mm':14,'colonnade_clear_height_mm':12,'rays':rays,'passed':True}
(M/'portal-ray-proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
