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
# Scholars residence: stepped facade and five asymmetrical sawtooth roof planes.
add(0,0,0,150,89,3)
# Long lower gallery remains open in front of recessed inner wall.
add(0,13,2.8,134,44,29)
for x in [-63,-36,-9,18,45,64]:add(x,-18,3,2.6,2.6,26)
for z in [15,29]:add(0,-12,z,135,15,2.3)
for x in [-51,-24,3,30,56]:cut(x,-9,5,20,3.2,8)
# Four stepped blocks, each with its distinct recessed brick-screen panel ranks.
for xa,xb,h in [(-67,-44,73),(-44,-19,80),(-19,7,88),(7,67,95)]:
 x=(xa+xb)/2;w=xb-xa
 add(x,7,29,w,53,h-29)
 for z in [h-52,h-34,h-16]:
  if w>40:
   for xx in [x-15,x+15]:cut(xx,-19.5,z,25,3.4,10)
  else:cut(x,-19.5,z,w-7,3.4,10)
  add(x,-20,z-3,w,1.8,1.7)
 # Sparse printable grill relief hints at actual perforated brick screens, backed by wall.
 for z in [h-52,h-34,h-16]:
  for xx in range(int(xa+5),int(xb-4),4):
   details.append(box(xx,-19.5,z,1.0,4,10))
 for z in [h-52,h-34,h-16]:
  for zz in [z+3,z+7]:details.append(box(x,-19.5,zz,w-7,4,1.1))
# Five visible tilted roof sheets: solid structural wedge tied into roof, no floating strips.
for xa,xb,z in [(-69,-45,73),(-45,-19,80),(-19,8,88),(8,37,95),(37,69,95)]:
 parts.append(profile([(xa,z-.3),(xb,z-.3),(xb,z+3),(xa,z+10)],7,58))
# Small lower entrance awning and forecourt steps.
add(0,-23,13.5,134,9,1.8)
for x in [-63,64]:add(x,-24,3,2.6,2.6,12)
for i in range(4):add(0,-35+i*2,2.8,88,2.3,1+i*.8)
# Neighboring Zhishan and gym walls omitted; rear is a simplified envelope.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
