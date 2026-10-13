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
# E10: front plus both obliques from NTU official exterior gallery.
add(0,0,0,150,90,3)
add(0,8,2.8,136,61,66)
# Central grey entrance tower and shallow monumental arch.
add(0,-24,3,41,8,74)
add(0,-24.5,20,48,9,5)
arch_cut(0,-29,3.4,27,21,3.4);arch_trim(0,-29.6,3.4,27,21)
for x in [-9,-4.5,0,4.5,9]:details.append(box(x,-28.4,2.8,1,3,16.7))
for z in [28,42,56]:
 cut(0,-28,z,20,3.3,9)
 for x in [-6.5,0,6.5]:details.append(box(x,-27.6,z,1,2,9))
 details.append(box(0,-27.6,z+4,20,2,1))
# Stepped top with diamond medallion rather than a fabricated roof.
add(0,-24,74,23,8,4)
parts.append(profile([(-12,77),(12,77),(0,87)],-24,8))
cuts.append(profile([(0,79),(2.5,81.5),(0,84),(-2.5,81.5)],-28,2.5))
# Four upper bands and ground-level rectangular/circular openings seen through trees.
for x in [-56,-40,40,56]:
 for z in [22,34,46,58]:
  cut(x,-22.5,z,9,3,7)
  details.append(box(x,-22.1,z+3.5,9,2,.9))
for x in [-58,58]:
 cuts.append(Manifold.cylinder(3,3.8,3.8,circular_segments=40).rotate((90,0,0)).translate((x,-21.3,10)))
for x in [-42,-29,29,42]:cut(x,-22.5,5,6,3,9)
# Exposed grid on two side elevations; depth and bay count are approximate.
for side in [-68,68]:
 for y in [-15,-2,11,24,34]:
  for z in [22,34,46,58]:cut(side,y,z,3,8,7)
 for y in [-20,-7,6,19,32]:add(side,y,19,2.3,1.6,47)
 for z in [19,31,43,55,67]:add(side,8,z,2.3,61,1.4)
step(0,-35,44,4)
# Tree-obscured small features, unseen rear and roof equipment left plain.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
solid=solid.scale((1,1,.9))
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
