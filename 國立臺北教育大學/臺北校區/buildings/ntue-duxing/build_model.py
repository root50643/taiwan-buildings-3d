"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. Public plan outlines guide massing; interiors are not reconstructed.
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
# Duxing eight-storey L building. Excludes separately delivered MoNTUE building.
add(0,0,0,150,140,3)
add(0,-35,2.8,132,40,98)
add(-55,23,2.8,22,78,98)
# Main public front: two broad room window zones and narrow service core.
for z in [7,19,31,43,55,67,79,91]:
 for x,w in [(-49,12),(-8,27),(31,38)]:cut(x,-55,z,w,4.6,7)
 # Slender stair slit on far right, clearly separate from long windows.
 if z>=43:cut(60,-55,z,2.6,4.6,4.8)
# Recessed dark vertical circulation zone, observed left of main window bays.
for z in [19,31,43,55,67,79,91]:cut(-29,-55,z,9,5,8)
# Large grey entrance frame at right end with real deep wedge-roof porch.
add(45,-57,3,42,12,37)
# Cutter profile in y/z, rotated into x extrusion. Entry soffit slopes downward inward.
entry=profile([(-64,3),(-33,3),(-33,21),(-64,30)],-45,34).rotate((0,0,90))
cuts.append(entry)
# Door/glazing remains at back, not a fabricated tunnel through the wing.
add(45,-31.8,3,32,4,17)
for x in [34,45,56]:cut(x,-33.8,4,8.2,3.5,11)
# Upper pale-frame glazing and right-end open circulation balconies.
cut(45,-63,32,32,4,5.5)
for z in [6,21]:cut(66,-37,z,8,17,10)
for z in [8,23]:details.append(box(65.4,-37,z,3.2,18.4,1.5))
# Inner L court: broad windows on long wing, paired narrow groups on return.
for x in [-38,-13,12,37,57]:
 for z in [19,31,43,55,67,79,91]:cut(x,-15,z,19,4.4,7)
for y in [-1,15,31,47]:
 for z in [19,31,43,55,67,79,91]:cut(-44,y,z,4.4,11,7)
# Ground colonnade genuinely open ahead of set-back inner glazing.
cut(-1,-15,3,126,15,12)
add(0,-14,15,132,17,1.8)
for x in [-58,-37,-16,5,26,47,62]:details.append(box(x,-14,3,2.5,11,13.0))
cut(-44,23,3,14,68,12)
add(-44,23,15,17,78,1.8)
for y in [-6,11,28,45,59]:details.append(box(-44,y,3,11,2.5,13.0))
# Roof heights: flat parapets visible from below; no invented equipment.
for y in [-55,-15]:add(0,y,100.2,133,1.7,1.8)
for x in [-66,66]:add(x,-35,100.2,1.7,41,1.8)
for x in [-66,-44]:add(x,23,100.2,1.7,79,1.8)
add(-55,62,100.2,23,1.7,1.8)
for i in range(3):details.append(box(45,-67+i*1.4,2.8,35,2,.6*(i+1)))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
