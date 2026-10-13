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
# Library: 8 levels, upper broad brick/glass bands above recessed lower colonnades.
add(0,0,0,150,91,3)
# Lower glazed body set behind freestanding facade columns.
add(0,7,2.8,126,51,40)
# Forecourt staircase, a model support for base-level colonnade.
for i in range(5):add(0,-36+i*2,2.8,127,2.4,1+i*1.2)
# Two-storey portico stays genuinely open in front of the recessed glazing.
for x in [-60,-45,-29,-14,16,32,47,60]:column(x,-26,3,1.3,29)
for z in [15,28]:add(0,-23,z,126,9,2.2)
for x in [-56,-38,-20,0,21,40,57]:
 for z in [6,18]:cut(x,-18.5,z,14,2.8,7)
# Two recessed mid levels with front gallery piers.
for z in [31,42]:
 add(0,5,z,130,62,2)
 for x in [-59,-45,-30,-15,0,15,30,45,59]:add(x,-25,z,1.6,2.6,10)
 add(0,-25,z,129,1.4,2)
add(0,10,41,125,45,12)
for x in [-54,-39,-24,24,39,54]:cut(x,-12.5,44,11,3,6)
# Side galleries are visible in the official oblique photograph.
for side in [-1,1]:
 for z in [32,44]:
  cut(side*63,8,z,8,39,8)
  for y in [-11,2,15,27]:details.append(box(side*62.8,y,z,8,1.6,8))
# Four upper stripe levels project beyond lower structural stack.
add(0,4,52,137,65,43)
for z in [55,66,77,88]:
 cut(0,-28.5,z,134,2.6,4.4)
 for x in range(-63,64,6):details.append(box(x,-28.4,z,.9,2.4,4.4))
 # both side band runs documented in the exterior side photograph
 for side in [-1,1]:cut(side*68.5,4,z,2.6,61,4.4)
# Central framed library sign is backed plaque, text too small is omitted.
add(0,-30,78,32,3.5,15)
cut(0,-32,80,28,1.7,11)
# Broad roof eave held above clerestory and top penthouse with cross.
add(0,4,94.5,133,59,5.5)
for x in range(-59,60,14):cut(x,-25.8,96,10,2.5,2.8)
add(0,4,100,141,70,2)
add(0,8,101.5,26,22,6)
add(0,8,107.1,1.8,1.8,8)
add(0,8,111.5,6.4,1.8,1.8)
# Plain rear and service volume depth are approximations; no hidden rooms.
add(54,33,3,22,20,105)
add(54,33,87,29,25,2.5)
for z in [10,24,38,52,66,80,94]:
 cut(65,33,z,3.5,14,10)
for y in [29,37]:add(65.3,y,5,1.5,1.1,96)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
