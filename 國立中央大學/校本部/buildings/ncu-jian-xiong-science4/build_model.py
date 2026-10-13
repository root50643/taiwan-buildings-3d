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
# Ten-storey L-shaped science block viewed across the lake; unknown outer back plain.
add(0,0,0,150,145,3)
add(-42,-3,2.8,32,118,110)
add(11,42,2.8,106,28,110)
# Curved interior-corner galleries, deliberately open recesses between robust slabs.
column(-26,28,2.8,14,110)
for z in np.arange(9,106,10.5):
 ring=Manifold.cylinder(7,15,15,circular_segments=64)-Manifold.cylinder(7,11.5,11.5,circular_segments=64)
 cuts.append(ring.translate((-26,28,z)) ^ box(-15,17,z,22,22,7))
# Facade grid along inner left wing.
for y in [-46,-34,-22,-10,2,14]:
 for z in np.arange(7,106,10.5):
  cut(-26,y,z,3,8,6.6)
  add(-24.5,y,z+7.5,3.5,10,1.5)
# Lake-facing back wing.
for x in [-8,4,16,28,40,52]:
 for z in np.arange(7,106,10.5):
  cut(x,28,z,8,3,6.6)
  add(x,26.5,z+7.5,10,3.5,1.5)
# Continuous strong vertical facade piers observed in official images.
for y in [-52,-40,-28,-16,-4,8,20]:add(-24.9,y,3,2.5,2.2,110)
for x in [-14,-2,10,22,34,46,58]:add(x,26.9,3,2.2,2.5,110)
# End cores taller than classroom bars, with narrow vertical glazing.
add(-43,-53,2.8,35,20,116)
add(61,42,2.8,12,31,116)
for z in range(7,116,11):
 cut(-36,-63,z,7,3,7)
 cut(61,26.5,z,4,3,8)
# Recessed rounded corner windows at the close end; curved silhouette coarse.
column(-36,-55,2.8,9,112)
for z in range(7,108,11):cut(-34,-64,z,10,3,6.5)
# Roof service boxes visible over inner junction; no guessed complete equipment layout.
add(-19,43,112,25,22,7)
add(-47,29,112,18,18,4)
# Small upward dish visible in official lake photograph, thickened opaque bowl.
add(36,42,112,8,8,8)
column(36,42,119,2.6,6)
rr=np.linspace(0,9,18)
pts=[(float(r),float(r*r/30)) for r in rr]+[(float(r),float(r*r/30-1.7)) for r in rr[::-1]]
parts.append(CrossSection([pts[::-1]]).revolve(64).translate((36,42,125)))
# Very fine dish feed tripod and unrelated small rooftop observing hut omitted.
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
