"""Sample actual STL sections for XY features below a 0.8 mm reference width.
A geometric screening only, not a nozzle toolpath simulation or full wall analysis.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
from shapely.geometry import Polygon
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',force='mesh',process=True)
rows=[]
for z in [102.071]:
 # Canonical edge direction gives bitwise-consistent shared-edge intersections.
 tri=m.triangles
 mask=(tri[:,:,2].min(axis=1)<z)&(tri[:,:,2].max(axis=1)>z)
 segments=[]
 for f in tri[mask]:
  hit=[]
  for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
   if tuple(a)>tuple(b):a,b=b,a
   if a[2]<z<b[2] or b[2]<z<a[2]:hit.append(a+(b-a)*(z-a[2])/(b[2]-a[2]))
  if len(hit)==2:segments.append(hit)
 adj={}
 for seg in segments:
  a,b=[tuple(np.round(q[:2],6)) for q in seg]
  if a==b:continue
  adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
 assert adj and all(len(v)==2 for v in adj.values()), f'Unclosed section at {z}: reject thin screening'
 remaining=set(adj);shape=Polygon()
 while remaining:
  seed=next(iter(remaining));a=seed;last=None;loop=[]
  while True:
   loop.append(a);remaining.discard(a)
   if len(adj[a])!=2:break
   opts=adj[a];b=opts[0] if opts[0]!=last else opts[1];last,a=a,b
   if a==seed or len(loop)>len(adj):break
  if len(loop)>2:
   p=Polygon(loop)
   assert a==seed and p.is_valid, f'Invalid closed loop at {z}'
   if p.area>1e-8:shape=shape.symmetric_difference(p)
 assert shape.is_valid, f'Invalid composite section at {z}'

polys=list(shape.geoms) if hasattr(shape,"geoms") else [shape]
rings=[{"z_mm":102.071,"minimum_outer_to_inner_boundary_distance_mm":min(poly.exterior.distance(inner) for inner in poly.interiors),"ring_area_mm2":poly.area,"bounds":list(poly.bounds)} for poly in polys if poly.interiors]
assert len(rings)==1 and rings[0]["minimum_outer_to_inner_boundary_distance_mm"]>=1.25
report={"method":"Actual STL canonical closed XY contour at z102.071; minimum distance between ring exterior and interior boundaries. Local ring width, not whole-model wall thickness.","stl_sha256":hashlib.sha256((R/"model.stl").read_bytes()).hexdigest(),"roof_top_mm":101.9,"ring_bottom_mm":101.4,"ring_top_mm":105,"roof_overlap_mm":.5,"rings":rings}
(R/"roof-ring-check.json").write_text(json.dumps(report,indent=2)+"\n");print(report)
