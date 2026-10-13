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
add(0,0,0,150,100,3)
# Lakeside restaurant: staggered three-storey glazed wings under stepped red roofs.
add(-29,10,2.8,61,38,32)
add(33,4,2.8,53,43,25)
add(-3,18,2.8,18,31,38)
# Separate pitched volumes and a raised middle roof, not a flat box.
parts.append(slope([(-12,34),(32,34),(18,44)],66).translate((-29,0,0)))
parts.append(slope([(-20,27),(30,27),(11,44)],58).translate((33,0,0)))
parts.append(slope([(0,40),(38,40),(24,46)],23).translate((-3,0,0)))
add(33,-1,35,15,12,6)
cut(33,-7,36,12,3,3)
add(33,-1,40.5,17,14,1.2)
# Broad lakeside glass recesses and thin horizontal floor ledges.
for x,w,y,h in [(-29,55,-9,31),(33,45,-17.5,24)]:
 for z in [6,16,26]:
  if z+6<h+3:
   cut(x,y,z,w,4,6.8)
   for xx in np.arange(x-w/2+3,x+w/2,8):det(float(xx),y+.8,z,1.3,3.8,6.8)
 for z in [13.5,23.5]:add(x,y,z,w+4,3,1.2)
# Front veranda columns and projecting deck visible across the lake.
add(-27,-16,3,66,17,2)
for x in [-56,-42,-28,-14,0]:col(x,-20,4,1.2,29)
add(-28,-20,33,65,4,1.7)
# Shallow side approach steps, with lake and bridge omitted to keep one building focus.
for i in range(6):add(60,-35+i*2,3,13,3,.8*(i+1))
# Unobserved rear wall openings deliberately not extrapolated.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
