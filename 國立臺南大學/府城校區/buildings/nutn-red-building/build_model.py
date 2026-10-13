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
# Historic red building: long main wing and two rear returns around open court.
add(0,0,0,150,86,3)
add(0,-17,2.8,138,23,38)
# Rear returns and open court; no invented solid courtyard infill.
for x in [-58,58]:add(x,10,2.8,22,45,38)
# Three storeys of deeply recessed colonnade bays on principal front.
for z in [5,17,29]:
 for x in [-63,-55,-47,-19,-11,-3,5,13,21,47,55,63]:
  cut(x,-27,z,5.3,6,9)
  if z>5:
   for dx in [-1.8,0,1.8]:cut(x+dx,-27,z-2,1.05,6,1.3)
# Two entrance frames visible along the long main facade.
for ex in [-34,34]:
 add(ex,-30,3,15,5,32)
 cut(ex,-31,3,6.5,6,9)
 for dx in [-4.2,0,4.2]:cut(ex+dx,-32,16,2.4,4,14)
 add(ex,-31,34,18,6,2.5)
 for dx in [-4.2,0,4.2]:cut(ex+dx,-28,36,2.4,3,3.5)
 for i in range(3):add(ex,-35+i*1.5,2.8,21,2,1+i*.7)
# Roof hips, main ridge and cross-return ridges, not flat boxes.
hip(0,-17,40.1,142,28,7)
for x in [-58,58]:
 parts.append(CrossSection.square((26,48),center=True).extrude(7,scale_top=(.03,.72)).translate((x,10,40.1)))
add(0,-17,47,108,1.3,1.0)
# Open rear-facing corridor recesses, observed in photographs, simplified rhythm.
for z in [5,17,29]:
 for x in range(-42,43,9):cut(x,-5,z,6,5,9)
 for side in [-1,1]:
  for y in [0,11,22]:cut(side*47,y,z,4.5,7,9)
# End walls and unknown courtyard window details kept plain, not inferred rooms.


solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
