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
# Partial study: Fanglan entrance and five visible capsule-window bays only.
# Deliberate cut face at right: tree-obscured remainder is not reconstructed.
add(0,0,0,150,69,3)
add(10,4,2.8,112,36,68)
# Left stair entry and tall louver screen.
add(-54,4,2.8,24,36,74)
cut(-54,-14,4,17,5.5,30)
cut(-54,-14,39,18,6,34)
for z in [41,46,51,56,61,66,71]:add(-54,-17,z,20,7,1.8)
add(-54,-17,35,23,8,2.2)
# Five visible rounded-rectangle windows per storey, preserving 2+3 grouping.
def capsule(x,y,z,w,h,depth):
 r=w/2;pts=[]
 for t in np.linspace(0,math.pi,25):pts.append((x+r*math.cos(t),z+h-r+r*math.sin(t)))
 for t in np.linspace(math.pi,2*math.pi,25):pts.append((x+r*math.cos(t),z+r+r*math.sin(t)))
 return profile(pts,y,depth)
for x in [-27,-12,13,28,43]:
 for z in [12,43]:
  cuts.append(capsule(x,-14.2,z,7.2,18.5,3))
  details.append(capsule(x,-14.4,z-1,9.4,20.5,1.7)-capsule(x,-14.8,z,7.2,18.5,2.5))
  details.append(box(x,-14.5,z+3.2,8.4,3.8,1.2))
# Wall joint between first pair and following triple and story division.
cut(0,-14.4,3,1.1,1.2,66)
cut(10,-14.4,34.5,110,1.1,1.0)
# End elevation has one capsule at each level, shown by official side photo.
for z in [12,43]:cuts.append(capsule(2,0,z,7.2,18.5,3).rotate((0,0,90)).translate((-66,0,0)))
add(0,4,70,132,37,1.6)
# Ramp as broad slab strips, no submillimetre free railings.
for i in range(5):add(-54,-28+i*2.2,2.8,22,2.5,.7+i*.55)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
