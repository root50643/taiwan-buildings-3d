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
# N74 front facade, cross-checked with official CLD front/oblique images.
add(0,0,0,150,94,3)
add(0,6,2.8,136,53,80)
add(0,6,82,138,55,1.5)
for z in [20,40,60]:add(0,-20.8,z,137,2,3.5)
# Center has two narrow windows on intermediate levels and two wide top windows.
for z in [25,45]:
 for x in [-9,9]:cut(x,-20.5,z,4.5,3,12)
for x in [-8,8]:
 cut(x,-20.5,65,11,3,12)
 details.append(box(x,-19.6,65,1,2,12))
 details.append(box(x,-19.6,73,10.6,2,.9))
# Distinct deep upper balcony-like recesses flanking the central top pair.
for x in [-31,31]:
 cut(x,-20.5,63,17,9,16)
 add(x,-21,62,18,2,2)
# Alternating narrow side windows and broader end glazing, not a uniform window grid.
for z in [5,25,45]:
 for x in [-60,-45,-31,31,45,60]:
  cut(x,-20.5,z,6,3,12)
  details.append(box(x,-19.6,z+8,5.6,2,.9))
for x in [-60,60]:
 cut(x,-20.5,65,9,3,12)
 details.append(box(x,-19.6,65,1,2,12))
for x in [-48,48]:cut(x,-20.5,65,6,3,12)
# Vertical concrete-like strips and explicit notch at the center of the high fascia.
for x in [-68,-52,-20,0,20,52,68]:add(x,-20.7,3,1.4,1.8,79)
cut(0,-20.5,78,1.8,3.5,7)
# Shallow arched entrance beam beneath a flat rectangular portico.
cut(0,-20.5,3,29,3,19)
for x in [-10,-5,5,10]:details.append(box(x,-19.6,3,1,2,19))
add(0,-29,25,50,21,3.5)
for x in [-21,21]:add(x,-35,3,5,5,23)
add(0,-35,20,46,4.5,7)
poly=[(-17,3),(17,3),(17,21)]+[(float(x),21+3.5*(1-(x/17)**2))for x in np.linspace(17,-17,31)[1:]]
cuts.append(profile(poly,-35,6))
step(0,-43,39,5)
# Unseen ends and reverse remain plain; ivy and neighboring high-rise are omitted.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
