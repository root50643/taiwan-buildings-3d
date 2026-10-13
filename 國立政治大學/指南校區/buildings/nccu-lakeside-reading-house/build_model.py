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

def prism(poly,z,h):return CrossSection([poly]).extrude(h).translate((0,0,z))
def rotated_box(x,y,z,w,d,h,deg):return box(0,0,0,w,d,h).rotate((0,0,deg)).translate((x,y,z))
# Independent two-storey reading house; full footprint, no adjacent main tower or invented bridge.
add(0,0,0,150,106,3)
# Open raised undercroft preserves lake-side pavilion character.
for x in [-53,0,53]:
 for y in [-24,24]:add(x,y,2.8,4.8,4.8,9)
# Rear service/stair wall is part of the building, not an enclosing fill beneath the house.
add(0,32,2.8,120,8,54)
add(0,0,10,132,82,3)
add(0,0,34,132,82,3)
# Inset glazing mass at each of the two levels, leaving balcony recesses.
for z in [12.8,36.8]:
 add(0,0,z,122,68,22)
 for x in range(-55,60,10):
  cut(x,-34,z+1.3,8.5,3.6,18)
  details.append(box(x,-34.5,z+9,8.5,2.4,1.1))
 for side in [-1,1]:
  for y in [-26,-15,-4,7,18,29]:
   cut(side*61,y,z+1.3,3.6,9.4,18)
   details.append(box(side*61.5,y,z+9,2.4,9.4,1.1))
 # Broad three-sided frame columns and balcony rail backed by deck.
 for x in [-64,64]:add(x,-38,z-.5,2.8,2.8,23)
 add(0,-40,z-.7,132,1.4,3.8)
 for side in [-1,1]:add(side*65,0,z-.7,1.4,82,3.8)
# Oversailing roof slab; upper pavilion has a striking folded fascia dropping at the rear.
add(0,-1,58.3,137,85,2.5)
for side in [1]:
 # Side silhouette slopes down behind the pavilion, retained as a substantial attached fold.
 p=prism([(-1.8,-40),(1.8,-40),(1.8,43),(-1.8,43)],0,1) if False else None
 parts.append(profile([(-43,58.5),(43,58.5),(43,38),(37,39),(30,54.8),(-43,57)][::-1],0,3.2).rotate((0,0,90)).translate((side*66,0,0)))
# Service-side photographs establish mixed solid core, glazed entrance and open upper walkway.
for z in [15,39]:
 cut(-20,36,z,15,4,6)
 cut(4,36,z,9,4,6)
 cut(35,36,z-2,25,4.5,17)
 for x in [28,36,44]:details.append(box(x,35.3,z-2,1.3,3,17))
# Exterior staircase rises along the service-side flank, fused into the side wall and base.
for i in range(18):add(-66,-27+i*3.4,2.8,10,3.8,1.7*(i+1))
add(-64,32,33,12,11,3)
# Low rear approach platform reaches base; no detached handrails or paper-thin posts.
add(0,43,2.8,45,10,8)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
