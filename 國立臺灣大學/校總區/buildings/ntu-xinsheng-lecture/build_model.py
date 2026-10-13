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
# N25: five-level main block; vertical frame and brick stair-bays are photo-evidenced.
add(0,0,0,150,69,3)
add(0,4,2.8,136,40,55)
# Open corridor appearance is a shallow recess with solid back; no interior replica.
for x in [-60,-48,-24,-12,0,12,24,48,60]:
 for z in [6,17,28,39,50]:cut(x,-16,z,9.3,4,7)
for x in [-66,-54,-42,-30,-18,-6,6,18,30,42,54,66]:add(x,-17,3,1.5,2.4,55)
# Spandrels and horizontal balcony rails enlarged for a durable print.
for z in [15,26,37,48]:
 add(0,-17,z,134,2.4,1.2)
 details.append(box(0,-17,z+2.2,134,1.4,1))
# Broad brick-clad vertical stair zones, visible on main long elevation.
for x in [-36,36]:
 add(x,-18,3,11.5,5.2,55)
# Three small projecting central landings, captured by official close angles.
for z in [15,26,37]:
 add(0,-21.5,z,13,12,1.8)
 add(0,-27,z+1.6,13,1.2,3)
 for x in [-6,6]:add(x,-23,z+1.6,1.2,7,3)
# Upper-level louver strips are robust relief, not separate wires.
for x in [-60,-48,-24,-12,12,24,48,60]:
 for z in [53,55]:details.append(box(x,-16,z,10.8,4.4,.9))
add(0,4,57,139,43,1.6)
add(0,-21,13.3,20,13,1.8)
step(0,-31,30,4)
# Rear is plain due to missing reliable reverse-elevation evidence.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
