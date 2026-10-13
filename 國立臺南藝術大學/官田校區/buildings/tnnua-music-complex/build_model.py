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
add(0,0,0,150,144,3)
# Four parallel long blocks and three front/back courtyard pairs, as in official map.
for x in [-51,-17,17,51]:
 add(x,0,2.8,17,119,39)
 add(x,0,41,20,122,1.7)
 # Exterior balcony strips on the rear halves, photograph-confirmed horizontal rhythm.
 for side in [-1,1]:
  xx=x+side*8.5
  for z in [13,23,33]:
   cut(xx,30,z,5,51,6.5)
   for y in [7,18,29,40,51]:det(xx-side*1.3,y,z,3,1.2,6.5)
  # Teaching-area alternating punched openings in long courtyard elevations.
  for y in [-49,-35,-21]:
   for z in [9,19,29]:
    if not (x==51 and side==1 and y in [-49,-35]):cut(xx,y,z,2.6,6 if y!=-35 else 8,4)
 # End entry slots and top row.
 for xx in [x-4,x+4]:
  for z in [10,21,31]:cut(xx,-59.5,z,3,2.5,4)
# A central row of high-level bridges, with voids beneath retained.
add(0,0,14,121,8,2)
add(0,0,24,121,8,2)
add(0,0,34,121,8,2)
for x in [-34,0,34]:
 for z in [16,26]:
  add(x,-4,z,18,1.4,2.2)
  add(x,4,z,18,1.4,2.2)
 # Glazed bridge rhythm, widened miniature mullions.
 for xx in [x-7,x,x+7]:add(xx,0,14,1.1,8,22)
# End staircase towers and distinctive projecting front rehearsal-room box.
add(62,-38,3,8,28,39)
for z in [13,23,33]:cut(65,-39,z,3,20,6.5)
add(46,-59,14,27,11,11)
cut(46,-64.5,16,23,2.5,7)
for x in [36,42,48,54]:det(x,-64.5,15.5,1.2,3,8)
for x in [35,56]:col(x,-62,3,1.2,12)
# Public approach stair next to the projecting box.
for i in range(10):add(29,-66+i*1.6,3,7,2,1.1*(i+1))
# Unknown outer rear detailing omitted; courtyard topology comes from public map.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
