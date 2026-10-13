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
# Ground-level entrance segment, first observed entrance only. No underground corridor or second portal.
add(0,10,0,100,150,3)
# Front landing and photographed thick frame.
add(0,-47,2.8,81,29,3)
add(0,-37,5.5,68,15,98)
cut(0,-42,7,50,18,88)
# Closed metal door is retained at rear of shallow recess. Upper glazing is opaque relief.
add(0,-31.8,6,51,3,90)
cut(0,-34,52,43,3.2,38)
# Broad lower louver slats, fused relief on the actual closed door plane.
for z in range(11,49,4):details.append(box(0,-34,z,44,2.2,1.8))
# Thin central glass subdivisions simplified, not structural wall piers.
# Upper glass remains one broad panel; internal display decoration is not a mullion.
# Heavy flat top cap projects ahead of frame; underside is flat and open in front of door.
add(0,-39,102,74,23,5)
# Only observed left side retaining wall descending toward covered ground is modeled.
# Its back/right boundaries are deliberate local cutoffs, not the missing subterranean body.
wall=profile([(-45,5), (71,5),(71,25),(35,31),(1,61),(-20,96),(-45,102)],31,6).rotate((0,0,90))
parts.append(wall)
# Three broad horizontal courses observed at foot of left wall.
for z in [9,17,25]:add(-31,13,z,6.8,114,1.2)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
