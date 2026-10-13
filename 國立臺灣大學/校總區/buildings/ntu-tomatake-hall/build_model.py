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
def shallow_arch(x,y,z,w,h,depth,rise):
 pts=[(x-w/2,z),(x+w/2,z),(x+w/2,z+h-rise)]
 pts += [(xx,z+h-rise+rise*(1-((xx-x)/(w/2))**2)) for xx in np.linspace(x+w/2,x-w/2,31)[1:]]
 return profile(pts,y,depth)
# E22: Tomatake / Zhiwu hall, separate from old Agricultural Machinery hall E21.
add(0,0,0,150,81,3)
add(0,5,2.8,136,48,54)
add(0,5,56,139,51,1.6)
# Four visible window rows with the broad grey bands and brick infill retained as relief.
for x,w in [(-55,16),(-31,15),(0,22),(31,15),(55,16)]:
 for z in [6,19,32,45]:
  if x==0 and z in [6,19]:continue
  cut(x,-19,z,w,3,8)
  for xx in [x-w/4,x+w/4]:details.append(box(xx,-18.6,z,1,2,8))
  details.append(box(x,-18.6,z+4.5,w+.6,2,1))
for z in [3,15,28,41,54]:add(0,-19.6,z,138,2,2.3)
# Tall slender facade piers, projecting slightly and continuous through the bands.
for x in [-67,-43,-19,19,43,67]:add(x,-20.1,3,2.3,3.4,54)
# Raised grey central cap and small round opening, no invented pitched roof.
add(0,-19.4,55,40,4,6.5)
cuts.append(Manifold.cylinder(3,2.2,2.2,circular_segments=36).rotate((90,0,0)).translate((0,-19,58.3)))
# Front portal with low segmented curve, balcony-like solid parapet and two large piers.
add(0,-23,3,38,13,17)
cuts.append(shallow_arch(0,-29.5,3.3,23,12,3.5,2.7))
add(0,-24,19,42,15,2)
add(0,-30.6,20,42,1.7,5)
for x in [-17,17]:add(x,-24.5,3,4,12,17)
step(0,-35,35,4)
# Both blank narrow side walls with horizontal stripes are visible in official obliques.
for x in [-68,68]:
 for z in [3,15,28,41,54]:add(x,5,z,1.8,48,2.3)
# Rear not photographed; left blank, no interiors or equipment.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
