"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. No survey or interior data used.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def gable(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x,z+h)],y,d))
def arch(x,y,z,w,h,depth):
 r=w/2; spring=z+h-r
 pts=[(x-r,z),(x+r,z),(x+r,spring)]
 pts += [(x+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,25)[1:]]
 return profile(pts,y,depth)
def arch_cut(x,y,z,w,h,depth):cuts.append(arch(x,y,z,w,h,depth))
def arch_trim(x,y,z,w,h):
 # Backed relief ring, fused into the wall, not a separate floating shell.
 details.append(arch(x,y,z,w+1.7,h+.85,1.7)-arch(x,y-.1,z-.2,w,h+.2,2.3))
def hip(x,y,z,w,d,h):parts.append(CrossSection.square((w,d),center=True).extrude(h,scale_top=(.72,.03)).translate((x,y,z)))
def column(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
def step(x,y,w,n=3):
 for i in range(n):add(x,y+i*1.4,2.8,w,1.7,.7*(i+1))
# Sixteen-storey tower, hipped/gabled glass crown and curved upper oriel.
# Height, not base width, is the independently scaled longest dimension (150mm).
add(0,0,0,102,86,3)
add(0,6,2.8,69,49,130)
# Tall stepped side channels, visible on side photo, left open to exterior.
for side in [-1,1]:
 cut(side*34.5,6,11,5,8,111)
 # outermost narrow glazed slot remains a shallow recess in the side plane
 for z in range(19,121,8):
  for y in [-12,-2,14,24]:cut(side*34.5,y,z,2.5,5.5,5.5)
 for z in [128,132]:cut(side*34.5,6,z,1.3,48,.9)
 for y in [-12,-5,2,9,16,23]:cut(side*34.5,y,124,1.3,.9,11)
# Main front brick-window field, 6 bays x 11 rows and robust mullions.
for z in range(23,112,8):
 for x in [-25,-15,-5,5,15,25]:
  if z>=110 and abs(x)<11:continue
  cut(x,-18.5,z,5.4,2.8,5.2)
  details.append(box(x,-18.5,z,.9,3.0,5.2))
# The bottom three levels have heavy pale frame and sheltered central entry.
for z in [7,15]:
 for x in [-25,-15,-5,5,15,25]:cut(x,-18.5,z,5.5,3.0,5)
cut(0,-18.5,3,14,5,10)
add(0,-23,12.5,21,11,1.6)
for i in range(5):add(0,-34+i*2,2.8,25,2.3,.8+i*.7)
# Upper glass cap follows a true triangular gable silhouette.
parts.append(profile([(-34.5,127),(-34.5,135),(0,144.5),(34.5,135),(34.5,127)][::-1],6,49))
# Curtain-wall grid is shallow engraved relief, with no invented internal glass void.
for z in [128,132,136,140]:
 if z<134:
  for x in [-23,23]:cut(x,-18.5,z,22,1.3,.9)
 else:cut(0,-18.5,z,68,1.3,.9)
for x in range(-30,31,5):
 z=134 if abs(x)<11 else 123
 cut(x,-18.5,z,.9,1.3,141-z)
# Centre curved projecting bay extends down from glass cap.
bay=Manifold.cylinder(24,10,10,circular_segments=80).translate((0,-15,110))
parts.append(bay)
for z in [113,117,121,125,129,133]:
 ring=Manifold.cylinder(1.1,10.6,10.6,circular_segments=80)-Manifold.cylinder(1.3,9.0,9.0,circular_segments=80).translate((0,0,-.1))
 details.append(ring.translate((0,-15,z)))
# Backed round motif at centre of gable and cross on top ridge.
cuts.append(Manifold.cylinder(1.8,2.9,2.9,circular_segments=40).rotate((90,0,0)).translate((0,-18.0,139)))
add(0,6,143.8,1.5,1.5,6.2)
add(0,6,147.5,5.6,1.5,1.5)
# Rear brick window fields limited to observed side photo; rear face otherwise plain.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
