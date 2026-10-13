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
# Wenyuan main two-storey hall: large open ground-level passage supports upper hall.
# Background library and its cross in the source photo are NOT part of Wenyuan.
add(0,0,0,150,89,3)
# End stair/core masses and structural piers support the upper enclosed hall.
for x in [-59,59]:add(x,8,2.8,14,32,40)
for x in [-62,-42,-22,0,22,42,62]:
 for y in [-18,18]:column(x,y,3,1.7,24)
add(0,0,25,135,45,20)
add(0,0,24,138,48,2.2)
for x in [-58,-46,-34,34,46,58]:
 cut(x,-22.5,31,10,3,11)
 details.append(box(x,-22.5,31,1.1,3,11))
 details.append(box(x,-22.5,36,10,3,1.1))
# Projecting framed central name/window panel observed above open passage.
add(0,-25,27,44,6,14)
cut(0,-28,30,37,2.3,9)
for x in [-12,0,12]:details.append(box(x,-28,30,1.3,2.2,9))
# Recessed rear wall glimpsed only in the two end stair areas; centre remains fully open.
hip(0,0,44.5,144,53,6.5)
# Low front platform and stairs; no modeled below-grade classroom interior.
for i in range(3):add(0,-34+i*2,2.8,129,2.3,.6+i*.6)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
