"""Read-only ray tests of delivered STL: curved pavilion solid, sloped, fused to B wing."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
R=Path(__file__).resolve().parent;out=R/'curved-glass-body-check.json';out.write_text(json.dumps({'passed':False,'checks':{'completed':False}}));T=trimesh.load(R/'model.stl',process=False).triangles

def ray(origin,direction,max_distance):
 origin=np.array(origin,float);direction=np.array(direction,float);hits=[]
 for a,b,c in T:
  e1=b-a;e2=c-a;h=np.cross(direction,e2);det=np.dot(e1,h)
  if abs(det)<1e-10:continue
  f=1/det;s=origin-a;u=f*np.dot(s,h)
  if not -1e-7<=u<=1+1e-7:continue
  q=np.cross(s,e1);v=f*np.dot(direction,q)
  if v<-1e-7 or u+v>1+1e-7:continue
  d=f*np.dot(e2,q)
  if 0<=d<=max_distance:hits.append((origin+d*direction).tolist())
 return sorted(set(tuple(round(q,5) for q in p) for p in hits))
rays={'vertical_through_pavilion':ray([20,-31,-1],[0,0,1],20),'wing_to_curve_low':ray([15.6,-63,5],[0,1,0],45),'wing_to_curve_high':ray([15.6,-63,12],[0,1,0],45)}
vertical=rays['vertical_through_pavilion'];lo=rays['wing_to_curve_low'];hi=rays['wing_to_curve_high']
checks={'vertical_only_bottom_and_solid_roof':len(vertical)==2 and abs(vertical[0][2])<1e-5 and abs(vertical[-1][2]-14.9)<1e-4,'lower_wing_and_pavilion_fused':len(lo)==2,'upper_wing_and_pavilion_fused':len(hi)==2,'facade_slopes_inward_with_height':len(lo)==len(hi)==2 and lo[-1][1]-hi[-1][1]>.8}
r={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'method':'Moller-Trumbore unmodified STL ray intersections. Vertical ray has only z0 base and z14.9 pavilion roof; Y rays cross B wing and pavilion with no internal separating faces; upper front edge recedes.','rays_xyz_mm':rays,'not_physical_print_test':True};out.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));raise SystemExit(0 if r['passed'] else 1)
