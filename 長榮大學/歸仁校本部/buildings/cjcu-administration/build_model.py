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
# Six-level administration mass; front is long public approach elevation.
add(0,0,0,150,87,3)
add(0,4,2.8,130,48,64)
# Four red-brick upper levels with asymmetric groups, above a ground-level entrance.
for z in [17,28,39,50]:
 for x in [-57,-48,-39,24,33,42,51,60]:cut(x,-20,z,4.5,2.6,5.8)
# Central two-storey tall grouped glazing and upper broad inset.
for z in [17,28]:
 for x in [-21,-8,5]:cut(x,-20,z,10,2.8,7.5)
for x in [-20,-5,10]:cut(x,-20,41,11,2.7,5.5)
for x in [-28,15]:add(x,-20.6,15,1.7,1.7,32)
# Thin vertical recess at right of middle window composition.
cut(20,-20,18,2.2,3,29)
# White upper glazed storey, closely spaced mullions, horizontal sunscreen.
cut(0,-20,57,125,2.8,8)
for x in range(-60,61,8):details.append(box(x,-20.4,57,1.1,2.8,8))
for z in [58,61,64]:details.append(box(0,-21, z,125,1.5,1.0))
add(0,4,66,132,50,1.6)
# Right end documented in official oblique photograph: regular windows and two tall slots.
for z in [18,29,40,51]:
 for y in [-12,-3,6,15,24]:cut(65,y,z,2.6,4.4,5.8)
for y in [0,18]:cut(64,y,17,9.0,7.2,22)
cut(65,4,58,3,45,7)
for y in range(-17,27,7):details.append(box(65, y,58,2.6,1.0,7))
# Rooftop room and rear-end stone stair/cross tower, seen in contractor photograph.
add(12,8,67.3,41,24,8)
add(-53,13,2.9,18,31,75)
add(-53,13,77.5,2.2,2.2,9)
add(-53,13,82.4,10,2.2,2.2)
# Rear elevation seen in contractor view: repeated windows beneath broad upper glazing.
for z in [17,28,39,50]:
 for x in [-33,-22,-11,0,11,22,33,44,55]:cut(x,28,z,5.4,2.8,6)
cut(10,28,57,102,3,8)
for x in range(-37,59,8):details.append(box(x,28.4,57,1.1,2.8,8))
for z in [58,61,64]:details.append(box(10,29,z,102,1.5,1.0))
# Rear attached low arched walkway; its depth and far rear openings are approximate.
add(4,30,2.8,105,10,12)
for x in [-39,-24,-9,6,21,36,49]:arch_cut(x,30,3,8,9,13)
add(4,30,14.2,108,12,1.5)
# Shallow front entrance bays and canopy; preserve actual lower entrance recess.
for x in [-36,-12,12,36]:cut(x,-20,3,16,5,9)
add(0,-22,12,98,11,1.8)
for x in [-46,46]:add(x,-25,3,2.2,2.2,10)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
