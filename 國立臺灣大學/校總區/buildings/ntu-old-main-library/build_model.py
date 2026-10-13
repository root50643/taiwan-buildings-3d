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
# Old Main Library / History Gallery front historic volume only.
add(0,0,0,150,68,3)
add(0,6,2.8,136,40,32)
add(0,-15,2.8,43,9,34)
gable(0,-15,36,45,9,9)
add(0,6,34,138,42,1.3)
# Central arched window and flank lancets; exact masonry patterns omitted.
arch_cut(0,-19.5,20,13,15,1.8);arch_trim(0,-19.5,20,13,15)
for x in [-16,16]:arch_cut(x,-19.5,20,4.2,12,1.6)
for x in [-3.5,0,3.5]:details.append(box(x,-19.1,20,.9,1,10))
for z in [24,28]:details.append(box(0,-19.1,z,12.5,1,.9))
# Three arches in the deeply projecting entrance loggia, closed-backed.
add(0,-25,2.8,40,12,16.6)
for x in [-13,0,13]:arch_cut(x,-31,3,9,13.3,7);arch_trim(x,-31,3,9,13.3)
add(0,-30.7,18.5,41,2,1.5)
for x in [-59,-49,-39,-29,29,39,49,59]:
 arch_cut(x,-14,19,5.2,13,1.7);arch_trim(x,-14,19,5.2,13)
 cut(x,-14,5,5.2,1.5,9)
# The circular gable vent is a shallow recess, no unobserved interior.
cuts.append(Manifold.cylinder(2,1.9,1.9,circular_segments=24).rotate((90,0,0)).translate((0,-18.4,39)))
step(0,-34,43)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
