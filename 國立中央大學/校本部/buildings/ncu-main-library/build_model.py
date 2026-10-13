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
# Photo-based eight-storey main library; no inferred inner rooms.
add(0,0,0,150,110,3)
add(0,5,2.8,126,76,105)
# Deep framed recess across front; top header and side piers remain.
cut(0,-32,18,103,6,80)
# Recessed window fields, 9 bays and six rows visible in distant official view.
for x in range(-44,45,11):
 for z in [31,42,53,64,75,86]:
  cut(x,-28.5,z,8.2,3,7.8)
  details.append(box(x,-28.5,z+3.8,8.4,4.0,.9))
  details.append(box(x,-28.5,z,1.0,4.0,8.0))
# Fine top band under the heavy cornice.
for x in range(-48,49,6):cut(x,-31.5,97,4.2,5,4.3)
# Ground entry and stepped projecting rectilinear porch/reading bays.
add(0,-37,3,111,15,19)
for x in [-44,-33,-22,-11,0,11,22,33,44]:cut(x,-45,7,8,4,11)
for x,h,w in [(-33,18,19),(-16,30,18),(0,18,19),(16,30,18),(33,18,19)]:
 add(x,-38,20,w,13,h)
 cut(x,-45,23,w-4,3,h-5)
 # projecting facade frame standing over the shallow bay
 add(x,-45,20+h,w+2,2,1.4)
for x in [-54,-43,-23,-7,7,23,43,54]: add(x,-45,3,1.4,2.0,19)
# Prominent round window, ring backed by solid wall.
parts.append(Manifold.cylinder(19,7.5,7.5,circular_segments=64).rotate((90,0,0)).translate((0,-26.5,48)))
ring=Manifold.cylinder(2,7.5,7.5,circular_segments=64)-Manifold.cylinder(3,6.0,6.0,circular_segments=64).translate((0,0,-.5))
cuts.append(Manifold.cylinder(4,6.0,6.0,circular_segments=64).rotate((90,0,0)).translate((0,-44.0,48)))
details.append(box(0,-45.0,41,1.0,2.0,14));details.append(box(0,-45.0,47.5,14,2,1))
# Visible right flank has sparse slot windows rather than a copied front grid.
for z in [18,32,46,60,74,88]:cut(63,20,z,3,9,4)
add(0,5,107,128,78,2)
step(0,-51,100,3)
# Rear intentionally plain: no reliable reverse-elevation pixels.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
