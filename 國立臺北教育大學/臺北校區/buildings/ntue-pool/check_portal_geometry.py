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
rays=[dict(label='entry_depth_glazing',origin=[-57,-60,12],direction=[0,1,0]),dict(label='center_recess_depth',origin=[-53,-60,12],direction=[0,1,0]),dict(label='side_wall_clear_span',origin=[-80,-40,15],direction=[1,0,0]),dict(label='soffit_to_floor_clear_height',origin=[-53,-40,50],direction=[0,0,-1])]
for r in rays:r['intersections_mm']=hits(r['origin'],r['direction'])
report={'stl_sha256':hashlib.sha256((M/'model.stl').read_bytes()).hexdigest(),'method':'Moller-Trumbore every original STL triangle; process=False, no repair or section capping; duplicate same-face hits collapsed 1e-5 mm','units':'model millimetres, not surveyed real dimensions','front_side_wall_plane_y':-47.5,'glazing_frame_front_y':-28.5,'open_depth_mm':19,'clear_width_mm':28.6,'clear_height_mm':30.5,'rays':rays}
assert abs(rays[0]['intersections_mm'][0][1]+28.5)<1e-4
assert abs(rays[2]['intersections_mm'][2][0]-rays[2]['intersections_mm'][1][0]-28.6)<1e-4
assert abs(rays[3]['intersections_mm'][1][2]-rays[3]['intersections_mm'][2][2]-30.5)<1e-4
report['passed']=True
(M/'portal-ray-proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
