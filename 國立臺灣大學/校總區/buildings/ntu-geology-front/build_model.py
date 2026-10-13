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
# S22: three-storey front block only, excluding old specimen building and rear complex.
add(0,0,0,150,72,3)
add(0,6,2.8,136,43,44)
add(0,6,46,140,48,2)
# Deep arched precast window hoods are the key feature, not plain flat arched holes.
for x in [-57,-38,-19,0,19,38,57]:
 for xx in [x-5.5,x,x+5.5]:
  for z,h in [(5,12.5),(21,10.5),(35,9)]:
   if x==0 and z==5:continue
   outer=arch(xx,-17,z,5.3,h+1,4.6)
   parts.append(outer)
   cuts.append(arch(xx,-17,z+.9,3.5,h-.2,6))
for z in [3,18,32,45]:add(0,-15.7,z,137,1.5,1.6)
for x in [-67,-47.5,-28.5,-9.5,9.5,28.5,47.5,67]:add(x,-15.7,3,1.5,1.6,43)
# Thin curved front canopy approximated by a solid shallow curved roof, supported back wall.
pts=[(-13,16),(13,16)]+[(float(x),18+1.8*(1-(x/13)**2))for x in np.linspace(13,-13,31)]
parts.append(profile(pts,-21,15))
cut(0,-15.5,3.2,18,3,11)
for x in [-6,0,6]:details.append(box(x,-15,3,.9,2,11.3))
step(0,-29,25,4)
# Roof-edge brackets appear on the public front; simplified into solid teeth.
for x in range(-66,67,4):add(x,-16.9,44,1.2,5,2.5)
# End faces and back deliberately plain; no inferred matching array.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
