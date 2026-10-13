"""Original photo-derived NTHU exterior miniature, dimensions in millimetres.
No source 3D assets, survey plans, or interior arrangements used.
Run: python build_model.py (see requirements.txt).
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h): return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h): parts.append(box(x,y,z,w,d,h))
def det(x,y,z,w,d,h): details.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h): cuts.append(box(x,y,z,w,d,h))
def ellipse(x,y,z,rx,ry,h): return Manifold.cylinder(h,1,1,circular_segments=96).scale((rx,ry,1)).translate((x,y,z))
def wedge(poly,y,depth): return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def column(x,y,z,r,h): parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
# 2024 completed renovation exterior, not the pre-renovation EECS facade.
add(0,0,0,150,140,3)
add(-47,3,2.8,31,96,69.2)
add(47,3,2.8,31,96,101.2)
add(0,43,2.8,108,27,101.2)
# Courtyard glazing arranged as recessed square bays with crossed mullions.
for side in [-1,1]:
 x=side*31.5;heights=[10,23,36,49,62] if side<0 else [10,23,36,49,62,75,88]
 for z in heights:
  for y in [-35,-20,-5,10,25]:
   cut(x,y,z,3.5,10,9)
   det(x,y,z,4,1.2,9);det(x,y,z+4.5,4,10,1.1)
for z in [10,23,36,49,62,75,88]:
 for x in [-26,-13,13,26]:
  cut(x,29.5,z,9,3.5,9)
  det(x,29.5,z,1.1,4,9);det(x,29.5,z+4.5,9,4,1.1)
# Projecting centre strip with two subtly upturned top corners.
add(0,27.5,28,13,5,79)
parts.append(wedge([(-7,107),(0,105),(7,107),(7,110),(0,108),(-7,110)],27.5,5))
# Newly fitted extended mesh sunshades simplified as layered thick ribs.
for z in [29,66,97]:
 det(0,26,z,67,6,1.4)
 det(0,26,z+2,67,6,1.4)
for side,h in [(-1,72),(1,104)]:
 for z in [29,66,97]:
  if z<h:
   for zz in [z,z+2]:det(side*30,1,zz,6,85,1.4)
# Prominent outer facade window groups; unphotographed far back is simplified.
for side in [-1,1]:
 h=72 if side<0 else 104
 for z in range(10,h-7,13):
  for y in [-31,-15,1,17,33]:
   cut(side*62.5,y,z,3,10,9)
   det(side*62.5,y,z,3.5,1.2,9)
# Exterior shading bands continue along the outer wings seen in renovation photos.
for side,h in [(-1,72),(1,104)]:
 for z in [29,66,97]:
  if z<h:
   for zz in [z,z+2]:det(side*63,2,zz,4,92,1.4)
# Lower wing end with public exterior semi-circular stair/landing silhouette.
for z in [12,25,38,51,64]:parts.append(ellipse(-58,-44,z,7,7,1.8))
add(-59,-41,3,4,7,67)
# Two rooftop vent/pavilion forms visible above the lower courtyard wing.
for y in [-15,22]:
 column(-47,y,71,6,4)
 parts.append(Manifold.cylinder(7,6,0.9,circular_segments=32).translate((-47,y,75)))
# Entrance portal and broad split stair approach with centre planted strip omitted.
for x in [-16,16]:add(x,12,3,3.5,7,18)
add(0,12,20,36,7,3)
add(0,26,3,24,9,18)
cut(0,21.5,5,15,3,13)
for i in range(7):
 for x in [-11,11]:add(x,-32+i*6,3,18,7,1+i*1.8)
# All in One artwork as coarse tilted open cube; micro-tubes and letters omitted.
frame=Manifold.cube((14,14,14),center=True)
for dims in [(18,10.5,10.5),(10.5,18,10.5),(10.5,10.5,18)]:frame=frame-Manifold.cube(dims,center=True)
frame=frame.rotate((18,24,24)).translate((0,16,34))
parts.append(frame)
add(0,16,22,2.2,2.2,13)
# Rear wall remains plain; no internal room or equipment reconstruction.
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
