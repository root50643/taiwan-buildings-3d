"""Original STL local triangle/ray intersections across the diagonal courtyard gallery.
No repair. Verifies open passage, integral support pier, and continuous overhead slab.
"""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
R=Path(__file__).resolve().parent;out=R/'gallery-opening-check.json';out.write_text(json.dumps({'passed':False,'checks':{'completed':False}}))
T=trimesh.load(R/'model.stl',process=False).triangles
p0=np.array([-52.,40.]);delta=np.array([77.,-83.]);normal=np.array([83.,77.]);normal/=np.linalg.norm(normal)
def cast(t,z):
 xy=p0+t*delta;origin=np.r_[xy-6*normal,z];direction=np.r_[normal,0.];hits=[]
 for a,b,c in T:
  e1=b-a;e2=c-a;h=np.cross(direction,e2);det=np.dot(e1,h)
  if abs(det)<1e-10:continue
  f=1/det;s=origin-a;u=f*np.dot(s,h)
  if not (-1e-7<=u<=1+1e-7):continue
  q=np.cross(s,e1);v=f*np.dot(direction,q)
  if v<-1e-7 or u+v>1+1e-7:continue
  distance=f*np.dot(e2,q)
  if 0<distance<12:hits.append(float(distance-6))
 return {'center_xy_mm':xy.tolist(),'z_mm':z,'perpendicular_hit_positions_mm':sorted(set(round(x,5) for x in hits))}
rays={n:cast(t,z) for n,t,z in [('midspan_low',.5,8.),('midspan_high',.5,18.5),('pier',5/11,8.),('slab_midspan',.5,20.5),('slab_above_pier',5/11,20.5)]}
checks={'midspan_open_low':len(rays['midspan_low']['perpendicular_hit_positions_mm'])==0,'midspan_open_high':len(rays['midspan_high']['perpendicular_hit_positions_mm'])==0,'pier_solid_interval':len(rays['pier']['perpendicular_hit_positions_mm'])==2,'slab_midspan_continuous':len(rays['slab_midspan']['perpendicular_hit_positions_mm'])==2,'slab_above_pier_continuous':len(rays['slab_above_pier']['perpendicular_hit_positions_mm'])==2}
report={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'method':'Moller-Trumbore intersections of unmodified STL triangles; rays extend -6 to +6mm perpendicular to diagonal gallery, z8/18.5/20.5. Whole-model connected-shell QA separately verifies all pier/beam unions.','rays':rays,'not_structural_load_test':True};out.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)
