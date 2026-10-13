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
# Official 2023 completed aerial and public approach: three linked roof groups.
def yz(poly,x,width):return CrossSection([poly]).extrude(width).rotate((90,0,90)).translate((x-width/2,0,0))
def roof(x,y,w,d,z,rise):return yz([(y-d/2,z),(y+d/2,z),(y,z+rise)],x,w)
add(0,0,0,150,140,3)
# Long foreground bamboo-clad wing, opposite staggered gable pair and slim link.
add(0,-41,2.8,130,29,25.2)
parts.append(roof(0,-41,136,35,27,9))
add(-19,40,2.8,74,30,26.2)
parts.append(roof(-19,40,80,36,28,9))
add(-13,22,2.8,86,19,22.2)
parts.append(roof(-13,22,91,25,24,7))
add(55,5,2.8,15,92,23.2)
parts.append(roof(55,5,20,96,25,5).rotate((0,0,0)))
# Side link roof ridge runs lengthwise, replace prior crosswise triangle envelope.
parts.pop()
parts.append(wedge([(44,25),(66,25),(66,31),(44,26.5)],5,97))
# Distinct oblique small courtyard-facing projection, angle and depth estimated.
projection=box(0,0,2.8,34,22,22.2)+roof(0,0,40,28,24,7)
parts.append(projection.rotate((0,0,18)).translate((34,-7,0)))
# Real front has small irregularly spaced windows, not a continuous glass wall.
for x in [-55,-42,-23,-9,11,29,47,59]:cut(x,-55.5,10,5,3,7)
for x in [-45,-24,-2,19]:cut(x,7.5,8,7,3,9)
# Thickened bamboo-cladding rhythm, merged relief instead of separate stalks.
for x in range(-63,65,3):
 if any(abs(x-w)<3 for w in [-55,-42,-23,-9,11,29,47,59]):
  det(x,-55.6,3,0.9,1.2,7);det(x,-55.6,17,0.9,1.2,10)
 else:det(x,-55.6,3,0.9,1.2,24)
 det(x,-26.4,3,0.9,1.2,24)
for x in range(-53,19,3):det(x,55.1,3,0.9,1.2,25)
for y in range(-37,49,3):det(62.6,y,3,1.2,0.9,22)
# Roof ridges and broad secondary battens track visible long horizontal lines.
for y,z in [(-41,35.5),(-50,31),(-32,31)]:det(0,y,z,134,1.2,1)
for y,z in [(40,36.5),(31,32),(49,32)]:det(-19,y,z,78,1.2,1)
# Low terrace/door apron only; no underground excavation or room arrangements.
add(-14,-15,3,48,15,1.5)
# Detached demonstration granary/watch platform excluded from the building scope.
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
