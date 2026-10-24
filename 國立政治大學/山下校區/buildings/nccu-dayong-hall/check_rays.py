"""Raw analytic triangle rays; every tread plus finite ramp endpoints and sampled thickness."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;_,v,f=raw_read(A/'model.stl');m=trimesh.Trimesh(v,f,process=False);S=2.5;rows=[]
def ray(name,x,y,h,expected_top=None):
 o=np.array([x,y,h+.08])*S;loc,_,_=m.ray.intersects_location([o],[[0,0,-1]]);assert len(loc),name;hit=loc[np.linalg.norm(loc-o,axis=1).argmin()];expected=h if expected_top is None else expected_top;err=abs(hit[2]-expected*S);rows.append(dict(name=name,origin_mm=o.tolist(),first_hit_mm=hit.tolist(),expected_top_mm=expected*S,error_mm=float(err)));assert err<.003,(name,err)
for c in [-27.8,-10.7,11.4,27.8]:
 for k in range(3):
  z=.5+k*3.3
  for flight in [0,1]:
   for i in range(9):
    y=(3.35+i*.34+.18) if not flight else (6.07-i*.34+.18);h=z+(i+1)*3.3/18+(1.65 if flight else 0)
    for x in ([c-1.67,c-1.05,c-.35] if not flight else [c+.35,c+1.05,c+1.67]):ray(f'core{c}_level{k}_flight{flight}_step{i}',x,y,h)
for i in range(12):
 h=max(1.87,3.8-(i+1)*1.95/12)
 for x in [-12,-10.5,-9]:ray(f'external_step{i}',x,-5.3-(i+1)*.33+.16,h)
for x in [-28.9,-28.6,-28.51,-28.49,-28.4,-28.1,-12.7,-12.51,-12.49,-12.4,-12.35]:
 h=1.88 if x<-28.5 else (3.8 if x>-12.5 else 1.88+(x+28.5)/16*1.92)
 for y in [-5,-4.6,-4.15]:
  q=lambda v:round(v*1024)/1024
  realend=q(-10.5-2.15);top=q(1.88) if x<-28.5 else (q(3.8) if x>=realend else q(1.88)+(x+28.5)/(realend+28.5)*(q(3.8)-q(1.88)))
  ray('ramp_endpoint',x,y,h,top)
for y in [-15.05,-14,-12,-10.91,-10.89,-10.5,-9.4]:
 h=1.85 if y>-10.9 else .18+(y+15.2)/4.3*1.67
 for x in [-12,-10.5,-9]:ray('foot_grade_top',x,y,h)
for x in [-33.35,-32,-30,-29.56,-29.54,-29,-28.6]:
 h=1.88 if x>-29.55 else .18+(x+33.5)/3.95*1.70
 for y in [-5.2,-4.7,-4.2]:ray('ramp_grade_top',x,y,h)
ids=np.random.default_rng(20261024).choice(len(f),512,replace=False);norm=m.face_normals[ids];orig=m.triangles_center[ids]-norm*.0001;mins=np.full(len(ids),np.inf)
for start in range(0,len(ids),64):
 loc,ir,it=m.ray.intersects_location(orig[start:start+64],-norm[start:start+64],multiple_hits=True)
 for i,d in zip(ir,np.linalg.norm(loc-orig[start+ir],axis=1)):
  if d>1e-6:mins[start+i]=min(mins[start+i],d)
assert np.isfinite(mins).all()
r=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),route_rays=rows,route_ray_count=len(rows),sampled_normal_thickness=dict(count=512,seed=20261024,minimum_mm=float(mins.min()),below_0_8mm_count=int((mins<.8).sum()),samples=[dict(face=int(i),thickness_mm=float(d)) for i,d in zip(ids,mins)]),limits='Raw analytic triangle rays. Sampled thickness is not global minimum wall/strength or printability certification; no physical print.')
(A/'qa/ray-validation.json').write_text(json.dumps(r,indent=2));print('route rays',len(rows),'normal rays',len(ids),'minimum',mins.min())
