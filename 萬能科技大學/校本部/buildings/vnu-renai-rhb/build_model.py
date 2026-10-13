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
# Five-storey dormitory: four tall lower window rows and a fifth short top rank.
add(0,0,0,150,72,3)
add(0,5,2.8,136,44,69)
# Broad offset stair bay interrupts otherwise narrow vertical windows.
for z in [8,21,34,47]:
 for x in range(-61,65,9):
  if 14<x<36:continue
  cut(x,-17,z,3.7,3.2,7)
  add(x,-18,z+7,5.4,2.2,1.2)
 cut(24,-17,z+2,18,3.2,3.3)
 for x in [20,28]:details.append(box(x,-17,z+2,1.2,3.4,3.3))
# Substantial full-height light piers and top horizontal band are distinctive.
for x in range(-67,69,9):add(x,-17.8,3,1.4,1.6,56)
add(0,-17.8,58,137,1.6,2)
for x in range(-61,65,9):cut(x,-17,63,3.8,3.2,4)
# Right end: banners are omitted but the central window stack remains.
for z in [18,31,44]:cut(68,4,z,3.2,5,7)
for y in [-8,20]:cut(68,y,63,3.2,4,4)
add(0,5,71,139,47,1.4)
# Ground and rear screened by trees/not photographed: no invented entries or rear windows.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
