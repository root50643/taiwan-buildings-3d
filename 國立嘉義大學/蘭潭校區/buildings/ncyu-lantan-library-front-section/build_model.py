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
# A31 Library and Information Building: front block SECTION only.
# Real photographed front facade and corner returns; artificial plain cut rear at y=+15.
add(0,0,0,150,65,3)
add(0,2,2.8,128,26,53.2)
# Central projecting frontispiece and taller shallow gable.
add(0,-2,2.8,38,34,58.2)
parts.append(profile([(-19,60.7),(19,60.7),(19,64),(0,70),(-19,64)],-2,34))
for x in [-21,21]:add(x,-2,2.8,10,30,57.2)
# Corner cylindrical bays, not detached turrets.
for x in [-62,62]:
 parts.append(Manifold.cylinder(53.5,8.5,8.5,circular_segments=64).translate((x,-4,2.8)))
 parts.append(Manifold.cylinder(1.8,9.2,9.2,circular_segments=64).translate((x,-4,45.4)))
 parts.append(Manifold.cylinder(13.5,9,9,circular_segments=64).translate((x,-4,47)))
 parts.append(Manifold.cylinder(6,9.5,4.5,circular_segments=64).translate((x,-4,60.2)))
 # Projecting vertical upper grille remains fused to the cylinder backing.
 for a in range(0,360,30):
  ang=math.radians(a);xx=x+9*math.cos(ang);yy=-4+9*math.sin(ang)
  cuts.append(box(0,-8.6,48,2.1,2.5,11).rotate((0,0,a)).translate((x,-4,0)))
 # Lower front bay windows; shallow solid-backed recesses.
 for xx in [x-4,x,x+4]:
  cut(xx,-11.4,9,2.5,3,12)
  cut(xx,-11.4,24,2.5,3,12)
# Deep lower window groups across brick wings: two-level vertical panes with raised surrounds.
for x in [-50,-40,-30,30,40,50]:
 cut(x,-11,9,6.4,3.4,20)
 details.append(box(x,-9.7,18,7.0,1.5,1.1))
 details.append(box(x,-9.7,8.8,1.0,1.5,20.4))
 cut(x,-11,34,4.1,3.3,8)
 # Upper setback continuous small window band.
 cut(x,-11,48,7.8,3.4,6)
 add(x,-12,46.3,9.8,2.4,1.4)
# Shallow cornices over upper wing bands and main floor transition.
for x in [-44,44]:
 add(x,-.5,55.4,39,29,1.6)
 add(x,-12,44.8,38,2.7,1.4)
# Main three tall arched windows, central taller than the flank pair.
for x,z,h,w in [(-10.5,28,30,7.8),(0,28,33.5,8.3),(10.5,28,30,7.8)]:
 cuts.append(arch(x,-19, z,w,h,3.8))
 for zz in [34,41,48,54]:
  if zz<z+h-2:details.append(box(x,-17.5,zz,w+.3,1.2,1.0))
 details.append(box(x,-17.5,z-.2,1.0,1.2,h-2.0))
# Five round oculi beneath the peaked top.
for x,z in [(-15,60.5),(-8,63.5),(0,65.5),(8,63.5),(15,60.5)]:
 cuts.append(Manifold.cylinder(3.5,1.65,1.65,circular_segments=40).rotate((90,0,0)).translate((x,-17.4,z)))
# Windows beside central arch tower.
for x in [-22,22]:
 for z in [10,22,36,48]:cut(x,-17,z,5.5,3.2,7)
# Entrance loggia projects forward. Two central columns support balcony/label beam.
add(0,-21,18.4,31,13,3.4)
for x in [-13,-8,8,13]:column(x,-25,5.3,1.1,13.4)
cut(0,-19,5.4,22,4,12)
# Broad approach terrace and stairs, with solid-backed low balustrade.
add(0,-21,2.8,47,20,2.8)
for i in range(4):add(0,-30+i*2,2.8,29,2.3,.7+i*.7)
for x in [-21,21]:add(x,-22,5.3,2.2,15,3.2)
# Front balcony rail: coarse fused relief, no unsupported hairline pickets.
add(0,-26.9,21.5,30,1.5,2)
for x in range(-13,14,4):add(x,-26.9,21.4,1.4,1.5,3.8)
# Photographed west-side return windows at shallow front-block cutoff.
for side in [-1,1]:
 for yy in [4,11]:
  for z in [12,28,39,49]:cut(side*64,yy,z,3.2,4.6,6)
# Back is an explicit cut surface, not an invented complete rear elevation.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
