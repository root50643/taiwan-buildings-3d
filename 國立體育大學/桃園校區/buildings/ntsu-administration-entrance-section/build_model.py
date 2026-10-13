"""Photo-derived entrance section; millimetres, self-built approximate geometry.
Unobserved rear is a plain cut end, not a claimed reconstruction of the whole building.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
P=[];C=[];D=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):P.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):C.append(box(x,y,z,w,d,h))
def cyl(x,y,z,r,h):P.append(Manifold.cylinder(h,r,r,circular_segments=32).translate((x,y,z)))

# Explicitly the central entrance and three adjoining facade bays per side.
add(0,0,0,150,70,3)
add(0,12,2.8,130,28,79)
add(0,9,2.8,32,34,93)
# Real recessed central glazing and open upper tower slot, not regular whole-building windows.
cut(0,-8,43,18,4,37)
cut(0,9,84,18,38,7.6)
# Main entry is a deep double-height porch with two cylindrical stone columns.
cut(0,-8,3,24,18,33)
cyl(-18,-18,2.8,4.4,32.5);cyl(18,-18,2.8,4.4,32.5)
add(0,-17,34,44,16,7)
# Portal lintel and roof return into the tower and form one solid.
add(0,-9,39,42,28,2.0)
for side in [-1,1]:
 for k in range(3):
  x=side*(28+13*k)
  # Double-height outer columns stand in front of lower glazing.
  add(x,-4,2.8,3,6,37)
  for z in [11,26]:cut(x+side*4.5,-2, z,7,3,8)
  cut(x,-2,44,8.5,3,7)
  cut(x,-2,58,8.5,3,7)
  # top clerestory is a paired narrow opening with solid central pier.
  for dx in [-2.6,2.6]:cut(x+dx,-2,73,3.6,3,4)
# Strong tower glazing crossbars, backed by recess; no isolated fine window frames.
for z in [52,65,77]:D.append(box(0,-7.4,z,19,3.4,1.3))
D.append(box(0,-7.4,43,1.4,3.4,37))
# Unobserved rear and side-cut faces intentionally blank.

solid=P[0]
for p in P[1:]:solid=solid+p
for c in C:solid=solid-c
for d in D:solid=solid+d
assert len(solid.decompose())==1
m=solid.to_mesh64();mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,len(mesh.faces),mesh.is_watertight)
