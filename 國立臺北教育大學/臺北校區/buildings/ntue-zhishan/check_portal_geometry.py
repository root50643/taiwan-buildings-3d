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
scale=150/117.7
rays=[dict(label='recessed_entry_depth',origin=[23,-60,10],direction=[0,1,0]),dict(label='canopy_to_steps_clearance',origin=[23,-40,30],direction=[0,0,-1])]
for r in rays:r['origin']=(np.array(r['origin'])*scale).tolist();r['intersections_mm']=hits(r['origin'],r['direction'])
assert abs(rays[0]['intersections_mm'][0][1]-(-20.5*scale))<1e-4
zs=[p[2] for p in rays[1]['intersections_mm']]
assert abs(zs[1]-17*scale)<1e-4 and abs(zs[2]-5.4*scale)<1e-4
report={'stl_sha256':hashlib.sha256((M/'model.stl').read_bytes()).hexdigest(),'method':'Moller-Trumbore original STL triangle ray intersections; process=False, no repair; same-face duplicates collapsed 1e-5 mm','units':'model mm, not surveyed building dimensions','entry_depth_from_main_front_plane_mm':9.5*scale,'canopy_to_step_clearance_mm':11.6*scale,'rays':rays,'passed':True}
(M/'portal-ray-proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
