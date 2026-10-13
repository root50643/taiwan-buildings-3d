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
# M22 main herbarium block, excluding greenhouse, separate drying hut and connecting arcade.
add(0,0,0,150,79,3)
add(0,2,2.8,136,42,56)
add(0,2,58,139,45,1.8)
add(0,2,60,141,47,1.3)
# Long round-headed upper windows and lower rectangles seen on street and garden fronts.
xs=[-57.75+i*10.5 for i in range(12)]
for y in [-19,23]:
 for x in xs:
  if y==23 and abs(x+26)<16:continue
  if not(y==-19 and abs(x)<12):
   cut(x,y,7,6.5,3,13)
   details.append(box(x,y-0.3 if y==23 else y+.3,7,1,2,13))
   details.append(box(x,y-0.3 if y==23 else y+.3,15,7,2,.9))
  arch_cut(x,y,24,7,32,3)
  arch_trim(x,y,24,7,32)
  for z in [34,44]:details.append(box(x,y-0.3 if y==23 else y+.3,z,7.5,2,.9))
  details.append(box(x,y-0.3 if y==23 else y+.3,24,.9,2,27))
  # Lower solid spandrel and subtle vertical trims, not literal exposed interior floors.
  # Continuous arched frame, not stacked classroom-style short windows.
# Street-side principal door and thin rectangular canopy.
cut(0,-19,3.5,19,3,21)
for x in [-6,0,6]:details.append(box(x,-18.5,3,1,2,21.5))
add(0,-23,24,25,11,1.5)
step(0,-32,24,5)
# Garden-side shallow projected entrance bay visible in photographer's courtyard view.
add(-26,24,3,25,8,57.5)
arch_cut(-26,28,4,14,22,3)
arch_cut(-26,28,30,8,26,3)
arch_trim(-26,28,30,8,26)
for z in [39,47]:details.append(box(-26,27.7,z,8.5,2,.9))
add(-26,24,60,28,10,1.5)
# Cornice/base lines; roof behind the parapet is unresolved and simplified as a solid low cap.
for y in [-19.3,23.3]:
 for z in [3,21.5,57]:add(0,y,z,137,1.5,1.5)
# Narrow ends intentionally plain; no greenhouse/interior or speculative pitched roof.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
