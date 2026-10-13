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
# H: five-storey student activities/first dormitory building, not duplicate facilities.
add(0,0,0,150,86,3)
add(0,10,2.8,135,44,49)
# Three window fields separated by two raised glass stair strips.
for z in [7,17,27,37,47]:
 for x,w in [(-51,27),(-7,40),(43,38)]:
  cut(x,-12,z,w,3.8,5.4)
  for xx in ([] if z==7 and x==-7 else np.arange(x-w/2+5,x+w/2,7)):details.append(box(float(xx),-12,z,1.1,4.0,5.4))
for z in [14,24,34,44,52]:add(0,-13,z,135,3.7,2.3)
# Stair towers run uninterrupted beyond roof; distinctive two vertical strips.
for x in [-31,20]:
 add(x,-12,2.8,9,9,54)
 cut(x,-16.5,4,4.3,3.2,50)
 for z in range(6,55,7):details.append(box(x,-16,z,4.5,2.8,1.1))
 add(x,-11,56,12,12,1.8)
# Solid end wall projects above roof, roof service head observed at right.
add(65,9,3,7,45,55)
add(56,19,51,22,19,6)
# Central entry recedes behind the projecting upper floor.
cut(-5,-11,3,23,8,11)
for x in [-16,6]:details.append(box(x,-14,3,2.6,4,12))
add(-5,-16,13.6,28,9,1.5)
step(-5,-24,27,3)
# I food-processing/autonomous-learning attachment is separately coded in map; omitted here.
# Back is unsurveyed and deliberately plain; perimeter depth is an approximate envelope.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
