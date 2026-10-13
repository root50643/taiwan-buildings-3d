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
# White eight-storey block: public street and lawn-facing external views.
add(0,0,0,150,122,3)
add(12,9,2.8,108,66,96.2)
# Offset tall end tower, split visually by continuous recessed vertical window strip.
add(-49,-4,2.8,30,77,106.2)
cut(-49,-42.5,3,9,5,106.5)
for z in [9,22,35,48,61,74,87,100]:
 det(-49,-42,z,9.4,5.5,2.2)
# Large multi-storey glazed entrance recess on public lawn elevation.
cut(22,-24,3,48,8,34)
for x in [0,9,18,27,36,45]:det(x,-25,3,1.3,10,34)
for z in [9,16,23,30]:det(22,-25,z,48,9,1.3)
# Five upper recessed horizontal window bands and narrow tall adjoining bays.
for z in [42,53,64,75,86]:
 cut(27,-24,z,67,4,6.7)
 for x in [-4,7,18,29,40,51,59]:det(x,-24,z,1.1,4.5,6.7)
 for x in [-25,-18,-11]:cut(x,-24,z,3.8,3,7)
# Opposite public street long elevation observed as five broad horizontal bands.
for z in [42,53,64,75,86]:
 cut(14,42,z,98,4,6.7)
 for x in range(-30,62,11):det(x,42,z,1.1,4.5,6.7)
# End windows seen around tower-to-main junction.
for z in [9,22,35,48,61,74,87]:cut(-34,-5,z,3,38,7)
# Exterior entry steps, no internal atrium or circulation model.
for i in range(3):add(22,-32+i*2,3+i*.8,51,8-i*2,.9)
# Roof grille, flags, bus shelter and trees omitted; unobserved end plain.
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
