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
# M: second dormitory. Ten storeys; official 2019 school presentation p42.
add(0,0,0,115,98,3)
# Narrow front elevation; long flank with repeating paired dormitory windows.
add(0,7,2.8,91,66,131)
# Broad central glass strip, nine transverse window bands alternating solid spandrels.
cut(0,-26,18,25,4.5,110)
for z in range(21,128,12):
 details.append(box(0,-25,z,25.5,3.1,5.2))
 for x in [-8,0,8]:details.append(box(x,-26,z+5.2,1.2,3,6.8))
# Slim side windows flanking the central glass; projecting staggered balcony boxes.
for z in range(11,126,12):
 for x in [-26,26]:
  cut(x,-26,z,3.5,3.2,7.8)
  add(x+2,-28,z,10,5.2,3.4)
# Restrained rectangular wall frames: observed decoration not invented full extra rooms.
for x in [-37,37]:
 for z in range(39,126,12):
  add(x,-26.1,z,13,1.5,1.1)
  add(x+(-6 if x<0 else 6),-26.1,z,1.1,1.5,11)
# Side paired windows visible in the photograph: ten rows with narrow upper lights.
for z in range(8,129,12):
 for y in [-15,0,15,30]:
  cut(-45.4,y,z,3.4,9.0,6.0)
  cut(-45.4,y,z+7.4,3.4,9.0,1.8)
  details.append(box(-45.2,y,z,2.8,1.2,6.1))
# Roofline: stepped rectangular heads, no parapet antenna detail.
add(-30,10,133,24,31,11)
add(28,24,133,18,25,10)
add(1,18,133,17,25,14)
add(1,18,146,20,28,1.4)
add(0,6,132,94,69,1.8)
# True entrance recess, broad lintel canopy and stair wings.
cut(0,-25,3,30,10,13)
for x in [-16,16]:details.append(box(x,-29,3,3.0,5,14))
add(0,-30,15,35,12,2.5)
for i in range(4):add(0,-42+i*2.0,3,34,2.3,1.0*(i+1))
# Source obscures far right and rear: no rear window pattern is fabricated.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.apply_scale(150.0/mesh.extents.max())
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
