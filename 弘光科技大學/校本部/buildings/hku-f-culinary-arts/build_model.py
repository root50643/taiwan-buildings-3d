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
# F building, photographed in 2024 event directions; official 3D image secondary only.
add(0,0,0,150,103,3)
add(0,9,2.8,129,58,72)
# Front has five narrow framed louver fields and a broad plain right sign panel.
for x in [-54,-37,-20,-3,14]:
 cut(x,-20,14,13.5,3.5,48)
 # Horizontal louvers are backed wall relief, every rib >=1.1 mm.
 for z in range(15,62,3):details.append(box(x,-20.4,z,13.7,3.8,1.15))
for x in [-63,-46,-29,-12,5,22]:add(x,-22,12,2.0,4,52)
# Upper set-back floor with continuous horizontal opening and stout uprights.
cut(0,-20.5,65,120,4,7)
for x in range(-58,63,16):details.append(box(x,-21,65,1.8,4.5,7))
add(0,9,74,132,60,2.1)
# Low glazed ground level and long awning, with end bay stepping around the front.
for x in range(-54,62,17):cut(x,-20,4,13,4,6)
parts.append(profile([(-67,12),(67,12),(67,14.1),(-67,14.1)],-23.3,8))
# Right return visible in photo: recessed long bands and tall screen beside stairs.
for z in [16,29,42,55]:cut(64.5,12,z,3.5,40,7)
for y in [-15,-5,5,15,25]:add(65.2,y,10,2.5,1.4,61)
# Two front low stairs/retaining cheeks are gross exterior site approximations.
for x in [-43,31]:
 for i in range(5):add(x,-38+i*2.4,2.8,29,2.7,(i+1)*1.05)
# Roof's modest left utility volume, seen above the wall.
add(-48,20,76,20,19,7)
for x in [-53,-46]:cut(x,10.5,79,4,2,2)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
