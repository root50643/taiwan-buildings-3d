"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. No survey or interior data used.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, Mesh64
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
# Isolated chapel only: the tall academic building behind it is excluded.
add(0,0,0,150,130,3)
# Broad fan-like hall envelope behind a projecting central facade.
foot=[(-24,-34),(24,-34),(54,-5),(6,44),(-6,44),(-54,-5)]
parts.append(CrossSection([foot]).extrude(45).translate((0,0,2.8)))
# Upper roof band follows polygon; roof terraces are represented without invented interiors.
parts.append(CrossSection([foot]).extrude(2.0).translate((0,0,47)))
# central projecting front glass wall and heavy white vertical piers
add(0,-37,14,44,5,35)
cut(0,-39.5,16,38,3.0,31)
for x in [-20,-15,-10,10,15,20]:add(x,-40,14,2,3,36)
# central grid stays backed to wall, preserving aperture rhythm without loose thin meshes
for x in [-7,-3.5,0,3.5,7]:details.append(box(x,-40,17,1.0,3.1,29))
for z in [22,28,34,40]:details.append(box(0,-40,z,19,3.1,1))
# Flat projecting buttress caps above the slender strips.
for x in [-25,-16,16,25]:add(x,-37,48,7,11,4)
# Tall flanking piers extend to ground; recessed under-entrance is truly open.
for x in [-28,28]:add(x,-37,3,7,12,47)
cut(0,-36,4,48,10,10)
add(0,-31,4,46,1.5,9)
# Left/right broad wings: tall inset stained-glass slots and overhanging head blocks.
for side in [-1,1]:
 # Slanted annexes seen in the posted public floor-plan photograph.
 angle=-side*45
 wing=box(0,0,2.8,27,20,45).rotate((0,0,angle)).translate((side*47,-13,0))
 parts.append(wing)
 parts.append(box(0,0,41,29,22,10).rotate((0,0,angle)).translate((side*47,-13,0)))
 for y in [-6,0,6]:
  cuts.append(box(side*13.4,y,8,4,2.8,32).rotate((0,0,angle)).translate((side*47,-13,0)))
 for y in range(-8,9,4):
  parts.append(box(side*13.5,y,43,2,1.3,7).rotate((0,0,angle)).translate((side*47,-13,0)))
 # Buttresses flanking the rear apex are externally documented by floor outline.
 parts.append(box(0,0,3,8,6,43).rotate((0,0,angle)).translate((side*11,38,0)))
# Wide forecourt steps, no neighboring scenery included.
for i in range(5):add(0,-51+i*2.2,2.8,80,2.6,.7+i*.8)
# Alpha and Omega + cross are thickened structural symbols. Outer omega arch opening retained.
parts.append(profile(list(reversed([(-6,49),(0,62),(6,49),(3.8,49),(0,57),(-3.8,49)])),-32,2.2))
add(0,-32,51,1.8,2.2,12)
add(0,-32,57,6.5,2.2,1.8)
add(0,-32,51,8,2.2,1.5)
# Rear has no verified detailed photo: only the conservative envelope, no invented openings.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
