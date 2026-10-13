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
# E: courtyard plan from official campus map; seven-level side balcony wing confirmed in oblique photograph.
add(0,0,0,150,119,3)
# Four perimeter bars leave a genuinely open-air central courtyard.
add(-51,7,2.8,25,75,76)
add(51,7,2.8,25,75,76)
add(0,36,2.8,104,19,76)
add(0,-23,2.8,104,21,76)
# Photograph's near side: deeply recessed balcony bays, continuous parapet and narrow stair strip.
for z in [9,19,29,39,49,59,69]:
 for y in [-18,5,28]:cut(-63.1,y,z,3.8,18,6)
 add(-63.2,7,z+5.7,2.4,73,1.3)
for z in [8,18,28,38,48,58,68]:cut(-61,42,z,5,5,3)
# Front side seen receding in photo: paired window zones with a central tall seam.
for x in [-45,-29,-13,13,29,45]:
 for z in [10,21,32,43,54,65]:cut(x,-33.5,z,7,3.3,6)
# Stepped top-front blocks and round openings are visible at the photograph's roof silhouette;
# their full frontal composition is supplemented by the official elevation illustration.
for x in [-29,29]:
 add(x,-23,78,18,21,5)
 ring=Manifold.cylinder(3,5.6,5.6,circular_segments=64).rotate((90,0,0)).translate((x,-32,84))
 hole=Manifold.cylinder(5,3.8,3.8,circular_segments=64).rotate((90,0,0)).translate((x,-31,84))
 parts.append(ring);cuts.append(hole)
add(0,-23,76,20,21,10)
# Main projecting entry canopy on substantial piers; taken directly from oblique photo.
cut(0,-33,3,20,5,16)
add(0,-39,20,42,22,2.7)
for x in [-18,18]:add(x,-47,3,3.3,3.3,18)
step(0,-51,42,4)
# Restrained parapets and blank rear: unseen rear window schedule not mirrored.
for x in [-51,51]:add(x,7,78,26,76,1.5)
add(0,36,78,105,20,1.5)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
