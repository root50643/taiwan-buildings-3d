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
# Nine-storey classroom block; lower floors unobstructed in 2023 dated inventory photo.
add(0,0,0,150,83,3)
add(0,5,2.8,132,50,90)
# Ground-level sheltered entrance, shallow bays rather than an invented full internal void.
for x in [-53,-36,-19,-2,15,32,49]:cut(x,-20,3,13,5,8)
# Broad brick facade has horizontal bands and closely spaced rectangular window groups.
for z in [15,25,35,45,55,65,75,85]:
 for x in [-54,-40,-26,-12,2,16,30,44]:
  cut(x,-20,z,10.8,3.2,5)
  details.append(box(x,-20,z,.9,2.8,5))
 add(0,-20.3,z-2,131,1.3,1.4)
# Projecting glazed stair tower on front right, ties to backing wall.
add(56,-22,3,12,7,91)
for z in range(8,91,10):cut(56,-25.5,z,9,2.6,7)
add(56,-25.7,4,1.2,1.4,90)
# Exposed left end: sparse openings and shallow projecting floor slabs.
for z in [15,25,35,45,55,65,75,85]:
 cut(-66,7,z,3,9,4)
 add(-66,5,z-2,2,49,1.2)
# Flat roof, two separate stair penthouses and the front tower cap.
add(0,5,92.4,135,52,1.8)
add(-40,12,94,14,14,12)
add(54,-14,93.5,15,14,16)
add(54,-14,109,17,16,1.5)
# Covered entrance slab; deep rear remains deliberately simplified.
add(-13,-23,12,105,13,2)
for x in [-59,34]:add(x,-27,3,2,2,10)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
