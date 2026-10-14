"""Dense samples on original actual face normals at the north/east facade joint."""
from check_architectural_rays import tri,norm,ray,R,S
import numpy as np,json,hashlib
rows=[]
weights=[(1/3,1/3,1/3),(.8,.1,.1),(.1,.8,.1),(.1,.1,.8),(.48,.48,.04),(.48,.04,.48),(.04,.48,.48)]
for i,(f,n) in enumerate(zip(tri,norm)):
 c=f.mean(axis=0);x,y,z=c[0]/S,-c[1]/S,(c[2]-2)/S
 if not (39.5<x<42.5 and -25<y<-20.5 and 4.2<z<15.7 and abs(n[2])<1e-5 and (n[0]>.8 or n[1]>.8)):continue
 for w in weights:
  p=np.array(w)@f;a=ray(p-n*.0001,-n);assert a
  front=bool(n[0]>.99 or (n[1]>.8 and abs(n[0])>.01))
  root_direction=[-1,0,0] if p[0]/S>41.7 else [-.1723803,-.9850305,0]
  backing=ray(p-n*.0001,root_direction)
  assert backing
  rows.append({'face':i,'barycentric':w,'point_mm':p.tolist(),'normal':n.tolist(),'solid_normal_mm':a[0]+.0001,'facade_front_skin':front,'inward_X_backing_mm':backing[0],'actual_backing_direction':root_direction})
front_rows=[r for r in rows if r['facade_front_skin']]
relief=[r for r in rows if not r['facade_front_skin']]
assert front_rows and min(r['solid_normal_mm'] for r in front_rows)>.8
assert all(r['inward_X_backing_mm']>.8 for r in relief)
j={'passed':True,'sample_count':len(rows),'original_face_count':len(set(r['face'] for r in rows)),'minimum_facade_front_skin_normal_mm':min(r['solid_normal_mm'] for r in front_rows),'minimum_backed_decorative_edge_normal_mm':min(r['solid_normal_mm'] for r in relief),'minimum_decorative_edge_wall_normal_root_mm':min(r['inward_X_backing_mm'] for r in relief),'selection':'All original vertical faces in corner x39.5..42.5m,y-25..-20.5m,z4.2..15.7m with outward X or north normal >0.8; seven interior barycentric samples per face.','limitation':'All selected faces sampled: facade-facing skin normals separately checked; decorative shallow window-edge normals may be0.390625mm, with actual facade-inward full-wall root checked at every point. Not a global wall certificate. No mesh repair.','samples':rows,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()};(R/'corner-skin-check.json').write_text(json.dumps(j,indent=2));print({k:v for k,v in j.items() if k!='samples'})
