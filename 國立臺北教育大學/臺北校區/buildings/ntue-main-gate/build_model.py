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

def segment(x,y,z,w,h,rise,depth):
 spring=z+h-rise
 pts=[(x-w/2,z),(x+w/2,z),(x+w/2,spring)]
 pts += [(x+w/2*math.cos(t),spring+rise*math.sin(t)) for t in np.linspace(0,math.pi,33)[1:]]
 return profile(pts,y,depth)
def segment_trim(x,y,z,w,h,rise,th=2.0):
 return segment(x,y,z,w+2*th,h+th,rise+th,2.4)-segment(x,y-.1,z-.2,w,h+.2,rise,3.2)
# Main gate segment: current flat-topped portal shown by official and 2023 photographs.
add(0,0,0,150,52,3)
add(0,0,2.8,140,26,55)
# Tall centre name wall, lower flanking tops.
add(0,0,57,94,26,13)
for z,w in [(57,142),(69,96),(71,98)]:add(0,0,z,w,28,2)
# Wide segmental vehicle arch; two pedestrian passages with straight lintels.
cuts.append(segment(0,0,3,62,40,9,35))
for x in [-47,47]:cut(x,0,3,18,35,29)
# Main supports become paired round columns above the tall plinths.
for x in [-35,35]:
 cut(x,0,15,13,32,17)
 details.append(box(x,0,3,14,28,12.5))
 details.append(box(x,0,31,15,30,4))
 for dx in [-3.1,3.1]:
  for y in [-8.5,8.5]:details.append(Manifold.cylinder(17,2.3,2.3,circular_segments=28).translate((x+dx,y,15)))
# Grey arch surround visible on front and back, with robust keystone.
for a in [0,180]:
 details.append(segment_trim(0,-13,3,62,40,9,2.6).rotate((0,0,a)))
 details.append(box(0,-14.2,43,3.5,3,7).rotate((0,0,a)))
 for z in [37,47,56]:
  for x in [-59,59]:details.append(box(x,-13.4,z,21,1.3,1.3).rotate((0,0,a)))
 # Broad horizontal stone courses, no unprintable lettering or event signboards.
 details.append(box(0,-13.4,68,95,1.4,1.4).rotate((0,0,a)))
# Outer masonry base courses.
for x in [-64,64]:add(x,0,3,13,28,13)
# No invented rear guardhouse; only photographed freestanding portal thickness is included.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
