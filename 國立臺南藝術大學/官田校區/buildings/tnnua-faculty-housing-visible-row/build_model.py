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
add(0,0,0,150,78,3)
# A single continuous photographed row only, not two invented independent banks.
# Five adjoining modules represent the visible segment, not five certified housing blocks.
for i in range(5):
 x=-52+i*26; y=9+[0,1.5,0,-1.5,0][i];h=[37,38,37,39,38][i]
 add(x,y,2.8,26.5,32,h)
 # Low shallow gabled roof: long ridge runs along the contiguous row.
 poly=[(y-18,h+2),(y,h+7),(y+18,h+2),(y+18,h+4),(y,h+9),(y-18,h+4)]
 if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))<0:poly=poly[::-1]
 parts.append(CrossSection([poly]).extrude(27).rotate((90,0,90)).translate((x-13.5,0,0)))
 # Recessed upper balcony and projecting brick middle-level terrace.
 cut(x-3,y-16,26,15,5,10)
 add(x-3,y-18,24.8,19,8,1.8)
 add(x-3,y-21,26,19,1.5,3.5)
 for dx in [-8,1,6]:det(x+dx,y-17,26,1.2,4.2,10)
 add(x+4,y-19,14,19,7,1.6)
 add(x+4,y-21.8,15.5,19,1.5,4)
 cut(x+4,y-16,17,11,3.5,5)
 cut(x-5,y-16,5,10,3.5,7)
 # Upper parapet/projection makes stepped roof line visible from canal.
 add(x+8,y-13,h-1,9,6,5)
# Low continuous creekside platform; water/landscape is reduced to a shallow channel.
add(0,-14,2.8,140,19,2.2)
# No other bank, housing A-H assignment, interiors or residents reconstructed.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
