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
# N14 old gymnasium: front, oblique and official backstage photos.
add(0,0,0,150,134,3)
add(0,0,2.8,133,110,48)
# Massive rectangular portal frame at both ends, not a guessed pitched roof.
for y in [-55,55]:
 add(0,y,48,135,4,3)
 for x in [-64,64]:add(x,y,2.8,6,4,48)
# Front six perforated-screen panels interpreted as coarse backed grid relief.
for x in [-48,-32,-16,16,32,48]:
 for xx in [x-4.5,x-1.5,x+1.5,x+4.5]:
  for z in range(20,46,3):cut(xx,-55,z,1.8,2.5,1.8)
 add(x,-55,7,1.1,1.7,40)
 cut(x,-55,6,11.5,2,10)
 for xx in [x-3,x+3]:details.append(box(xx,-55,6,.9,1.6,10))
 details.append(box(x,-55,10,11.5,1.6,.9))
# Central tall glass bay and sheltered entrance.
cut(0,-54,6,15,4,41)
for x in [-5,0,5]:details.append(box(x,-54,6,.9,2,41))
for z in [17,27,37]:details.append(box(0,-54,z,15,2,.9))
details.append(box(0,-56,16,23,8,1.5))
step(0,-63,34,4)
# Rear stage elevation: broad blank centre, three windows each wing and high vents.
cut(0,55,5,20,4,11)
details.append(box(0,56,16,23,8,1.5))
for x in [-51,-39,-27,27,39,51]:
 for z,h in [(8,5),(20,10),(35,10)]:
  cut(x,54,z,9,3,h)
  details.append(box(x,54,z,1,1.8,h))
  details.append(box(x,54,z+h/2,9,1.8,1))
for x in range(-15,16,5):
 for z in [42,45]:cut(x,54,z,3.6,3,1.3)
for i in range(5):add(0,64-i*1.7,2.8,64,2,.7*(i+1))
# Side bays are deliberately simplified from oblique photographic evidence.
for x in [-66.5,66.5]:
 for y in [-39,-23,-7,9,25,41]:
  for z in [9,30]:cut(x,y,z,2,9,12)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
