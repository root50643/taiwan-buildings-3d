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
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def slope(poly,width):return CrossSection([poly]).extrude(width).rotate((90,0,90)).translate((-width/2,0,0))
def col(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
add(0,0,0,150,108,3)
# Orthogonal shop box and offset terrace compose the award-publication exterior.
add(-12,14,2.8,77,35,30)
add(-12,14,32,79,37,1.8)
add(22,-13,2.8,74,34,18)
# Lower glazed shop frontage, strong concrete end walls.
cut(21,-30,5,62,4,13)
for x in [-8,5,18,31,44]:det(x,-30,5,1.6,4.6,13)
# Large upper terrace and perimeter parapet are exterior mass, no furnishings.
add(18,-8,20,87,48,2.1)
add(18,-32,22,87,1.5,3)
add(60,-7,22,1.5,48,3)
# Rounded/conical volume joins the oblique circulation edge.
parts.append(Manifold.cylinder(26,12,9,circular_segments=64).translate((48,12,2.8)))
# Front-to-upper exterior ramp represented as a solid, thickened inclined strip.
parts.append(profile([(-69,3),(-26,3),(-26,23),(-69,5)],-39,9))
parts.append(profile([(-69,5),(-26,23),(-26,25),(-69,7)],-44,1.5))
add(-26,-35,21,13,12,2)
# Upper west wall's tall narrow external cutouts.
for x in [-38,-23,-8]:cut(x,-3.5,22,4,4,8)
# A folded shade canopy above terrace: distinctive thin irregular double fold.
parts.append(profile([(-7,46),(18,50),(54,45),(54,47),(18,52),(-7,48)],-6,37))
def beam(a,b,r):
 v=np.array(b)-np.array(a);h=float(np.linalg.norm(v));theta=math.degrees(math.acos(v[2]/h));phi=math.degrees(math.atan2(v[1],v[0]));parts.append(Manifold.cylinder(h,r,r,circular_segments=16).rotate((0,theta,phi)).translate(a))
for x in [3,42]:
 for y in [-20,8]:
  col(x,y,21,1.3,23)
  beam((x,y,37),(x-9,y,(46+(x+2)*4/25 if x-9<=18 else 50-(x-27)*5/36)+.5),1)
  beam((x,y,37),(x+9,y,(46+(x+16)*4/25 if x+9<=18 else 50-(x-9)*5/36)+.5),1)
# Rear photograph does not establish every opening; omit invented detail.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
