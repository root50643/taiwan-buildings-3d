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
# N24: original Wang Da-hong front block, excluding later rear annex.
add(0,0,0,150,102,3)
add(0,7,2.8,130,61,68)
# Front central recessed louver field, bounded by broad mostly blank side wings.
cut(0,-23.5,18, 60,7,50)
# Three narrow vertical brick mullion bands separating horizontal sunshades.
for x in [-30,-10,10,30]:details.append(box(x,-25,17,3.8,6,54))
for x in [-20,0,20]:
 for z in range(21,68,3):details.append(box(x,-24,z,17,8,1.2))
# Rounded outside leading corners of the heavy wings.
for x in [-50,50]:
 add(x,-24,3,30,12,68)
 parts.append(Manifold.cylinder(68,7,7,circular_segments=40).translate((x+(8 if x>0 else -8),-25,3)))
# Solid side walls end above central roof level as in exterior photographs.
for x in [-61,61]:add(x,3,70,8,63,5)
# Entrance, large thick canopy, three glazed door bays and simple steps.
for x in [-20,0,20]:cut(x,-23.5,5,14,4,11)
for x in [-26,-13,0,13,26]:details.append(box(x,-23.5,5,1,2,11))
details.append(box(0,-30,17,74,20,2.8))
step(0,-43,69,6)
# Unverified rear is left plain; no imagined windows/equipment/internal plan.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
