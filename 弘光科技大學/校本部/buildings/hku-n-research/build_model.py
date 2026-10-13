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
# N research building: contractor photograph and 2024 signs/map identity.
add(0,0,0,150,112,3)
# L-shape creates the visible open-air forecourt rather than a filled rectangular block.
add(-20,22,2.8,92,31,75)
add(52,3,2.8,28,69,75)
# Rounded glazed stair/atrium tower at the interior corner, above six-level wings.
parts.append(Manifold.cylinder(82,18,18,circular_segments=96).translate((32,22,3)))
# Six long window bands and thick downstand brick spandrels.
for z in [14,25,36,47,58,69]:
 for x in range(-58,28,11):
  cut(x,6.5,z,8.5,5,5.8)
  details.append(box(x,5.8,z,1.05,5.5,5.9))
 add(-20,3.8,z+6.5,94,5,1.25)
 if z>=36:
  for y in [-24,-12,0]:cut(38,y,z,5,8.7,5.8)
# Actual staggered left-wing balcony fronts; terraces remain open behind low solid rails.
for z,xc,w in [(25,-31,40),(36,-30,38),(47,-31,39),(58,-38,48)]:
 add(xc,0,z,w,14,1.8)
 add(xc,-6.3,z+1.6,w,1.4,3.6)
 cut(xc,-6.4,z+2.4,w-7,1.6,1.1)
# Curved glass bands with robust fused mullions.
for z in [32,43,54,65,76]:
 outer=Manifold.cylinder(7,18.5,18.5,circular_segments=96)
 inner=Manifold.cylinder(8,16,16,circular_segments=96).translate((0,0,-.5))
 cuts.append((outer-inner).translate((32,22,z))^box(32,10,z,40,26,7))
 for deg in range(185,356,25):
  a=math.radians(deg);add(32+17*math.cos(a),22+17*math.sin(a),z,1.3,1.3,7.2)
parts.append(Manifold.cylinder(2,19,19,circular_segments=96).translate((32,22,84)))
# Ground-floor arcade under left bar, deep but backed by rear envelope.
for x in range(-56,22,13):cut(x,6.5,3,9.5,12,8)
# Low glass-clad entrance hall, with a broad open garage portal below.
add(27,-14,2.8,55,28,25)
cut(30,-28.5,3,39,13,10)
for z in [15,20]:cut(27,-30, z,49,9,3.7)
for x in range(4,52,8):details.append(box(x,-28,14,1.1,2.4,12))
# Sloping cheeks of ramp are approximations; no separate sculpture included.
for x in [-4,59]:
 parts.append(profile([(x-4,3),(x+4,3),(x+4,23),(x-4,23)],-24,18))
add(-20,22,77,95,34,2)
add(52,3,77,31,71,2)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
