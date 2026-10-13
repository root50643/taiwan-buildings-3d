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
# A administrative/teaching building. Central arch verified by university actual photo.
add(0,0,0,150,92,3)
# Main three-level teaching wing, entrance group and right lower return.
add(-33,8,2.8,70,41,46)
add(10,3,2.8,28,43,51)
add(42,14,2.8,36,37,39)
# Narrow full-height arched stair glazing in a recessed panel.
arch_cut(10,-19,10,14,40,5)
for x in [5.5,10,14.5]:details.append(box(x,-19,10,1.05,5.3,30))
for z in [19,30,40]:details.append(box(10,-19,z,14.4,5.3,1.1))
# Arch mullions only reach the backed upper arch surface.
for x,h in [(5.5,5),(10,7),(14.5,5)]:details.append(box(x,-18,40,1.05,3.4,h))
# Stepped red shoulders are distinct vertical masses.
add(-6,-1,2.8,6,42,46)
add(27,3,2.8,7,42,51)
add(37,5,2.8,16,41,47)
for x in [-6,27]:
 for z in [9,24,39]:cut(x,-22 if x==-6 else -18,z,3.9,5,8)
parts.append(profile([(-4,52),(24,52),(24,57),(5,57)],3,43))
# Long white/red classroom wing with three rows and five visible bays.
for z in [8,23,38]:
 for x in [-60,-47,-34,-21]:cut(x,-12.5,z,9.5,4,6.6)
for x in [-66,-54,-41,-28,-15]:add(x,-14,3,1.5,3.2,44)
# Open entry throat under arch; front steps and lintel frame.
cut(10,-19,3,12,9,6)
step(10,-26,30,5)
add(-33,8,48.2,74,43,2)
# Right low wing side/courtyard opening visible only in secondary view: simplified.
for z in [8,20,32]:
 for x in [45,55]:cut(x,-4.5,z,6,3,5.5)
add(42,14,41,39,39,1.7)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
