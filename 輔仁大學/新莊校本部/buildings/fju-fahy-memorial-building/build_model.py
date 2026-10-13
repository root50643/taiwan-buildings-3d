"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. No survey or interior data used.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, Mesh64
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
# Whole main tower exterior study; rear depth is estimated and plainly declared.
add(0,0,0,150,95,3)
# Two lower side wings, central taller head and glazed vertical middle.
add(0,8,2.8,110,48,113)
add(0,6,114,64,47,25)
add(0,-18,19,65,9,111)
cut(0,-23,30,28,3.5,90)
# Continuous central glazed grid, backed recess prevents loose mullions.
for x in [-11,-5.5,0,5.5,11]:details.append(box(x,-23,31,1.0,3.8,88))
for z in range(32,119,9):details.append(box(0,-23,z,28,3.8,1.0))
# Six visible side window levels and rooftop recessed balcony.
for z in [40,54,68,82,96,110]:
 for side in [-1,1]:
  cut(side*44,-16,z,18,3.5,8)
  for x in [side*38,side*44,side*50]:details.append(box(x,-17,z,1.2,3.6,8))
  add(side*44,-18,z-2,22,5,2)
for side in [-1,1]:
 cut(side*44,-16,111,18,4,4)
 # Side fenestration is not sufficiently observed and is intentionally omitted.
# High central blank head with triple slot pairs, prominent name plaque.
for x in [-26,-21,-16,16,21,26]:cut(x,-17.5,128,2.2,4,7)
add(0,-24,117,32,4.0,6)
add(0,-24,111,33,4.5,2)
# Lower entry portal with circular canopy and open columns below.
for side in [-1,1]:
 for z in [10,23]:cut(side*44,-16,z,16,3,3)
# semicircular portico footprint is supported by columns and main wall.
port=Manifold.cylinder(2.5,23,23,circular_segments=96).translate((0,-16,27))
parts.append(port ^ box(0,-28,26,49,28,5))
for x in [-20,-10,10,20]:column(x,-28 if abs(x)==20 else -36,3,1.8,25)
# curved staircase, broad raised entrance landing; arching stairs represented as cut disks.
for i in range(7):
 st=Manifold.cylinder(.8+i*.85,29-i*1.0,29-i*1.0,circular_segments=96).translate((0,-14,2.8))
 parts.append(st ^ box(0,-32,2.8,63,37,8))
# Top slabs emphasize the actual stepped skyline.
add(0,7,138.5,67,49,2)
add(-44,8,115,24,48,2);add(44,8,115,24,48,2)
# Source photos do not resolve the rear fenestration; this face is intentionally plain.

parts=[parts[0]]+[p.scale((.88,1,1)) for p in parts[1:]]
cuts=[p.scale((.88,1,1)) for p in cuts]
details=[p.scale((.88,1,1)) for p in details]
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
