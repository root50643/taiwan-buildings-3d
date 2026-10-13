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
# S22 vicinity: separate historic specimen cottage, not the multi-storey department front.
add(0,0,0,150,76,3)
add(-6,0,2.8,108,47,5)
add(-6,0,7,108,45,26)
parts.append(profile([(-26,32),(26,32),(0,47)],6,113).rotate((0,0,90)))
# Externally visible long side is mostly blind, divided by shallow wall pilasters.
for x in [-59,-40,-21,-2,17,36,47]:add(x,-22.6,7,1.4,1.8,26)
for y in [-22.7,22.7]:add(-6,y,6.8,108,1.2,1.3)
# End gable pentagonal windows on both documented ends; all openings are backed relief.
for x in [-62.5,50.5]:
 poly=[(-6,35),(6,35),(6,41),(0,44),(-6,41)]
 cuts.append(profile(poly,-x,3).rotate((0,0,90)))
 details.append(box(x,0,35,3.6,1,8))
 for y in [-4,4]:details.append(box(x,y,35,3.6,.9,6))
 details.append(box(x,0,39,3.6,11,.9))
# Rear end has two tall rectangular recesses, shallow horizontal eyebrow hoods.
for y in [-13,13]:
 cut(-60,y,10,3,11,17)
 add(-61,y,27,5,15,1.8)
# Five ridge ventilators seen in official and current public external photos.
for x in [-44,-23,-2,19,40]:
 add(x,0,44.5,5.8,5.8,3.5)
 column(x,0,47.5,2.25,4.6)
 column(x,0,49.2,2.7,1)
 column(x,0,52,2.8,1.4)
# Glazed front vestibule represented as solid volume with recessed glass and thick frames.
add(60,0,2.8,26,45,26)
add(60,0,29,29,48,1.8)
for y in [-22.5,22.5]:
 for x in [53,64]:cut(x,y,9,8,2.8,17)
 for x in [48,58.5,72.5]:add(x,y,3,1.5,1.6,27)
 add(60,y,7,26,1.7,1.5)
for y in [-14,0,14]:cut(73,y,9,3,11,17)
for y in [-21,-7,7,21]:add(73,y,3,1.6,1.5,27)
# Hidden long reverse face and small equipment deliberately not invented.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
