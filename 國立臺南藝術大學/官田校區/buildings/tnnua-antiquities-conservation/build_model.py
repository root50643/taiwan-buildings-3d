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
add(0,0,0,150,109,3)
# Interlocking solids and wall planes observed in two built exterior photographs.
add(-40,6,2.8,40,53,46)
add(30,12,2.8,63,50,18)
add(27,6,20,69,47,24)
# Broad projecting planes, offset and tilted in plan instead of a simple rectangular box.
parts.append(box(-41,-23,3,44,3,51).rotate((0,0,-4)))
parts.append(box(-10,-14,3,3,51,55).rotate((0,0,-5)))
parts.append(box(60,10,17,3,58,36).rotate((0,0,5)))
add(-42,5,53,48,61,2.6)
add(26,9,48,74,57,2.6)
# Recess beneath the upper projecting front volume.
cut(32,-13,3.2,44,16,16)
col(44,-12,3,1.6,17.5)
# Deep front glass strip with slender but thickened mullions.
cut(28,-17.5,23,58,3.5,19)
for x in [2,12,22,32,42,52]:det(x,-17.8,23,1.2,3.8,19)
# Left wall's irregular punched slots, accurately unlike a regular classroom grid.
for x,z,w,h in [(-57,16,2,12),(-47,10,2,6),(-30,21,3.5,2),(-45,27,3.5,2),(-35,24,3.2,2),(-55,31,3.2,2),(-22,33,2,8)]:cut(x,-20.5,z,w,9,h)
# Central tall fin has isolated slit and clear shadow gap.
cut(-10,-31,42,2,12,8)
cut(-17,-8,18,8,20,27)
# Oblique right end: upper narrow apertures only, lower recess.
for y in [3,20]:cut(61,y,31,4,7,3)
# Rear/north broad glazing supported by official exterior perspective images;
# exact rear geometry remains a simplified pair of bands.
for x,w in [(-40,27),(27,52)]:
 for z in [10,29]:cut(x,32 if x<0 else 28.5,z,w,4,12)
for x in [-50,-40,-30,7,20,33,46]:
 for z in [10,29]:det(x,32 if x<0 else 28.5,z,1.2,4.6,12)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
