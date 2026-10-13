"""Direct original-STL X-ray intersections through B-wing piloti, columns and beam.
Does not alter the mesh. Rays run from x=-70 to -32mm, bounded to the B-wing span.
"""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',process=False);T=m.triangles
# Solve barycentric coordinates in the YZ projection for each triangular face.
def cross(y,z):
 hits=[]
 for t in T:
  a,b,c=t;mat=np.column_stack((b[1:]-a[1:],c[1:]-a[1:]));det=np.linalg.det(mat)
  if abs(det)<1e-10:continue
  u,v=np.linalg.solve(mat,np.array([y,z])-a[1:])
  if u>=-1e-7 and v>=-1e-7 and u+v<=1+1e-7:
   x=float(a[0]+u*(b[0]-a[0])+v*(c[0]-a[0]))
   if -70<x<-32:hits.append(x)
 return sorted(set(round(x,5) for x in hits))
rays={name:{'y_mm':y,'z_mm':z,'x_hits_mm':cross(y,z)} for name,y,z in [('walkway_midspan',10.0,6.0),('walkway_upper_clearance',10.0,10.8),('columns',20.0,6.0),('beam_above_columns',20.0,11.2),('beam_above_walkway',10.0,11.2)]}
checks={'walkway_through_both_faces_empty':len(rays['walkway_midspan']['x_hits_mm'])==0,'walkway_clear_to_10_8mm':len(rays['walkway_upper_clearance']['x_hits_mm'])==0,'two_columns_crossed':len(rays['columns']['x_hits_mm'])==4,'solid_continuous_beam_across_columns':len(rays['beam_above_columns']['x_hits_mm'])==2,'solid_continuous_beam_across_walkway':len(rays['beam_above_walkway']['x_hits_mm'])==2}
report={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'method':'X-directed actual-STL triangle intersections, no repair. Empty midspan rays cross full B width; columns give two solid intervals; beam returns outer faces only. Geometry QA separately confirms one connected solid.','rays':rays,'not_a_structural_load_test':True}
(R/'piloti-opening-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)
