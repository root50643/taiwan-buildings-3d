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
# Two classroom/research bars and high bridge frame, plus round lecture projection.
add(0,0,0,134,150,3)
for x in [-39,39]:add(x,0,2.8,28,118,60)
# Back connection and broad overhead bridging volume form the monumental opening.
add(0,47,3,106,24,60)
add(0,0,54,106,118,9)
# Upper roof light/plant panels as shallow, backed roof wells.
for x in [-31,31]:cut(x,-3,61,25,53,4)
# Inward gallery walkway levels remain open underneath.
for z in [15,27,39]:
 add(0,20,z,55,7,2.3)
 # low solid rail behind each slab edge
 add(0,16.5,z+2.0,55,1.4,2)
# Long exterior window bands with mullions, documented aerials.
for side in [-1,1]:
 for z in [8,20,32,44,54]:
  cut(side*53,0,z,3,106,6.6)
  for y in range(-49,50,7):details.append(box(side*53,y,z,4.0,1.0,6.6))
# Inner elevations visible through central opening.
for side in [-1,1]:
 for z in [9,21,33,45]:
  for y in [-46,-32,-18,-4,10,24]:
   if not (side==1 and y==-46 and z<33):cut(side*25,y,z,3,10,6)
# Round low volume sits beside one bar at the courtyard-facing end.
roundvol=Manifold.cylinder(31,20,20,circular_segments=96).translate((26,-53,2.8))
parts.append(roundvol)
# curved glazed band beneath rooftop terrace
for z in [25,31]:
 details.append((Manifold.cylinder(1.3,20.8,20.8,circular_segments=96)-Manifold.cylinder(1.5,18,18,circular_segments=96).translate((0,0,-.1))).translate((26,-53,z)))
cut(26,-53,33,31,31,5)
# Terrace rim with open top, not enclosed cavity.
rim=(Manifold.cylinder(2.2,20.5,20.5,circular_segments=96)-Manifold.cylinder(3,18.6,18.6,circular_segments=96).translate((0,0,-.3))).translate((26,-53,33))
details.append(rim)
# Rooftop mechanical block, approximate grouping from actual aerial pixels.
add(15,24,62,22,20,7)
add(-11,22,62,17,19,4)
step(-12,-65,22,4)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
