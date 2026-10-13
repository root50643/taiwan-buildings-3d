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
# S62: public exterior before the ongoing restoration noted by NTU in 2026.
add(0,0,0,150,76,3)
add(0,6,2.8,136,26,18.5)
# Long gable roof, ridge parallel to the long facade, continuing over the veranda.
parts.append(profile([(-23,21),(23,21),(0,31)],0,143).rotate((0,0,90)))
# Raised porch is open to outside; the building itself is solid.
add(0,-15,2.8,140,17,1.8)
for x in [-66,-51,-36,-21,-6,9,24,39,54,67]:add(x,-21,4.5,1.7,1.7,17)
add(0,-21,20,139,2,1.5)
# Visible front doors and windows, simplified rhythm, not a measured bay schedule.
for x in [-57,-42,-27,-12,3,18,33,48,61]:
 if x in [-42,3,48]:cut(x,-7,4.5,6,2.5,12.5)
 else:
  cut(x,-7,9,8,2.5,6.5)
  details.append(box(x,-6.7,9,1,1.7,6.5));details.append(box(x,-6.7,12.5,8.4,1.7,.9))
# Opposite long face is documented in the official pre-restoration photo.
for x in [-56,-39,-22,-5,12,29]:
 if x in [-22,12]:cut(x,19,3.5,6.5,2.5,13)
 else:cut(x,19,9,8,2.5,7)
# Small lower end annex seen on the official rear oblique, roof/position approximate.
add(58,23,2.8,24,23,14)
parts.append(profile([(44,16.5),(72,16.5),(58,22)],23,25))
# End weatherboard relief on the photographed gable, simplified coarse lines.
for z in [6,9,12,15,18]:add(-68,6,z,1.2,26,.8)
for y in [-5,0,5,10,15]:add(-68,y,3,.9,.9,18)
cut(-68,6,10,2.5,7,5)
step(-46,-28,16,3)
# No roof tiles, tiny diagonal braces, indoor partitions, rice plots or signs reproduced.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
