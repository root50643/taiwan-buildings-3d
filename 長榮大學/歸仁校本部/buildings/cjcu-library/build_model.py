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
# Library main volume, six occupied above-ground levels plus exposed base/podium.
# Adjacent Computer and Network Center is expressly excluded.
add(0,0,0,150,96,3)
add(0,8,2.8,127,57,55.2)
# Projecting glazed west/public facade between brick end walls.
for z in [26,37,48]:
 cut(-3,-20.5,z,105,3,7)
 add(-3,-23,z-1.8,111,7,1.6)
 for x in range(-51,50,7):details.append(box(x,-20.5,z,1.0,3.8,7))
 # The horizontal mid-glazing sunscreen is backed into the wall.
 details.append(box(-3,-20.5,z+3.2,108,3.8,1.0))
# Broad white fascia band over each of the three glazed storeys.
for z in [34.2,45.2,56.2]:add(-3,-22.4,z,112,5.5,2)
# Two lower public levels with tall broad windows and entrance canopy.
for z in [6,16]:
 for x in [-48,-28,-8,12,32,49]:cut(x,-20.5,z,16,3.0,7)
add(-8,-26,13.8,45,16,1.8)
for x in [-26,10]:add(x,-32,3,2.2,2.2,12)
# Right brick wing and its regular three upper window rows from official photograph.
add(58,7,17,13,60,43)
for z in [28,39,50]:
 for y in [-16,-5,6,17,28]:cut(64.5,y,z,3,5,7)
# Sixth level truly steps back behind the open rooftop frame.
add(-3,13,57.8,110,38,11.5)
for x in range(-48,49,12):cut(x,-6,60,9,2.6,6.3)
add(-3,-8,68.4,113,6,1.8)
add(-3,13,68.6,113,40,1.5)
# Left orange rooftop frame rises above terrace with a genuine open passage below beam.
add(-60,-9,57.8,7,24,16.8)
add(-39,-18,71.2,46,5,3.4)
# Right rooftop frame turns around corner and steps back, as in photo.
add(60,11,57.8,7,52,16.8)
add(50,-13,71.2,25,5,3.4)
add(60,11,71.2,7,52,3.4)
# Thin perimeter terrace guard thickened for miniature, backed by roof slab.
add(-5,-19,58,108,1.3,2.2)
# Raised rooftop service volumes and a prominent front vertical light stone stair core.
add(-20,-9,60,19,24,21)
for z in [65,73]:
 for x in [-25,-18]:cut(x,-21, z,2.3,2.5,5)
add(20,11,69,33,25,7)
add(20,11,75.5,38,29,1.6)
# Front low red-brick arched arcade stays truly open and joined to the main building at ends.
add(0,-34,2.8,131,5,10)
for x in [-56,-43,-30,29,42,55]:arch_cut(x,-34,3,8.5,8,7)
# Central access opening, canopy supports rest behind opening.
cut(-2,-34,3,38,7,10)
add(0,-34,12.4,133,7,1.4)
add(-62,-27,2.8,5,14,10)
add(62,-27,2.8,5,14,10)
# Back unseen is a deliberately plain simplified depth envelope.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
