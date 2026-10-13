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
# Four-storey science building with two-storey recess/colonnade at left.
add(0,0,0,150,104,3)
add(0,7,2.8,130,68,58)
# Large visible open corner is cut through left side, beneath the continuous upper floor.
cut(-42,-21,17,48,30,28)
# Two tall frontal columns and an intermediate gallery slab retain characteristic massing.
for x in [-62,-34,-7]:details.append(box(x,-28,3,2.8,4.5,43))
add(-44,-14,31,39,30,2.2)
# Deep middle entrance bay, backed by inner wall.
cut(-2,-25,3,24,18,41)
add(-2,-14,30,24,8,2.2)
# Continuous top storey with paired window groups and small ventilation slots.
for x in range(-56,57,15):
 cut(x,-27,49,10,3,6)
 cut(x,-27,56,10,3,2.4)
# Right three lower storeys use horizontal openings, robust piers between bays.
for z in [8,21,35]:
 cut(35,-27,z,56,3,7)
 for x in [12,26,40,54]:details.append(box(x,-27,z,1.4,3.5,7))
# Windows at the back of the deep bays, not applied to the open front plane.
for z in [21,35]:
 for x in [-48,-21]:cut(x,-6.5,z,16,3,6.5)
 cut(1,-16.1,z,16,3,6.5)
# Roof vent stacks visible in both public views, grouped approximately, not machinery survey.
for x,y in [(-13,7),(-7,7),(36,11),(47,11),(52,11)]:
 column(x,y,60.5,1.8,5.5);column(x,y,65,2.6,1)
step(-2,-39,36,3)
# Unknown rear elevation and main depth remain explicitly simplified.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
