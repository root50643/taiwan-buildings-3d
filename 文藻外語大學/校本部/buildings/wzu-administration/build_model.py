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
# Administration: main facade bar, unequal courtyard returns, clerestory and high rear/right core.
add(0,0,0,150,145,3)
add(0,-31,2.8,134,25,55)
add(-55,-5,2.8,25,60,45)
add(55,10,2.8,25,100,47)
add(53,-22,2.8,28,35,72)
# Top recessed classroom row and contrasting high rectangular service volume.
add(-8,-26,57.4,105,24,14)
hip(-8,-26,71,113,30,4.0)
add(35,-19,74,22,23,17)
add(35,-19,90.5,26,27,2)
# Broad near facade: ground brick screens, middle separate window groups and upper long bands.
for x in [-55,-39,-23,23,39,55]:
 cut(x,-43.5,9,10,3.2,7)
 cut(x,-43.5,29,9,3.2,9)
for x in [-53,-32,-11,10,31,52]:
 cut(x,-43.5,44,17,3.3,9)
 details.append(box(x,-43.5,44,1.1,3.2,9))
for x in range(-51,42,12):cut(x,-38,61,10,3,8)
for x in [-65,-17,17,65]:add(x,-44,3,2.5,2,54)
# Central framed tiled portal: real ground passage kept open through main bar.
add(0,-48,3,37,13,36)
cut(0,-40,3,28,46,15)
cut(0,-54.5,23,30,3.5,9)
for x in [-10,0,10]:details.append(box(x,-54.5,23,1.1,3.4,9))
hip(0,-48,38.5,43,19,4)
# Inner gallery recesses along return wings retain the courtyard void.
for x,ys in [(-42.5,[-24,-8,8]),(42.5,[-12,4,20,36,52])]:
 for y in ys:
  for z in [8,24,39]:cut(x,y,z,7,11,8)
# Far façades and inter-wing depth are outer-outline estimates, no indoor layout.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
