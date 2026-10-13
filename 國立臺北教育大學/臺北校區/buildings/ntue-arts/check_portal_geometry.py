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
rays=[dict(label='center_entrance_depth',origin=[0,-80,12],direction=[0,1,0]),dict(label='between_front_column_pair',origin=[-60,-57,12],direction=[1,0,0]),dict(label='curved_slab_underside_to_steps',origin=[0,-57,90],direction=[0,0,-1]),dict(label='solid_left_front_column',origin=[-9,-57,24],direction=[0,0,-1])]
for r in rays:r['intersections_mm']=hits(r['origin'],r['direction'])
assert abs(rays[0]['intersections_mm'][0][1]+35.7)<1e-4
xx=[q[0] for q in rays[1]['intersections_mm'] if abs(q[0])<15]
assert len(xx)==4 and abs(xx[2]-xx[1]-14.2)<1e-4
zz=[q[2] for q in rays[2]['intersections_mm']]
assert abs(zz[1]-25.5)<1e-4 and abs(zz[2]-4.9)<1e-4
report={'stl_sha256':hashlib.sha256((M/'model.stl').read_bytes()).hexdigest(),'method':'Moller-Trumbore every original STL triangle; process=False, no repair or section capping; duplicate same-face hits collapsed 1e-5 mm','units':'model millimetres, not surveyed real dimensions','curved_front_soffit_y':-68.2,'center_recess_surface_y':-35.7,'center_open_depth_from_curved_front_mm':32.5,'clear_width_between_front_columns_mm':14.2,'clear_height_above_steps_mm':20.6,'rays':rays,'passed':True}
(M/'portal-ray-proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
