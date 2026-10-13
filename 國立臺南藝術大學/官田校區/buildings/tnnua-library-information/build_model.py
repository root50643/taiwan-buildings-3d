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
# Elliptic core, stepped parapets and asymmetric roof masses from official map and exterior photos.
add(0,0,0,150,108,3)
parts.append(ellipse(0,2,2.8,66,40,40))
# Raised central rooftop and side circular recesses seen in the campus bird's-eye map.
add(0,8,42,55,49,6)
for x in [-48,48]:
 parts.append(ellipse(x,6,42,9,10,2))
 cuts.append(ellipse(x,6,43.1,7.7,8.7,3))
# White coping bands represented as shallow geometric ledges, no texture needed.
parts.append(ellipse(0,2,40.5,66.7,40.7,2.3))
parts.append(ellipse(0,2,7.5,66.6,40.6,1.1))
# Broad curved front wings and centered deep entrance.
parts.append(ellipse(0,-28,2.8,41,17,22))
parts.append(ellipse(0,-28,24,42,17.5,1.8))
cut(0,-44,4.8,24,11,15.5)
for x in [-9,-4,4,9]:det(x,-40.9,5,1.2,5.5,15)
# Front blank brick expanse with two narrow slot stacks; not uniform invented windows.
for x in [-47,47]:
 for z in [12,25,34]:cut(x,-26, z,3.4,10,6)
# Front cornice and short recessed upper strip.
cut(0,-34,30,47,8,4)
# Simplified paired phoenix silhouette and crest panel, thickened for miniature.
add(0,-26,42.5,29,3.3,5)
for sign in [-1,1]:
 pts=[(sign*x,z) for x,z in [(1,47),(4,47),(9,51),(15,52),(16,55),(11,53),(7,53),(5,57),(3,57),(4,51)]]
 parts.append(profile(pts if sign==1 else pts[::-1],-26,2))
# Low entrance apron and stairs overlap the base.
for i in range(5):add(0,-49+i*1.5,3,38-2*i,2,0.55*(i+1))
# Unseen rear kept as simple oval envelope with no fabricated window schedule.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
