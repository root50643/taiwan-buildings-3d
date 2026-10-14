"""Original STL intersections for every front column, rear support, facade fine column,
and backed side pilaster. No processed/repaired mesh; no global-wall guarantee.
"""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
R=Path(__file__).parent;m=trimesh.load(R/'model.stl',process=False);S=2.7;GL=4.7;rows=[]
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);d/=np.linalg.norm(d);p,_,fi=m.ray.intersects_location([o],[d],multiple_hits=True);h=sorted((float(np.dot(q-o,d)),int(f))for q,f in zip(p,fi)if np.dot(q-o,d)>0);u=[]
 for dist,f in h:
  if not u or abs(dist-u[-1][0])>1e-6:u.append((dist,f))
 return u
def root(name,x,y):
 h=ray([x*S,y*S,-1],[0,0,1]);assert len(h)==2 and abs(h[0][0]-1)<1e-5,(name,h)
 rows.append(dict(feature=name,xy_mm=[x*S,y*S],all_original_hits_distance_face=h,continuous_base_to_upper_structure=True))
def width(name,x,y,z,diam):
 for axis in [0,1]:
  q=np.array([x*S,y*S,GL+z*S]);v=np.eye(3)[axis];h=ray(q-v*200,v);assert len(h)%2==0;interval=[(a,b)for a,b in zip(h[::2],h[1::2])if a[0]<=200<=b[0]];assert len(interval)==1,(name,z,axis,h);w=interval[0][1][0]-interval[0][0][0];assert w>=diam*S*.985,(name,z,axis,w)
  rows.append(dict(feature=name,axis=axis,z_mm=q[2],minimum_expected_mm=diam*S*.985,solid_chord_containing_feature_center_mm=w,all_original_hits_distance_face=h))
for x,w in [(-9.7,.72),(-8.2,1.4),(.2,1.4),(1.7,.72)]:
 name=f'front support x{x}';root(name,x,20.5)
 for z in [1.,4.,8.]:width(name,x,20.5,z,w)
for x in [-8.2,.2]:root(f'rear wall-backed support x{x}',x,14.1)
for x in np.linspace(-19.1,19.1,17):
 root(f'facade round column x{x}',float(x),14.15)
 for z in [1.5,4.5,8.5]:width(f'facade round column x{x}',x,14.15,z,.52)
for side in [-1,1]:
 for y in [-12,-7,-2,3,8,12]:root(f'side backed pilaster {side}/{y}',side*19.475,y)
for x,y in [(-4,18),(-6,18),(-2,18)]:
 h=ray([x*S,y*S,GL+.6*S+.01],[0,0,1]);assert h and h[0][0]>20,(x,y,h)
 rows.append(dict(feature='entrance open space below roof',xy_m=[x,y],clear_height_mm=h[0][0],all_original_hits_distance_face=h))
checks={'four_front_column_two_axis_chords_three_heights':True,'all_four_front_roots_continuous_base_to_roof':True,'seventeen_fine_column_roots_continuous':True,'two_rear_supports_and_twelve_pilasters_rooted':True,'entrance_three_open_clearances_over20mm':True}
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),checks=checks,passed=all(checks.values()),samples=rows,limits='Designated original mesh roots and chords only; supplement with all-triangle surface-chords report. Does not prove exhaustive minimum wall or unsupported printability.');(R/'feature-roots.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items()if k!='samples'})
