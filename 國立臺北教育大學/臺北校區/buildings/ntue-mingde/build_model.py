"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. Public plan outlines guide massing; interiors are not reconstructed.
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
# Mingde: three storeys, long narrow footprint, observed staggered circular stair windows.
add(0,0,0,150,53,3)
add(0,0,2.8,138,28,32)
# Flat overhanging roof and shallow fascia, no unsupported claim of pitched roof.
add(0,0,34,142,32,1.6)
# Left long-facade stair panel has 3+2 staggered circular openings, not floor rows.
for x,zs in [(-63,[8,18,28]),(-54,[13,23])]:
 for z in zs:
  cuts.append(Manifold.cylinder(4,2.5,2.5,circular_segments=40).rotate((90,0,0)).translate((x,-12,z)))
# Three photo-supported classroom groups; intervening tree-hidden bays left neutral.
for x in [-30,0,30]:
 for z in [7,17,27]:
  cut(x,-14,z,15,4.0,5.1)
  details.append(box(x,-14,z,1.1,2.5,5.1))
# Broad light-coloured structural wall bands, backed shallow relief only.
for x in [-41,-11,19,42]:add(x,-14.6,3,2.1,2,31)
# Opposite long elevation in photo A: three visible broad window groups.
# The photographed circle at its near-end lower level is retained alone;
# tree-hidden upper round windows are not copied from photo B.
for x in [-30,0,30]:
 for z in [7,17,27]:
  cut(x,14,z,15,4.0,5.1)
  details.append(box(x,14,z,1.1,2.5,5.1))
for x in [-41,-11,19,42]:add(x,14.6,3,2.1,2,31)
cuts.append(Manifold.cylinder(4,2.5,2.5,circular_segments=40).rotate((90,0,0)).translate((-63,16,8)))
# Central access and shallow canopy are visible on photo A's long elevation.
cut(0,14,3.1,13,7,8)
add(0,17,11,22,8,1.5)
for i in range(3):add(0,20-i*1.3,2.8,21,1.8,.55*(i+1))
# Observed short end: two unequal window groups at upper floors plus entrance canopy.
for y,w in [(-7,5.5),(4,4.5)]:
 for z in [15,26]:cut(-69,y,z,4,w,5)
cut(-69,-6,3.2,4,7,8)
add(-71,-6,11,7,14,1.6)
# Far short end and tree-hidden areas are unobserved and left plain.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
