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
# B Basic Medical: stepped front window composition and groups of circular openings.
add(0,0,0,150,92,3)
add(0,10,2.8,132,47,70)
# Main front glazing narrows towards the ground, a distinctive staggered facade.
for x,z,w in [(0,58,125),(0,44,88),(3,30, sixty:=60),(8,16,30)]:
 cut(x,-13.5,z,w,3.5,8)
 for xx in np.arange(x-w/2+6,x+w/2,8):details.append(box(xx,-13.5,z,1.1,3.7,8))
 add(x,-14,z-1,w+3,3.6,1.4)
# Small circular trios flank the descending window bands.
for sign in [-1,1]:
 for z in [23,38,53]:
  for xx,zz in [(sign*58,z),(sign*52,z),(sign*55,z-4)]:
   cuts.append(Manifold.cylinder(3.5,1.6,1.6,circular_segments=24).rotate((90,0,0)).translate((xx,-11.5,zz)))
# Ground entrance glazing and flat entrance shade.
for x in [-47,-30,-13,7,24,43]:cut(x,-13.5,5,12,3.5,7)
add(0,-17,13,136,12,1.8)
# Roof sport enclosure: left gabled section and longer airy right canopy.
add(0,10,72,135,49,1.8)
add(-44,13,73,37,36,10)
cut(-44,-5,75,31,3.3,6)
gable(-44,13,82.5,42,39,4)
# Taller long roof screen uses an open front supported by robust posts, no interior survey.
add(23,29,73,84,3,13)
for x in [-18,3,25,47,63]:add(x,-9,73,1.6,2,13)
add(23,10,85,85,41,2)
add(-5,10,73,23,37,11)
step(0,-29,36,3)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
