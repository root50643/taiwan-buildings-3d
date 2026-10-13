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
# E1: four-storey teaching hall, NOT animal hospital or veterinary hall three.
add(0,0,0,150,82,3)
add(0,5,2.8,136,48,61)
add(0,5,63,138,50,1.5)
# Central stepped parapet, very shallow curved cap as visible in front photograph.
poly=[(-24,63),(-24,66),(-16,66),(-16,70),(-8,71),(0,71.5),(8,71),(16,70),(16,66),(24,66),(24,63)]
parts.append(profile(list(reversed(poly)),-18.5,3))
# Four main window rows; paired narrow openings and regular structural bands.
for x in [-56,-34,34,56]:
 for z in [7,22,37,52]:
  for xx in [x-3.7,x+3.7]:
   cut(xx,-19,z,5.5,2.5,8.5)
   details.append(box(xx,-18.7,z+4.5,5.5,1.7,.9))
for x in [-21,21]:
 for z in [7,22,37,52]:cut(x,-19,z,5,2.5,8.5)
for z in [18,33,48,62]:add(0,-19.3,z,136,1.5,2)
# Central landing windows are staggered between the main levels.
for z in [17,32,47]:
 cut(0,-19,z,22,2.5,4.8)
 for x in [-7,0,7]:details.append(box(x,-18.7,z,.9,1.7,4.8))
cut(0,-19,3.5,19,3,10)
add(0,-21,13,27,7,1.6)
for x in [-13,13]:add(x,-19.7,3,1.3,2,63)
step(0,-30,30,4)
# Right side visible publicly: three vertical window groups per floor.
for y in [-12,4,20]:
 for z in [7,22,37,52]:
  cut(68,y,z,2.5,8,8.5)
  details.append(box(67.7,y,z+4.5,1.7,8,.9))
# Rear and left later additions unconfirmed; deliberately plain/excluded.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
