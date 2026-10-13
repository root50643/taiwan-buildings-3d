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
add(0,0,0,150,142,3)
# Pure concrete cube with recessed ground glazing, exterior only.
add(0,0,2.8,90,90,95.2)
cut(5,-45,3.2,64,8,11)
for x in [-24,-12,0,12,24,36]:det(x,-42.5,3,1.4,5.5,12)
# Diagonally projecting upper cube, observed on the front photograph.
cut(5,-44.5,58,31,5,35)
poly=[(-8,-43),(13,-60),(32,-50),(32,-40)]
parts.append(CrossSection([poly]).extrude(34).translate((0,0,60)))
# Exterior side stair, its treads and thin stringer embed into the wall.
parts.append(slope([(-34,20),(34,61),(34,63),(-34,22)],9).translate((48,0,0)))
for i in range(21):add(48,-33+i*3.3,21+i*2,10,3.6,1.5)
parts.append(slope([(-34,28),(34,69),(34,70.4),(-34,29.4)],1.7).translate((53.5,0,0)))
for y,z in [(-33,22),(-19,30),(-5,38),(9,46),(23,54),(34,62)]:add(53.5,y,z,1.3,1.3,7)
for y,z in [(-34,20),(34,61)]:cut(45,y,z,4,8,11)
# Two small photographed reverse balconies and door slots, plain rest of wall.
for z in [12,70]:
 cut(6,45,z,8,4,10)
 add(6,47,z,13,8,1.8)
 add(6,50,z+1.7,13,1.2,3.3)
# Ground approach terrace, side ramp and small entry-wall return.
add(-48,-25,3,15,39,10)
cut(-49,-44.5,3.2,5,5,8)
for i in range(6):add(-14,-64+i*2,3,100,2.5,.55*(i+1))
parts.append(slope([(-62,3),(-20,3),(-20,13),(-62,4)],12).translate((-53,0,0)))
# No reconstruction of the inner suspended gallery or internal circulation.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
