"""Original TNNUA exterior miniature, millimetres. Public photo-derived estimates.
Run: python build_model.py. No source 3D assets or interior/security details used.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def det(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def ellipse(x,y,z,rx,ry,h):return Manifold.cylinder(h,1,1,circular_segments=128).scale((rx,ry,1)).translate((x,y,z))
def profile(poly,y,depth):
 if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))<0:poly=poly[::-1]
 return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def slope(poly,width):return CrossSection([poly]).extrude(width).rotate((90,0,90)).translate((-width/2,0,0))
def col(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
add(0,0,0,150,124,3)
# Two parallel enclosed wings and a low foreground courtyard plinth.
add(0,0,2.8,116,89,14)
add(-43,6,16,29,77,23)
add(43,6,16,29,77,23)
add(0,33,16,87,23,23)
# Lower outdoor court is an open shallow terrace, not an interior arrangement.
cut(0,-12,12.5,48,45,6)
# Airy high outer canopy, with a central exposed skylight opening.
roof=box(0,1,47,136,102,2.4)-box(0,-3,46.8,36,35,3)
parts.append(roof)
for x in [-63,-27,27,63]:
 for y in [-39,35]:col(x,y,2.8,1.6,45)
# Roof beams and raised rear block visible in aerial view.
for x in [-15,-5,5,15]:add(x,-3,46.5,1.5,38,1.5)
add(-41,29,49,20,20,2)
# Visible rectangular rooftop projection and its overhanging cap.
add(29,-11,16,12,14,42)
add(29,-11,57.5,20,22,2)
for x in [24,27,30,33]:cut(x,-18,49,1.2,2,6)
# Long louvered upper wings: horizontal relief strips over shallow recess.
for side in [-1,1]:
 for xx in [side*28.5,side*57.5]:
  cut(xx,5,25,3.4,65,11)
  for z in [25,28,31,34]:det(xx,5,z,4,65,1.1)
 # Lower external plinth panels/windows, simple visible subdivision.
 for y in [-31,-14,3,20,37]:cut(side*58,y,5,3,10,6)
# Courtyard connecting bridge visible under the large canopy.
add(0,15,28,63,7,2)
add(0,11.5,30,63,1.3,2.8)
add(0,18.5,30,63,1.3,2.8)
# Front platform edge and offset broad exterior approach steps.
for x in [-49,-31,-12,7,26,45]:cut(x,-44.5,5,9,3,6)
for i in range(8):add(-37,-57+i*1.6,3,35,2,1.2*(i+1))
# No water, internal mechanical systems, furniture or security details modeled.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
