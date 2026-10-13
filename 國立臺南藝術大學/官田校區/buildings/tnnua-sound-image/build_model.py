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
add(0,0,0,150,136,3)
# Wedge landscape roof: principal 1:6 inclination described by the university.
parts.append(slope([(-57,2.8),(57,2.8),(57,25),(-57,6)],134))
# Outdoor roof courts: open to sky down to a solid basal floor, no hidden interior.
for x,y,w,d in [(-42,-12,27,24),(-6,-10,26,27),(35,-10,36,24),(-36,28,20,20),(1,29,28,21)]:parts[1]=parts[1]-box(x,y,4.5,w,d,35)
# Relative top elevations calibrated to the official ground-level ensemble photo: 82 mm tower / 60 mm theatre; approximate scene, no measured site levels.
# Eight-storey slender tower behind the slope, offset from the theatre.
add(-43,35,2.8,31,22,78.2)
add(-43,35,80.5,32,23,1.5)
# One large externally supported grid on its public front elevation.
cut(-43,23.6,34,22,3.5,42)
for x in np.linspace(-54,-32,7):det(float(x),22.6,34,1,3,42)
for z in np.linspace(34,76,12):det(-43,22.6,float(z),23,3,1)
# Side slot and high balcony seen from both photo corners.
for z in [28,37,46,55,64,73]:cut(-58.5,35,z,2.2,2.5,4)
add(-58.5,35,68,7,9,1.7)
add(-61,35,69,1.2,9,2.4)
# Irregular rear punched-window rhythm on actual reverse photo.
for x,z,w,h in [(-53,39,2.4,3),(-40,43,4,5),(-32,36,2.2,4),(-52,54,3,4),(-41,57,5,5),(-31,51,2.2,4),(-52,69,3,4),(-39,72,4,5),(-31,66,2,4),(-51,82,3,4),(-40,85,5,4),(-31,79,2,4)]:cut(x,46,3+(z-3)*.85,w,2.4,h*.85)
# Raised opaque theatre block and low glazed entrance pavilion.
add(38,6,2.8,39,43,57.2)
for x in [29,36,43]:cut(x,-15.5,36,1.6,3,14)
add(34,-22,3,49,16,23)
cut(34,-30,5.5,43,2.8,18)
for x in [14,22,30,38,46,54]:det(x,-30.4,5,1.3,4.1,21)
add(33,-22,25.5,52,19,1.8)
# The prominent descending stepped edge is a visible external roof/terrace feature.
for i in range(9):add(-60,-52+i*5.5,3,8,6,3+i*.9)
# Circular open entry court is a visible negative form; no rooms represented.
cuts.append(ellipse(4,-49,3.2,13,13,15))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
