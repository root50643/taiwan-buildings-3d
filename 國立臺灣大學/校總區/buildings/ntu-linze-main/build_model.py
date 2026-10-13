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
# E51 Linze main tower. Detached low lecture hall and bridges are outside scope.
add(0,0,0,150,99,3)
add(0,7,2.8,136,52,98)
# Deep but backed monumental entrance; no interior layout implied.
cut(0,-19,3,31,16,24)
add(0,-23,17,34,12,2)
for x in [-52,-36,36,52]:
 cut(x,-19,5,12,3,19)
 details.append(box(x,-18.6,5,1.1,2,19))
# Four tall window tiers in two paired red-brick zones, divided by grey bands.
for z in [37,51,74,88]:
 for center in [-57,-38,-19,0,19,38,57]:
  for dx in [-5,0,5]:
   x=center+dx;cut(x,-19,z,3.4,3,9.5)
   details.append(box(x,-18.2,z+6.8,3,2,.9))
for z in [29,64]:
 for x in [-56,-38,-19,0,19,38,56]:cut(x,-19,z,15,3,3.6)
for z in [27,34,62,70,100]:add(0,-19.5,z,138,3,1.8)
# Visible left end: grouped upper slots with broad blind central wall.
for z in [37,51,74,88]:
 for y in [-13,-6,22,29]:cut(-68,y,z,3,4,9.5)
for z in [29,64]:cut(-68,7,z,3,46,3.6)
for z in [27,34,62,70,100]:add(-68.5,7,z,3,54,1.8)
# Raised flat roof canopy with enlarged, exterior-open rectangular gaps.
add(0,7,100,137,53,2)
for y in [-18,32]:
 for x in [-65,-43,-21,1,23,45,65]:add(x,y,101.5,2.2,2.2,6)
for x in [-65,65]:add(x,7,101.5,2.2,2.2,6)
add(0,7,107,144,60,2)
step(0,-38,42,6)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
