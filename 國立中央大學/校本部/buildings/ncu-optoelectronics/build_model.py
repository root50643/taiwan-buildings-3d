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
# U-shaped deep-frame envelope, elevated entrance bridge and sloping open roof screen.
add(0,0,0,150,136,3)
for x in [-48,48]:add(x,3,2.8,22,110,74)
add(0,47,2.8,118,22,74)
# Elevated front volume frames the large open passage, with columns through the opening.
add(0,-41,38,76,17,38.8)
for x in [-22,0,22]:add(x,-42,3,2.4,5,35.1)
# Internal right-angle connection/walkway seen through entrance; rear courtyard stays open sky.
add(0,34,20,76,7,2.5)
# Outer grid recesses on BOTH flanks, from actual side/back contractor photographs.
for side in [-1,1]:
 for y in range(-41,43,12):
  for z in [8,21,34,47,60]:cut(side*59,y,z,16,10.5,11)
# Back grid is partially supported by corner photo; simplify unseen middle plain.
for x in range(-48,49,12):
 for z in [13,28,43,58]:cut(x,58,z,10.5,12,12)
# Glass entrance screen represented as recessed panels with thick framing, not texture.
for x in range(-31,32,9):
 for z in [43,54,65]:cut(x,-49, z,7.2,2.8,8)
for side in [-1,1]:
 for z in range(7,72,9):cut(side*47,-51,z,16,3,6.8)
# Raised front portals and long open roof screen. 1.5mm beam sections for printability.
for x in [-59,59]:add(x,-51,3,2.6,3,80)
# Roof shade grid slopes slightly towards the inner court, as a coarse approximation.
for x in range(-57,58,9):
 beam=profile([(-54,80),(-20,76),(-20,77.8),(-54,81.8)],0,1.5).rotate((0,0,90)).translate((x,0,0))
 # construct exact y-z profile with rotated x-z prism; x reflection is handled by symmetric ends.
 details.append(beam)
# Connect every longitudinal beam to supporting front and rear headers.
add(0,-54,80,120,2,2)
add(0,-20,76,120,2,2)
for y in [-45,-36,-27]:
 z=80-(y+54)*4/34
 details.append(box(0,y,z,120,1.5,1.8))
step(0,-61,102,4)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
