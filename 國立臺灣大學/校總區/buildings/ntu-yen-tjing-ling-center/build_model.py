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
# E63: broad horizontal brise-soleil, entrance canopy, rear paired solid blades.
add(0,0,0,150,83,3)
add(0,5,2.8,137,48,80)
# 24 thick, solid-backed horizontal louvres, a print-scale abstraction of dense shading.
for z in [5+i*3.2 for i in range(24)]:
 add(0,-20,z,140,5,1.2)
# Deep horizontal shadow gaps remain open to exterior, never enclosed inner shells.
for z in [6.3+i*3.2 for i in range(24)]:cut(0,-19,z,134,1.6,1.7)
# Keep source-supported vertical end edges understated.
for x in [-68,68]:add(x,-19.4,3,1.5,2,80)
# Broad cantilevered main entrance canopy supported by two massive portal walls.
details.append(box(0,-26,24,48,26,3))
for x in [-19,19]:details.append(box(x,-26,3,6,17,23))
cut(0,-22,4,30,8,19)
for x in [-10,0,10]:details.append(box(x,-17.8,4,1,1.8,19))
step(0,-37,42,6)
# Rear paired blank tower-like zones and small rows of horizontal windows.
cut(0,29,12,15,4,70)
for z in range(15,80,9):details.append(box(0,28, z,15,3,1.3))
for x in [-46,-30,30,46]:
 for z in [12,23,34,45,56,67,78]:
  if not (x<0 and z<18):cut(x,29,z,5,2.5,2)
# Lower rear service annex seen in historic photo; small attachment simplified, no equipment.
add(-47,31,2.8,38,13,15)
# Other narrow-side openings unknown and left blank.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
