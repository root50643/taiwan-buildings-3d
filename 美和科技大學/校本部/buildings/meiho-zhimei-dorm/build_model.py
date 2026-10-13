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
# Zhimei dormitory: observed main court facade, partial left return and corner towers.
add(0,0,0,150,111,3)
add(12,23,2.8,111,34,104)
# Left return length is deliberately approximate; photograph only shows part of the wing.
add(-51,-3,2.8,26,83,104)
# Seven stacked residential rows of deep balcony pockets along the main courtyard front.
for z in range(15,100,13):
 for x in range(-33,60,15):
  cut(x,6,z,11,7,10)
  details.append(box(x,3.5,z-.8,12,6,1.6))
  details.append(box(x,3.1,z+.2,6,1.4,4.8))
  # Adjacent tall window relief visible behind partial balcony wall.
  cut(x+3,8,z+2,3,2.5,6)
# Ground floor entry and canopy, source second exterior photo verifies entrance steps.
for x in [-25,-5,15,35,55]:cut(x,6,5,13,6,8)
add(11,0,14,115,16,2)
for x in [-34,59]:add(x,-5,3,2.4,2.4,11)
# Left inward return with same seen deep room bays; far hidden exterior remains plain.
for z in range(15,100,13):
 for y in [-34,-17]:
  cut(-38,y,z,5,12,10)
  details.append(box(-36.5,y,z-.8,5,13,1.6))
  details.append(box(-36,y,z,1.4,6,4.8))
# Rounded glazed stair at inside corner, and signature raised flat corner finials.
parts.append(Manifold.cylinder(108,7,7,circular_segments=48).translate((-36,1,3)))
for z in range(11,106,10):
 ring=Manifold.cylinder(5.5,7.3,7.3,circular_segments=48)-Manifold.cylinder(5.7,5.7,5.7,circular_segments=48)
 cuts.append(ring.translate((-36,1,z))^box(-33,-5,z,14,10,5.5))
# Stair shell is solid-backed; ribs merge into remaining core.
add(-36,1,108,16,18,4)
for x,y in [(65,23),(-51,-36)]:
 add(x,y,106,7,12,12)
 add(x,y,117,10,15,2)
add(12,23,106,114,37,2)
add(-51,-3,106,29,85,2)
step(10,-16,50,4)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
