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
add(0,0,0,150,148,3)
# Two meandering wings around a broad open landscape. Heights vary by segment.
for side in [-1,1]:
 ang=-side*10
 group=[];sub=[];features=[]
 def A(x,y,z,w,d,h):group.append(box(x,y,z,w,d,h))
 def C(x,y,z,w,d,h):sub.append(box(x,y,z,w,d,h))
 def D(x,y,z,w,d,h):features.append(box(x,y,z,w,d,h))
 x=side*43
 for y,ht in [(-38,57 if side==1 else 39),(0,49 if side==1 else 42),(37,40)]:
  A(x+(3 if y==0 else 0)*side,y,2.8,26,40,ht)
  A(x+(3 if y==0 else 0)*side,y,ht+2.2,31,43,2)
 # Deep ground loggia and two strong continuous balcony levels.
 C(x-side*12,1,3.2,12,107,10)
 for y in [-48,-30,-12,6,24,42,53]:D(x-side*10,y,3,10,2.2,11)
 for z in [13,24,35]:
  A(x-side*2,1,z,33,112,1.5)
  C(x-side*13,1,z+2,4,107,6)
  for y in [-49,-35,-21,-7,7,21,35,49]:D(x-side*12.2,y,z+1,3,1.2,7.4)
 # Narrow punched slots on outer return, intentionally not copied to every surface.
 for y in [-45,-18,10,40]:
  for z in [18,29,40]:
   if z<40 or y<20:C(x+side*15,y,z,8,5,4)
 # Prominent vertical stair tower and alternating terrace cutbacks.
 A(x+side*9,-42,2.8,11,22,58 if side==1 else 41)
 for z in [15,26,37,48]:
  if side==1 or z<40:C(x+side*14,-42,z,5,18,7)
 # Asymmetric roof stair enclosure/canopy, thickened for miniature.
 A(x,-36,60 if side==1 else 43,11,16,6)
 A(x,-36,65.5 if side==1 else 48.5,17,22,1.8)
 # Unite within a wing before rotation, then add to the shared base.
 wing=group[0]
 for q in group[1:]:wing=wing+q
 for q in sub:wing=wing-q
 for q in features:wing=wing+q
 parts.append(wing.rotate((0,0,ang)))
# No rooms, access-control arrangements or individual occupancy information.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
