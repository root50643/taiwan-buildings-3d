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
add(0,0,0,150,110,3)
# Photo-derived asymmetrical front: tall brick blade, recessed centre, projected right wing.
add(-43,8,2.8,43,77,63)
add(43,16,2.8,40,66,64)
add(0,35,2.8,54,30,57)
# Center front is deeply recessed, with separate open terrace and upper screened link.
add(0,-9,2.8,48,17,18)
add(0,-19,23,51,7,2)
add(0,-22,25,51,1.3,4)
for x in [-21,-14,-7,0,7,14,21]:add(x,-22,25,1.2,1.3,6)
add(0,-12,44,50,20,15)
# Tall facade fins on upper central connecting bridge.
for x in range(-22,25,5):add(x,-23,45,1.6,3,20)
# Left brick screen distinguished by broad recessed panel and alternating coarse brick relief.
cut(-49,-31,23,26,3,39)
for z in range(24,62,3):
 for i in range(6):
  x=-60+i*4.2+(1 if z%2 else 0)
  det(x,-31,z,3.2,3.4,1.2)
# Two open-square exterior porch cutouts beside the brick blade.
for z in [28,51]:cut(-29,-29,z,11,16,12)
for x in [-36,-31,-26,-21]:det(x,-30.5,26,1.3,3,21)
add(-43,-3,65,47,84,2.2)
# Right forward cantilevered plain volume, with tall fins under it and deep side setback.
add(43,-24,33,52,25,18)
add(43,-17,2.8,41,23,30.4)
for x in [24,31,38,45,52,59]:
 cut(x,-29,5,4.3,3,23)
 det(x-2.8,-31,3,1.4,3,29.8)
# Minimal glass division at recessed ground entrance, not internal layout.
cut(0,-18,5,42,2.5,13)
for x in [-18,-9,0,9,18]:det(x,-18,4.8,1.3,3,13.4)
# Shallow return apertures visible near right facade edge only; back deliberately plain.
for z in [18,31,44]:cut(63,7,z,3,10,6)
# Low external entry steps.
for i in range(3):add(0,-39+i*2,3,45,2.5,.7*(i+1))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
