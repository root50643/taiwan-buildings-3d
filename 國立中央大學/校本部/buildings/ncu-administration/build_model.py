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
# Four-storey administrative block. Depth is approximate; rear intentionally plain.
add(0,0,0,150,87,3)
add(0,5,2.8,130,55,43)
# Deep offset square sunshade lattice, physically recessed into the envelope.
for row in range(11):
 z=5+row*3.6
 for col in range(31):
  x=-60+col*4+(2 if row%2 else 0)
  if x>62:continue
  cut(x,-22.5,z,2.95,4.4,2.6)
# Irregular larger openings interrupt the lattice at visible positions.
for x,z,w,h in [(-26,29,11,7),(0,29,11,7),(23,14,14,7),(-16,10,9,7)]:cut(x,-22.4,z,w,4.6,h)
# Central projecting porte-cochere with deep entry opening and paired piers.
cut(8,-22,3,27,8,9)
add(8,-30,12,35,20,2.7)
for x in [-7,23]:add(x,-37,3,2.8,3.8,10)
add(8,-37,14.5,27,2.2,3)
step(8,-41,40,3)
# Continuous flat roof slab. The distant main-library tower is NOT an admin roof plant.
add(0,5,45.5,132,57,1.6)
# Left return observed behind trees, two broad shallow bands only.
for z in [13,25,37]:cut(-65,4,z,3.5,40,3)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
