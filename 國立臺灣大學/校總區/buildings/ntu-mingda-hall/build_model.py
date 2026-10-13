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
# E71: three official public exterior views, two-storey arched front and taller gridded block.
add(0,0,0,105,150,3)
add(0,10,2.8,78,116,104)
# Photo-supported front and long sides: five principal upper window bands.
for z in [37,51,65,79,93]:
 for x in [-32,-21,-10,1,12,23,34]:
  if z==37 and abs(x)<25:continue
  cut(x,-48,z,8,2.7,10)
  details.append(box(x,-47.8,z+5,8.6,1.8,.9))
 for side in [-39,39]:
  for y in [-39,-28,-17,-6,5,16,27,38,49,60]:
   cut(side,y,z,2.7,8,10)
   details.append(box(side*.992,y,z+5,1.8,8.6,.9))
# Closely spaced structural fins, thickened for printing, attached to solid back wall.
for x in [-38.5+i*5.5 for i in range(15)]:add(x,-49,31,1,3,76)
for side in [-39,39]:
 for y in [-47+i*5.5 for i in range(22)]:add(side,y,31,3,1,76)
for z in [33,47,61,75,89,103,107]:
 add(0,-49,z,82,3.7,1.3)
 for side in [-39,39]:add(side,10,z,3.7,118,1.3)
# Historicising front, broad lower level with three arch recesses, narrower upper pediment.
add(0,-50,3,80,30,25)
add(0,-54,27,47,22,18)
gable(0,-54,44.7,49,22,12)
add(0,-65,27,83,3,1.8)
add(0,-65,43.5,49,2,1.4)
for x,w,h in [(-29,10,17),(0,21,22),(29,10,17)]:
 arch_cut(x,-65,3.3,w,h,3.3);arch_trim(x,-65.5,3.3,w,h)
for x in [-11,0,11]:
 arch_cut(x,-65,30,8.6,11.2,3);arch_trim(x,-65.5,30,8.6,11.2)
# Circular medallions are shallow backed recesses, not floating or hidden shells.
for x,z,r in [(0,49.5,1.6),(-21,36,1.8),(21,36,1.8)]:
 cuts.append(Manifold.cylinder(3,r,r,circular_segments=32).rotate((90,0,0)).translate((x,-63.7,z)))
# Dentil rhythm along the sloping pediment, represented as short backed blocks.
for x in range(-21,22,3):add(x,-65,54.8-abs(x)*.48,1.2,1.7,1.2)
step(0,-71,73,4)
# Ground-floor side arches only where the official oblique shows the older-style base.
for side in [-39,39]:
 for y in [-23,-4,15,34,53]:
  a=arch(0,0,4,10,18,3).rotate((0,0,90)).translate((side,y,0));cuts.append(a)
# Rear facade not photographed: blank, no copied front elevation.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
