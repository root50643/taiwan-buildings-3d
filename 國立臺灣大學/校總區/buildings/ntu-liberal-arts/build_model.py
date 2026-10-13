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
# Long two-storey historic facade with three lower and three upper arches.
add(0,0,0,150,68,3)
add(0,6,2.8,136,40,26)
hip(0,6,28,139,43,6)
add(0,-15,2.8,31,9,29)
gable(0,-15,31,35,9,9)
# Projected ground portico and upper balcony; no unsupported miniature balustrades.
add(0,-23,2.8,29,10,14.8)
for x in [-9,0,9]:
 arch_cut(x,-28,3.1,6.5,12,6)
 arch_cut(x,-19.5,20,6,9,2.4);arch_trim(x,-19.5,20,6,9)
add(0,-26.8,17,30,2,1.4)
for x in [-61,-53,-45,-37,-29,-21,21,29,37,45,53,61]:
 arch_cut(x,-14,18,4.6,9,1.6);arch_trim(x,-14,18,4.6,9)
 cut(x,-14,5,4.6,1.6,8)
# Shallow front pilasters and banding read from photograph, simplified repeats.
for x in [-65,-57,-49,-41,-33,-25,25,33,41,49,57,65]:add(x,-14.4,4,1.1,1.3,23)
add(0,6,3,137,41,1)
step(0,-31,33)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
