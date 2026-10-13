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
# Ten-storey tower with differentiated taller window slab and lower open-loggia wing.
add(0,0,0,150,96,3)
add(-8,9,2.8,72,55,130)
add(-54,11,2.8,21,51,104)
add(42,11,2.8,39,51,120)
# Nine upper ranks plus ground level; photo establishes paired windows.
for z in range(18,127,12):
 for x in [-35,-17,1,19]:
  cut(x,-18.5,z,10.5,3.5,7.5)
  details.append(box(x,-18.5,z,1.1,3.6,7.5))
for z in range(17,118,12):
 cut(42,-14.5,z,33,5,9)
 for x in [29,42,55]:details.append(box(x,-14.5,z,1.4,5.2,9))
for z in range(14,121,12):add(42,-16,z,40,4,1.8)
# Raised main outer frame and caps preserve the source silhouette.
for x in [-45,29]:add(x,-19,3,3,3,131)
add(-8,9,132,78,60,2.2)
add(-54,11,106,24,54,2)
for z in range(17,102,12):
 cut(-54,-14.5,z,15,5,9)
 details.append(box(-54,-14.5,z,1.4,5.2,9))
for z in range(14,105,12):add(-54,-16,z,22,4,1.8)
add(42,11,121.5,42,56,2)
for x in [-35,-17,1,19]:cut(x,-18.5,3,13,4,10)
add(-20,-23,13,91,14,2)
step(-20,-33,92,4)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
