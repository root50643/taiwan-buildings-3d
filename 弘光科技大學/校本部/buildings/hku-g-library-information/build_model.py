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
# G Library front block, tall rear teaching volume and narrow stair tower.
# Front facade verified by official 2025 image and Commons photo taken 2013-02-26.
add(0,0,0,150,103,3)
# Raised library terrace, broad exterior staircase.
add(0,5,2.8,131,66,8)
for i in range(8):add(9,-43+i*2,2.8,99,2.3,1*(i+1))
# Three-level lower library block with stepped left end.
add(3,1,10,122,45,42)
add(-52,-3,10,23,49,43)
# Right slender vertical stair/service tower rises alongside the library.
add(64,16,2.8,12,48,92)
# Higher rear volume is set well back, with two visible classroom rows over roof.
add(0,26,10,119,21,81)
# entrance is materially recessed under lintel.
cut(11,-22,10,51,8,11)
for x in [-10,9,28]:details.append(box(x,-23,10,2,3,11))
# second-level broad windows and regular broad sunshade fins.
for x in range(-32,58,10):cut(x,-21.5,26,8,4,8)
for x in [-33,-13,7,27,47]:add(x,-24,34,1.8,6,4)
add(9,-24,36.5,102,5.5,1.8)
# Signature tall thin clerestory band: closely spaced solid white fins over glazing.
cut(9,-21.6,41,103,4,7)
for x in range(-42,62,4):details.append(box(x,-22.6,41,1.15,5.0,7))
add(9,-24,48,104,5.5,1.5)
# Left block has two column-like window pairs and deep small eaves.
for z in [15,27,40]:
 for x in [-59,-51,-43]:cut(x,-27.5,z,4.1,3.5,7)
 add(-51,-29,z+6.5,23,4,1.6)
# Receding red upper levels: pairs of vertical openings.
for z in [64,78]:
 for x in range(-51,58,12):
  for dx in [-2.7,2.7]:cut(x+dx,15.5,z,3.5,4,9)
# Long red sloped roof-canopy above library; front/side actual mass is retained.
parts.append(profile([(-60,53),(60,53),(60,57),(-60,57)],12,32))
add(0,8,56.5,123,36,2)
for z in [15,27,39,51,63,75,87]:cut(64,-8,z,3.4,4,5)
add(0,26,90.5,122,23,2)
# Roof/rear depths and unseen far flank are explicitly estimated.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
