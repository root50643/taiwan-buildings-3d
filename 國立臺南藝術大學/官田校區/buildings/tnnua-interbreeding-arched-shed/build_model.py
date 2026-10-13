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
add(0,0,0,150,112,3)
# Original broad semicylindrical steel shelter, exterior shell and columns only.
def tube(length,r):return Manifold.cylinder(length,r,r,circular_segments=128).rotate((0,90,0)).translate((-length/2,0,2.8))
clip=box(0,0,2.8,145,104,52)
shell=(tube(126,44)-tube(130,41.2))^clip
parts.append(shell)
# Raised external ribs, exaggerated to printable thickness.
for x in [-62,-42,-21,0,21,42,62]:
 rib=(Manifold.cylinder(1.6,45,45,circular_segments=128)-Manifold.cylinder(1.8,43.7,43.7,circular_segments=128).translate((0,0,-.1))).rotate((0,90,0)).translate((x-.8,0,2.8))
 parts.append(rib^clip)
# Open gable frames, deliberately no reconstruction of workroom interiors.
for x in [-60,60]:
 for y in [-27,0,27]:col(x,y,2.8,1.3,39 if y==0 else 34)
 add(x,0,34,2.8,60,2)
# Low frontal timber-deck mass visible in the historical exterior image.
add(0,-47,2.8,76,13,2)
for i in range(4):add(0,-53+i*1.4,3,50,2,.45*(i+1))
# Open ends prevent hidden enclosed cavity shells; thin roof needs print supports.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
