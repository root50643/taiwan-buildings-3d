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
# Two connected blocks J and K, one combined exterior model to avoid duplicating shared hall.
# Photographed 2024-10-19, actual photos 65/77/78; official JK thumbnail secondary.
add(0,0,0,150,83,3)
add(-46,6,2.8,47,39,59)
add(34,6,2.8,72,39,59)
# Tall flat bookend towers flank each block and center link.
for x in [-69,-22,-2,70]:add(x,6,2.8,4,42,62)
# Middle recessed hall and elevated entry canopy with open underside.
add(-12,9,2.8,19,35,42)
add(-12,-7,27,21,24,2)
for x in [-21,-3]:add(x,-17,3,2,2.2,25)
for x in [-18,-12,-6]:arch_cut(x,-8.5,32,4.5,7,3.5)
# Hall roof transverse barrel-like cover simplified with sloping sheet.
add(-12,9,45,21,36,2)
# Stair flights leave the low central passage open beneath upper canopy.
for i in range(7):add(-8,-28+i*1.7,2.8,11,2,1.7*(i+1))
# Right gym facade: upper three tall window tiers and a doubled small crown strip.
for x in range(6,67,5):
 for z in [37,44,51]:cut(x,-13.5,z,3.7,3.5,4.8)
 for z in [57,60]:cut(x,-13.5,z,1.4,3.5,1.5)
 # Lower tall glazing and small square tile above each bay.
 cut(x,-13.5,18,3.6,4,12)
 details.append(box(x,-14,18,1.0,4.6,12))
 cut(x,-13.5,32,1.8,3,1.7)
# Ground arcade beneath broad low canopy, actually open depth.
for x in range(6,67,5):cut(x,-13.5,3,3.5,10,9.8)
add(35,-17,13,66,8,1.9)
# Left teaching block has five flatter horizontal window rows.
for x in range(-64,-24,5):
 for z in [8,20,31,42,51]:cut(x,-13.5,z,3.5,3.6,5.0)
 for z in [57,60]:cut(x,-13.5,z,1.5,3.4,1.5)
add(-46,-16,14,44,6,1.7)
for x in [-69,-22,-2,70]:
 for z in [13,23,33,43,53]:cut(x,-15,z,1.5,3,6)
add(-46,6,62,48,40,1.6)
add(34,6,62,73,40,1.6)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
