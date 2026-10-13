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
# Siwei Hall: long-span two-storey auditorium, not an ordinary classroom bar.
add(0,0,0,88,150,3)
add(0,0,2.8,66,132,40)
# Central projecting entrance and tall upper window frame.
add(0,-67,2.8,30,8,42)
cut(0,-71,4,26,5,10)
for x in [-9,0,9]:
 cut(x,-71,19,7,3.2,16)
 for z in [23,28,32]:details.append(box(x,-71.2,z,7,2.5,1.1))
add(0,-70.8,15.0,35,6.5,1.8)
# Low side window banks on main facade.
for x in [-26,26]:
 cut(x,-66,6,10,3,7)
 cut(x,-66,22,10,3,13)
 for z in [26,30]:details.append(box(x,-66.2,z,10,2.3,1.1))
 add(x,-67,17,12,3,1.3)
# Long elevations retain the deep vertical structural bays.
for side in [-1,1]:
 for y in [-52,-30,-8,14,36,58]:
  add(side*33,y,3,2.6,3.4,40)
 for y in [-41,-19,3,25,47]:
  cut(side*33,y,20,3.3,12,15)
  for z in [24,29]:details.append(box(side*33.4,y,z,2.6,12,1.1))
 # Entrance canopy midway on each long side.
 add(side*36,10,13,8,18,1.7)
 cut(side*33,10,3,3,11,9)
# Roof is a conservative shallow long-span cover, without unseen equipment.
add(0,0,42.3,69,135,1.5)
# The high main frontage screens the shallow roof slope.
gable(0,0,43.3,68,132,2.5)
add(0,64,2.8,70,8,17)
# Plain rear stage/service elevation, shape constrained by official footprint.
step(0,-74,29,3)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
