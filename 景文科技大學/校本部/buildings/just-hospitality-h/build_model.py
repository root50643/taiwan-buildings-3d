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
# H hospitality: official oblique photo shows five ranks, broad flat roof, offset roof box and right shaft.
add(0,0,0,150,87,3)
add(-7,5,2.8,118,45,53)
# Proud front rectangular surround, not a painted border.
for x in [-65,49]:add(x,-18.5,11,2.4,2.8,45)
add(-8,-18.5,54,116,2.8,2)
for z in [15,25,35,45]:
 for x in range(-59,48,9):cut(x,-17.5,z,5,3.5,6)
for x in range(-58,46,12):cut(x,-17.5,4,8,3.5,7)
# Narrow recessed bay at the tower joint.
for z in [5,15,25,35,45]:cut(45,-18,z,4.8,3.6,6)
# Tall right-hand concrete circulation tower with a glazed return and winged cap.
add(60,5,2.8,15,47,65)
for z in [13,27,41,55]:cut(60,-18.5,z,10,3.2,3)
for z in [7,17,27,37,47,57]:cut(67.2,4,z,3.5,21,7)
add(60,5,68,23,52,1.9)
for x in [54,65]:add(x,7,66,1.5,30,3)
# Rectangular mechanical stair head on the left of the roof, seen behind main facade.
add(-39,14,55.5,30,20,11)
for x in [-46,-39,-32]:cut(x,4,58,3,2.5,6)
add(-39,14,66,31,21,1.3)
# Low stepped terrace shown immediately below facade; no landscape, flags or AC units.
add(-7,-26,3,118,13,4)
for i in range(4):add(-53,-35+i*1.4,3,18,1.7,.9*(i+1))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
