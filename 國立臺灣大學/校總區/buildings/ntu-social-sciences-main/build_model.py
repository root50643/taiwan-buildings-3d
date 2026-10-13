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
# E11 main 168m slab only. Low library pavilion is explicitly excluded.
# Official ratio 168:22.3:31.2 controls main slab; robust external framing is enlarged.
add(0,0,0,150,38,2.5)
add(0,0,2.4,142,18.85,26.37)
# Central open exterior terrace spans three levels, with visible massive columns.
cut(0,0,10.2,86,25,8.2)
for x in [-40,-30,-20,-10,10,20,30,40]:
 for y in [-8.8,8.8]:details.append(box(x,y,10,1.4,1.6,8.7))
# Documented central conference-volume exterior within the terrace, not interior rooms.
details.append(box(0,1,10,16,13,8.8))
# Offset two-storey large upper openings, framed by a central mullion.
cut(-48,0,22.0,10.8,25,5.2)
cut(48,0,18.7,10.8,25,5.2)
for x,z in [(-48,22),(48,18.7)]:details.append(box(x,0,z-.2,1.15,18.85,5.6))
# Shallow backed panels, simplified to one recess per structural bay.
for side in [-1,1]:
 for row in range(8):
  z=3.05+row*3.2
  for i in range(40):
   x=-69.225+i*3.55
   if (-43<x<43 and 9<z<19) or (-54<x<-42 and z>=22) or (42<x<54 and 18<z<24):continue
   cut(x,side*9.43,z,2.65,1.9,2.35)
 # Broader backed lower terrace on reverse, rather than invented rooms.
 if side==1:
  cut(0,9.43,3,135,5,5.7)
  for x in range(-66,67,11):details.append(box(x,8.4,2.7,1.5,4.3,6.3))
# Strong continuous horizontal slab bands and front/rear external fins.
for side in [-1,1]:
 for row in range(9):
  z=2.5+row*3.2
  # Do not bridge the central three-storey opening with imaginary floor bands.
  if 9<z<18:
   for x in [-58,58]:add(x,side*9.7,z,26,1.5,.8)
  else:add(0,side*9.7,z,143,1.5,.8)
 for i in range(41):
  x=-71+i*3.55
  if abs(x)<43:
   add(x,side*9.65,18.3,1.0,1.4,10.6)
   add(x,side*9.65,2.4,1.0,1.4,7.9)
  else:add(x,side*9.65,2.4,1.0,1.4,26.5)
# End facade has three main bays, subdivided as shallow louver-like panels.
for side in [-1,1]:
 for z in [3,6.2,9.4,12.6,15.8,19,22.2,25.4]:
  for y in [-6.2,0,6.2]:cut(side*71,y,z,2.2,4.8,2.3)
add(0,0,28.1,143,20.1,.9)
# No speculative rooftop machinery or low library roof pattern.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
