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
# Q student dormitory/QUBE: contractor whole-building actual photo, built 2020.
# Six storeys including ground; five open balcony tiers are visible on lower side.
add(0,0,0,150,75,3)
add(0,7,2.8,138,31,62)
# Central circulation spine and asymmetric rooftop mechanical enclosure.
add(25,7,2.8,7,33,72)
add(5,16,64,26,15,10)
# Strong rooftop open frame with no sealed internal void.
for x in [-69,-39,-9,21,43,69]:add(x,-9,64,1.8,2.5,7)
add(0,-9,70,140,2.5,2)
for z in [15,25,35,45,55]:add(0,-10,z-.8,138,8,1.2)
# Five balcony rows. Privacy screens are materially perforated, deliberately coarsened.
for row,z in enumerate([15,25,35,45,55]):
 for col in range(16):
  x=-64+col*8.3
  if 16<x<34:continue
  cut(x,-9,z,7.0,8.5,8.2)
  # Solid side screen swaps position in blocks, as irregular observed facade.
  sign=-1 if (row+col//3)%3 else 1
  sx=x+sign*2.0
  details.append(box(sx,-11.5,z-.2,3.0,1.2,8.4))
  # Small rail retains openness; minimum freestanding rail 1.1mm.
  details.append(box(x-sign*1.5,-11.5,z-.2,3.6,1.2,1.6))
  # source screen holes simplified to 1.1mm openings separated by >=1.0mm webs.
  for zz in [z+1.2,z+3.6,z+6.0]:
   # Apply after screen union below.
   pass
# Ground floor openings and strong asymmetric two-storey projecting entry box.
for x in range(-63,67,11):
 if not 4<x<44:cut(x,-9,4,8,4.5,8)
add(24,-15,2.8,32,16,18)
cut(24,-23,3,24,7,8)
for x in range(10,40,3):cut(x,-23,13,1.25,3,6)
# Side returns have exposed circulation landings; rear is unobserved simple envelope.
for z in [15,25,35,45,55]:cut(-69,6,z,5,22,8)
add(0,7,64.5,140,33,1.5)
# Main solid and perforated screen strips are fused first, then perforations opened.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
for row,z in enumerate([15,25,35,45,55]):
 for col in range(16):
  x=-64+col*8.3
  if 16<x<34:continue
  sign=-1 if (row+col//3)%3 else 1;sx=x+sign*2.0
  for zz in [z+1.2,z+3.6,z+6.0]:solid=solid-box(sx,-11.5,zz,1.0,2.0,1.2)
# Photographed multi-storey entrance/circulation recess interrupts every balcony band.
solid=solid-box(25,-9,21,16,29,43.5)
# Recessed landings join the rear wall, never bridge the facade opening.
for z in [25,35,45,55]:solid=solid+box(25,4.8,z,16.2,4,1.2)
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
