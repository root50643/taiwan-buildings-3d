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
# Schutte Memorial Building. 2025 oblique photo reveals two facade systems.
add(0,0,0,150,110,3)
add(-9,7,2.8,101,60,116)
# Long glazed elevation: three bays with six repeating window strips.
for x in [-43,-9,25]:
 cut(x,-23,6,28,3.4,108)
 for z in [8,27,46,65,84,103]:
  # Tall window mullions and horizontal transoms remain integral with backing.
  for dx in [-11,-7,-3,1,5,9]:details.append(box(x+dx,-23.3,z,1.1,3.4,10))
  details.append(box(x,-23.3,z+10,28,3.4,1.2))
  # Backed opaque spandrel, not invisible texture.
  details.append(box(x,-23.1,z+12,28,3.4,5.5))
# Two dark slender piers flare into broad inverted-triangle capitals at roof.
for x in [-26,8]:
 add(x,-23.7,4,4,3.8,101)
 parts.append(profile([(x-2,103),(x+2,103),(x+6,115),(x-6,115)],-23.5,4))
add(-9,-23,114,103,5,5)
# Right side: rough stone wall flanks a tall glazed stair bay.
cut(41.5,7,23,4,29,89)
for y in [-6,0,6,12,18]:details.append(box(41.9,y,24,3.5,1.0,86))
for z in range(25,110,10):details.append(box(41.9,7,z,3.5,29,1.0))
# White strong upright edges and three projecting opaque stair panels.
for y in [-10,24]:add(42.0,y,20,5,5,100)
for z in [36,64,92]:add(44.5,7,z,8,12,10)
# Low entrance/theatre wing along the short elevation, white flat deep fascia.
add(47,5,2.8,20,75,17)
cut(57,5,5,3.4,68,11)
for y in range(-26,39,8):details.append(box(57.3,y,5,3.4,1.2,11))
add(47,5,18,24,79,3)
# 2026 theatre vestibule: glass door set behind projecting side canopy and framed jamb.
add(59,-21,3,6,23,16)
cut(62,-21,5,3.1,19,11)
for y in [-29,-21,-13]:details.append(box(62.3,y,5,3.1,1.2,11))
for i in range(4):add(66+i*1.5,-21,2.8,2.0,25,.7+(3-i)*.8)
# Rooftop utility core and low perimeter edge; thin rail is generalized to solid rim.
add(-22,15,118,26,22,9)
add(-9,7,118.3,104,63,1.7)
# Rear unseen fenestration omitted, depth conservatively estimated from observed side.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
