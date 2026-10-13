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
# Eleven-floor central tower rising above lower wide wings and paired circular end cores.
add(0,0,0,150,89,3)
add(0,9,2.8,125,54,106)
add(0,-18,2.8,47,24,140)
for x in [-64,64]:column(x,-8,2.8,7,116)
# Central facade grid and deeper twin upper loggias.
for z in [8,25,42,57,71,85,99]:
 for x in [-17,-6,6,17]:cut(x,-30,z,8.5,3,10)
cut(0,-30,3,15,3,31)
for x in [-14,14]:cut(x,-28,119,13,13,11)
for x in [-14,14]:cut(x,-30,135,14,3,4)
cut(0,-30,131,11,3,8)
# Wings have alternating paired and singleton windows, not a copied box texture.
for z in [8,24,39,54,68,82,97]:
 for x in [-55,-40,40,55]:cut(x,-18,z,10,3,7)
for z in [15,31,46,61,75,89,103]:
 for x in [-48,48]:cut(x,-18,z,11,3,3)
# Visible cylindrical cores carry horizontal slit bands on front halves.
for x in [-64,64]:
 for z in [15,31,47,63,79,95,108]:cut(x,-14,z,16,4,5)
# Robust facade vertical mullions within lower central window bands.
for z in [42,57,71,85,99]:
 for x in [-17,-6,6,17]:details.append(box(x,-30,z,1.2,3.2,10))
step(0,-39,37,3)
# Back elevation and depth unknown; 2013 entrance state rather than presumed 2026 renovation.
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
solid=solid.scale((1,1,0.76)) # Photo-derived wide-to-high proportions, not survey.
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
