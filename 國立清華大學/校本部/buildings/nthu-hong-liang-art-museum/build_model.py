"""Original photo-derived NTHU exterior miniature, dimensions in millimetres.
No source 3D assets, survey plans, or interior arrangements used.
Run: python build_model.py (see requirements.txt).
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h): return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h): parts.append(box(x,y,z,w,d,h))
def det(x,y,z,w,d,h): details.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h): cuts.append(box(x,y,z,w,d,h))
def ellipse(x,y,z,rx,ry,h): return Manifold.cylinder(h,1,1,circular_segments=96).scale((rx,ry,1)).translate((x,y,z))
def wedge(poly,y,depth): return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def column(x,y,z,r,h): parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
# Three completed upper galleries, staggered front planes. Exteriors only.
# Ground slope flattened; lower glazed envelope is an opaque printable backing.
add(0,0,0,150,100,3)
# Lower mass reaches base. Long ground-floor setbacks retain floating reading.
add(-43,2,2.8,38,44,13.8)
add(5,5,2.8,62,38,13.8)
add(53,9,2.8,28,35,13.8)
# Upper three boxes and narrow recessed glazed links.
add(-48,0,16,34,52,23)
add(4,-2,16,59,52,23)
add(54,4,16,28,48,23)
add(-28,5,3,7,41,28)
add(36,8,3,6,38,21)
# Metal panel vertical joints are shallow grooves, not separate thin plates.
for x in [-61,-56,-51,-46,-41,-36]:cut(x,-26,17,.45,.65,21)
for x in [43,48,53,58,63,67]:cut(x,-20,17,.45,.65,21)
for y in [-20,-14,-8,-2,4,10,16,22]:
 cut(-65,y,17,.65,.45,21)
 cut(68,y,17,.65,.45,21)
# Recessed glazed ground-floor strips with robust mullions.
cut(-43,-20,4,34,2.6,10.5)
for x in [-57,-50,-43,-36,-29]:det(x,-20,4,1.1,3,10.5)
cut(-2,-14,4,38,3,10.5)
for x in [-19,-9,1,11]:det(x,-14,4,1.1,3.5,10.5)
cut(53,-8.5,4,24,2.5,10.5)
for x in [43,50,57,64]:det(x,-8.5,4,1.1,3,10.5)
# Wide concrete support under central gallery and slim entrance pier.
add(24,-15,3,13,19,13.4)
column(-20,-25,3,1.4,13.5)
# Visible end glazed wall, beneath metal upper box.
cut(-62,2,4,2.7,40,10.5)
for y in [-16,-6,4,14,20]:det(-62,y,4,3.2,1.1,10.5)
# Low red-brick external return visible in end view, fused to shared base.
add(-67,7,3,2.4,50,7)
add(-64,-17,3,8,4,7)
# No invented rooftop plant; unseen rear plain. All galleries solid internally.
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
