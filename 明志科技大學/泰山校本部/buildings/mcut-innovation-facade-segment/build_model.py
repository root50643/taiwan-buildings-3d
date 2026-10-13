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
# Front facade SEGMENT only, no claim to reproduce unknown building footprint/rear.
add(0,0,0,150,62,3)
# Long eight-level brick front elevation; shallow backing is explicitly a modelling cut.
add(0,9,2.8,138,29,109)
# Deep tall central entry/gallery recess, side masses and connecting top lintel retained.
cut(0,-3,3,62,30,96)
# Inner gallery and tower added after the main recess cut.
maincut=cuts.pop()
parts[-1]=parts[-1]-maincut
# Inner gallery floor bands visible beside center glazing, against rear backing.
for z in [15,28,41,54,67,80,93]:
 add(0,8,z,62,12,1.8)
 add(0,2,z+1.5,62,1.1,3.3)
# Forward faceted glass tower on ground-level round pillars; photograph has gently folded front.
poly=[(-19,-9),(-9,-11),(9,-11),(19,-9),(19,8),(-19,8)]
parts.append(CrossSection([poly]).extrude(86).translate((0,0,13)))
for x in [-15,0,15]:column(x,-4,3,1.8,11)
# Seven tall glazed rows with robust backed mullions.
for z in [16,28,40,52,64,76,88]:
 cut(0,-11,z,36,3,8.5)
 for x in [-15,-10,-5,0,5,10,15]:details.append(box(x,-11,z,1.0,3.2,8.5))
# Side square-window groups and continuous heads (eight storeys).
for z in [7,20,33,46,59,72,85,100]:
 for sign in [-1,1]:
  for xx in [39,46,53,60]:cut(sign*xx,-5.5,z,3.9,3.2,4.8)
  add(sign*49.5,-6.2,z+5.0,30,2.5,1.1)
# Narrow windows across top above open central frame.
for x in [-26,-16,-6,4,14,24]:cut(x,-5.5,101,3.9,3.2,4.8)
# Back is a flat sectional end, not an invented rear facade.
for i in range(4):add(0,-29+i*1.5,2.8,49,1.7,.5+i*.6)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
