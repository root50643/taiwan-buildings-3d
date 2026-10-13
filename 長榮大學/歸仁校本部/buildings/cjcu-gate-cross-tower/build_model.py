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
# Gate clock/cross tower: two thin vertical slabs with cross-shaped perforations.
# This is an independent landmark structure, NOT a teaching building or Shen-Hsing Bell Park.
add(0,0,0,64,55,4)
for x in [-7,7]:
 add(x,0,3.8,3.6,24,146.2)
 # Cross apertures through each slab, using documented broad-side silhouette.
 cut(x,0,106,5.8,1.9,27)
 cut(x,0,123,5.8,9,2.5)
 # Distinct scattered small wall openings; sizes adjusted for the miniature.
 for y,z,w,h in [(-5,17,1.6,2.1),(4,32,2,2.6),(-4,48,1.7,1.9),(3,67,2.0,2.6),(-3,82,1.7,2.2),(5,91,1.8,2.1),(1,58,1.5,2.0)]:
  cut(x,y,z,5.8,w,h)
# Lower tie slab seen half-way down the open gap.
add(0,0,57,14.6,7,2.8)
# High transverse tie sits behind cross perforations; preserves the large open gap.
add(0,-6,123,14.6,2,2.5)
# Small grounded plinth ledge; no imported bells, clocks, logos or precision decorative relief.
add(0,0,3.8,24,30,1.2)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
