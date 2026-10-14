"""Dense designated roof/glazing root checks on first original triangle hit.
Probe top surface vertically, then its actual face normal, retain all intersections.
Finite designated sampling, not exhaustive minimum-wall proof.
"""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
R=Path(__file__).parent;m=trimesh.load(R/'model.stl',process=False);S=2.7;GL=4.7;rows=[]
def hits(o,d):
 o=np.array(o,float);d=np.array(d,float);d/=np.linalg.norm(d);p,_,f=m.ray.intersects_location([o],[d],multiple_hits=True);h=sorted((float(np.dot(q-o,d)),int(fi),q.tolist())for q,fi in zip(p,f)if np.dot(q-o,d)>=0);u=[]
 for q in h:
  if not u or abs(q[0]-u[-1][0])>1e-7:u.append(q)
 return u
def sample(feature,x,y,rooted=False):
 h=hits([x*S,y*S,100],[0,0,-1]);assert h;face=h[0][1];p=np.array(h[0][2]);n=m.face_normals[face];a=hits(p+n*.000001,-n);assert len(a)>=2 and abs(a[0][0]-.000001)<.00001
 chord=a[1][0]-a[0][0];assert chord>=.8-1e-5,(feature,x,y,chord)
 root=hits([x*S,y*S,-1],[0,0,1])
 if rooted:assert len(root)==2 and abs(root[0][0]-1)<1e-5,(feature,x,y,root)
 rows.append(dict(feature=feature,xy_m=[x,y],original_triangle_index=face,surface_point_mm=p.tolist(),original_outward_normal=n.tolist(),first_solid_chord_mm=chord,all_normal_hits=a,all_vertical_hits=root,vertical_root_to_base_required=rooted))
for x in [-9,0,9]:
 for dx in [-2.95,-1.5,0,1.5,2.95]:
  for y in [6.05,6.3,6.5,8,9.95]:sample('north raised slope and cap',x+dx,y,True)
for x in np.linspace(-11.3,11.3,9):
 for y in [-.2,0,.2]:sample('truncated main ridge',float(x),y,True)
for x in [-20,-15,-5,5,15,20]:
 for y in [-15.70,15.70]:
  if y<0 and -1<x<13:continue
  sample('main eave near outer edge',x,y)
for x in [-.95,13.05]:
 for y in [-15,-12,-9.45]:sample('south recess roof edge',x,y)
for x in [-10.4,-9,-6,-4,-2,1,2.4]:
 for y in [15.3,18,21.55]:sample('gable roof and filled front edge',x,y)
checks={'all_designated_original_face_normals_first_chord_ge0p8mm':True,'north_raised_slopes_and_main_ridge_vertical_root_continuous':True,'actual_face_index_and_all_hits_recorded':True}
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),passed=True,checks=checks,sample_count=len(rows),minimum_sampled_chord_mm=min(x['first_solid_chord_mm']for x in rows),samples=rows,limits='Finite samples on specified original faces; supplemented by all-triangle four-point audit. Not global min wall, slicing or physical test.');(R/'roof-normals.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items()if k!='samples'})
