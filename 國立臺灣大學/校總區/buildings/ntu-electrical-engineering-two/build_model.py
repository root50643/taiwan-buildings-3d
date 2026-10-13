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
def shallow_arch(x,y,z,w,h,depth,rise):
 pts=[(x-w/2,z),(x+w/2,z),(x+w/2,z+h-rise)]
 pts += [(xx,z+h-rise+rise*(1-((xx-x)/(w/2))**2)) for xx in np.linspace(x+w/2,x-w/2,31)[1:]]
 return profile(pts,y,depth)
# E3: long principal public facade and side return; unseen rear plain.
add(0,0,0,150,80,3)
add(0,6,2.8,137,51,62)
add(0,6,64,139,53,1.3)
# Rhythmic paired openings, highest ones round headed, lower rows rectangular.
for x in [-58,-40,-22,22,40,58]:
 for xx in [x-3,x+3]:
  for z in [8,21,34,47]:
   if z==47:arch_cut(xx,-19.5,z,4.5,12,2.6)
   else:cut(xx,-19.5,z,4.5,2.6,9)
   details.append(box(xx,-19.2,z+5,4.9,1.7,.9))
# Slight projecting full-height bays and shallow curved parapet caps.
for x in [-58,0,58]:
 for xx in [x-8.4,x+8.4]:add(xx,-20.3,3,1.8,2.5,62)
 if x==0:
  gable(0,-20.4,64,28,2.7,4.5)
  cuts.append(shallow_arch(0,-20,60.5,15,3.7,3,2.8))
 else:parts.append(shallow_arch(x,-20.4,64,19,5,2.7,3.3))
# Broad recessed central vertical circulation band: backed, not open interior.
cut(0,-19.5,19,21,3.4,41)
for z in [19,29,39,49,59]:details.append(box(0,-19.4,z,22,2.6,1.8))
for x in [-8,-4,0,4,8]:details.append(box(x,-18.2,19,.9,1.9,41))
# Low rectangular portal, arched cap; modest solid stairs.
add(0,-23,3,38,14,15)
cut(0,-30,3.5,29,3.3,11)
parts.append(shallow_arch(0,-23,17,25,5,14,4))
step(0,-35,36,4)
# Side pair windows on the documented end, lower rows and arched top.
for y in [-11,3,17,27]:
 for z in [8,21,34,47]:
  if z==47:cuts.append(arch(0,0,z,6,12,3).rotate((0,0,90)).translate((-68.5,y,0)))
  else:cut(-68.5,y,z,3,6,9)
  details.append(box(-68.1,y,z+5,2,6.5,.9))
# A blank far narrow end and rear explicitly reflect missing image evidence.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
