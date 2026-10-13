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

def ell(x,y,z,rx,ry,h):return Manifold.cylinder(h,1,1,circular_segments=128).scale((rx,ry,1)).translate((x,y,z))
def circle_cut(x,y,z,r,d):cuts.append(Manifold.cylinder(d,r,r,circular_segments=24).rotate((90,0,0)).translate((x,y+d/2,z)))
def ramp_x(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x+w/2,z+h)],y,d))
# N13. Five-level brick slab + lower wing, entrance portico and green-ramp mass.
add(0,0,0,150,120,3)
add(22,8,2.8,78, 70,57)
add(-36,17,2.8,39,63, 30)
# Entrance portico is open to exterior, with a thickened 2.5mm canopy.
add(-22,-32,24,83,23,2.5)
add(-61,-32,3,4,23,23)
add(-22,-23,3,4,5,23)
# Circular roof opening visible in Harvard's entrance image, open through canopy.
cuts.append(Manifold.cylinder(4,5,5,circular_segments=40).translate((-36,-34,23.5)))
# Brick front: four rows of regular square windows, from official and Harvard photos.
for x in [-8,6,20,34,48]:
 for z in [29,39,49]:cut(x,-27,z,5.8,1.8,6)
# Tall front glazing under canopy.
for x in [-16,-8,0,8,16,24,32,40,48]:cut(x,-27,5,4.8,1.8,17)
# Left end exposed balconies and robust low parapets.
for z in [26,37,48,59]:
 add(-18,9,z,6,63,1.5)
 add(-20,9,z+1.2,2,63,3)
# Long side strips on the lower wing; visible in official overview.
for y in [-8,1,10,19,28,37]:
 cut(-55.5,y,6,1.6,5.4,13)
 cut(-55.5,y,23,1.6,4,6)
# Lawn ramp read as solid wedge, without copying landscaping or interior spaces.
# Low sloping volume runs alongside the main hall, as shown in official elevated view.
ramp_x(-36,49,2.9,49,20,13)

step(-21,-49,82,6)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
