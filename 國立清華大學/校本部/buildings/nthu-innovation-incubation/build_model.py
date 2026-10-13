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
# Original miniature of incubator only, excluding neighbouring lab and TSMC.
def yz(poly,x,width):
 return CrossSection([poly]).extrude(width).rotate((90,0,90)).translate((x-width/2,0,0))
add(0,0,0,150,140,3)
# Tall road-side main wing and low lake-facing fore-wing around exterior courtyard.
add(0,32,2.8,126,32,99.2)
add(-55,-4,2.8,16,72,32.2)
add(55,-4,2.8,16,72,32.2)
add(0,-38,2.8,126,28,11.2)
parts.append(yz([(-49,14),(-22,14),(-22,36),(-58,36)],0,126))
# Recessed outward-sloping lake facade; robust sloped mullions.
cuts.append(yz([(-51,16),(-48,16),(-56,35),(-60,35)],0,121))
for x in range(-59,62,7):
 details.append(yz([(-50,14),(-48,14),(-57,36),(-59,36)],x,1.4))
add(0,-39,35,132,44,2.2)
# Ground-floor window recess and columns under the fore-wing projection.
cut(0,-52,5,119,4,6)
for x in range(-58,61,10):det(x,-52,3,2,4.5,10)
# Upper main wing has a large inset curtain wall facing court, deep outer brick frame.
cut(0,16,41,118,4,56)
for z in [42,51,60,69,78,87,96]:det(0,16,z,118,4.5,1.7)
for x in range(-57,60,6):det(x,16,41,1.2,4.5,56)
# Road elevation: six rows of strongly projecting vertical white fins, not flat windows.
for z in [42,52,62,72,82,92]:
 cut(0,48,z,118,4,6.5)
 for x in range(-57,60,5):
  det(x,49,z,1.4,6,6.5)
# Road-side lower double-height screen and glazed ground storey.
cut(0,48,15,120,4,20)
for j,x in enumerate(range(-58,61,4)):
 det(x,49,15+(j%3)*2,1.3,6,20-(j%3)*2)
cut(0,48,5,118,3,6)
for x in range(-57,60,9):det(x,48,5,1.4,3.5,6)
# Roof parapet/outer frame is deliberately thick and equipment-free.
add(0,32,101,130,35,2)
for x in [-63,63]:
 for y in [16,48]:det(x,y,38,2.5,3,65)
# Side solid brick end has a narrow three-part vertical recess.
for z in [43,54,65,76,87]:cut(63,31,z,3,3.8,8)
# Low end facades with staggered vertical shading blades.
for side in [-1,1]:
 cut(side*63,-35,15,3,22,18)
 for j,y in enumerate(range(-49,-23,4)):
  det(side*64,y,15+(j%3)*2,4,1.5,18-(j%3)*2)
# Public court is kept open; partial slender crossing canopy intentionally omitted.
# Unphotographed boundary details and rear lower ground are simplified.
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
