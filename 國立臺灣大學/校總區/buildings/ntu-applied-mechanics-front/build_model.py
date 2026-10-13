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
# N59 principal front block only; not the full rear courtyard complex.
add(0,0,0,150,82,3)
add(0,8,2.8,119,44,69)
for x in [-66,66]:add(x,10,2.8,15,49,69)
# Shallow segmental pediment on flat-roof front block.
poly=[(-40,71),(-40,74),(-34,74),(-34,77)]
poly += [(x,77+3.4*(1-(x/34)**2)) for x in range(-34,35,2)]
poly += [(34,74),(40,74),(40,71)]
parts.append(profile(list(reversed(poly)),-13,3))
# Circular pediment oculus, solid-backed.
cuts.append(Manifold.cylinder(3,3.1,3.1,circular_segments=48).rotate((90,0,0)).translate((0,-13,75)))
# Three regular upper window bands; broad windows separated by paired narrow slits.
for z in [30,44,58]:
 for x,w in [(-48,11),(-33,3),(-26,3),(-14,11),(0,11),(14,11),(26,3),(33,3),(48,11)]:
  cut(x,-14,z,w,2.5,9)
  if w>5:
   details.append(box(x,-13.7,z,1,1.8,9))
   details.append(box(x,-13.7,z+4.5,w,1.8,.9))
for x in [-49,-36,36,49]:cut(x,-14,6,7,2.5,17)
for x in [-66,66]:
 for z in [8,24,40,56]:cut(x,-14.5,z,5,2,9)
# Glazed two-storey entry recessed into front; thick external portal frame.
cut(0,-14,5,32,3,32)
for x in [-10,0,10]:details.append(box(x,-13.7,5,1.1,2,32))
for z in [16,27]:details.append(box(0,-13.7,z,32,2,1))
opening=[(-16.5,3),(16.5,3),(16.5,28),(14,28),(14,31)]
opening += [(x,31+4*(1-(x/14)**2)) for x in range(14,-15,-1)]
opening += [(-14,28),(-16.5,28)]
portal=box(0,-24,3,45,20,42)-profile(opening,-24,22)
parts.append(portal)
# Lower colonnades follow gently angled outer entrance flanks; plain parapets simplified.
for side in [-1,1]:
 for i in range(3):
  x=side*(27+i*8);y=-23+i*1.5
  details.append(box(x,y,3,2.6,5,23))
 details.append(box(side*35,-20.5,26,29,10,5))
step(0,-36,66,5)
# Rear facade/roof annexes unobserved and excluded.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
