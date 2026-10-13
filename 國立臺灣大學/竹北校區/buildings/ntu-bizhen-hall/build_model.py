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
# 碧禎館 exterior, official 2015 report photos from four public viewpoints.
add(0,0,0,150,73,3)
add(0,0,2.8,140,48,82)
add(0,0,84,143,51,2)
# Two solid end blades around a recessed vertical glazed slot.
x=-70
cut(x,0,10,4,12,71)
for z in range(12,82,12):details.append(box(x,0,z,2.8,12,1.2))
# One clock observed on the solid blade; other end has taller glazing instead.
details.append(Manifold.cylinder(1.3,2.6,2.6,circular_segments=32).rotate((0,90,0)).translate((-70.6,-13,76)))
cut(70,8,10,4,22,72)
for y in [0,8,16]:details.append(box(70,y,10,2.8,1.2,72))
for z in range(12,82,12):details.append(box(70,8,z,2.8,22,1.2))
# Long wall faces: three small-window bands plus top recessed balcony band.
for y in [-24,24]:
 for x in [-62,-54,-46,-38,-30,-22,-14,-6,2,10,18,26,34,42,50,58,66]:
  for z in [35,47,59]:cut(x,y,z,4.8,2.8,3)
 # top bays retain heavy fascia and piers, not a hollow inner balcony cavity.
 for x in [-61,-46,-31,-16,-1,14,29,44,59]:cut(x,y,73,12,4,7)
 # off-centre glazed stair strip and three small balconies.
 if y<0:
  cut(-21,y,18,9,4,52)
  for z in [23,35,47,59]:
   details.append(box(-21,y,z,9,2.8,1.2))
   details.append(box(-21,y+(1 if y>0 else -1)*2,z,11,5,1.2))
  details.append(box(-21,y,18,1,2.8,52))
 # Ground-floor glazing/pilotis indicated as shallow backed recesses.
 for x in [-60,-46,-7,9,25,41,57]:cut(x,y,7,10,4,15)
# Lifted end zone is publicly visible, approximated as solid-backed open bays.
for x in [-70,70]:
 for y in [-15,15]:cut(x,y,4,5,8,10)
# Simple roof plant enclosure visible in official broadside photograph, not equipment.
add(-24,3,85,24,19,10)
# Public external ground levels vary; terrain and ramp retaining wall omitted.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
# Match the approximately 2.2:1 broad elevation in the official report.
solid=solid.scale((1,1,.75))
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
