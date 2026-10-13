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
# Seven-storey L-shaped court, taller end screen and stepped inner balconies.
add(0,0,0,150,144,3)
add(-12,43,2.8,105,26,98)
add(43,-2,2.8,28,116,91)
# Tall left terminal wall and perforated upper parapet.
add(-61,43,2.8,8,28,105)
add(-15,43,100,89,26,8)
for x in [-42,-24,-6,12]:cut(x,43,102,13,30,3.6)
# Front face of rear bar: six main rows over recessed ground level.
for x in [-46,-28,-10,8,24]:
 for z in [15,29,43,57,71,85]:cut(x,30, z,13,3,8.5)
for x in [-53,-35,-17,1,19]:details.append(box(x,29,12,1.6,2.8,81))
# Right wing inner facade windows.
for y in [-48,-31,-14,3,20]:
 for z in [13,27,41,55,69,83]:cut(29,y,z,3,12,7)
# Deep projecting lower screen, supported by ground-level piers.
add(22,-20,15,3,80,48)
for z in [20,35,50]:cut(22,-20,z,5,73,8)
for y in [-55,-39,-23,-7,9,17]:details.append(box(22,y,15,3,1.7,48))
for y in [-54,-18,17]:add(22,y,3,3,3,12.2)
# Screen connects to wing by solid horizontal gallery slabs, preserving recess depth.
for z in [15,30,45,60]:add(26,-20,z,9,80,1.8)
# Stack of small balconies at inside elbow.
for z in [15,29,43,57,71]:
 add(24,23,z,17,10,2)
 add(24,18.5,z+1.8,17,1.5,2.5)
# Small roof vent, no exact mechanical reconstruction.
column(44,-47,93,2,5)
step(0,-64,52,3)
# Rear and outward elevations deliberately plain due incomplete views.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
