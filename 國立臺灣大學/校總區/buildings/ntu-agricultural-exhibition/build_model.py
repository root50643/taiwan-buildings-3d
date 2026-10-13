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
# Three-storey rectangular hall with the characteristic circular-tile screens.
add(0,0,0,150,64,3)
add(0,5,2.8,138,44,39)
# Recessed ground-floor gallery. Backing retained; no interior rooms represented.
cut(0,-16,3,131,5,10.5)
for x in [-66,-52.8,-39.6,-26.4,-13.2,0,13.2,26.4,39.6,52.8,66]:
 details.append(box(x,-18,3,2.2,3.5,11))
# Two rows of screen panels; circular tiles represented as enlarged shallow dimples.
# Exact tile count/color and stagger pattern deliberately simplified for 0.4mm nozzle.
for floor in [15,28]:
 for bay in range(10):
  center=-62.1+13.8*bay
  for row in range(4):
   for col in range(4):
    x=center-4.6+col*3.05;z=floor+1.6+row*2.6
    cuts.append(Manifold.cylinder(1.8,.86,.86,circular_segments=16).rotate((90,0,0)).translate((x,-16.0,z)))
for z in [13,26.4,40]:add(0,-17.4,z,140,2,1.7)
for x in [-69,-55.2,-41.4,-27.6,-13.8,0,13.8,27.6,41.4,55.2,69]:add(x,-17.7,14,1.2,1.5,26)
# Public entrance glass band represented as backed shallow recesses.
for x in [-57,-44,-31,-18,-5,8,21,34,47,60]:cut(x,-13.7,4,9,1.6,7.5)
step(0,-24,47,n=4)
add(0,5,41,140,46,1.3)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
