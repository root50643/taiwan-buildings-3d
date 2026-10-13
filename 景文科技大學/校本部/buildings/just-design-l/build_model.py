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
# L Design: photograph observed white classical facade, high paired piers and round portico.
add(0,0,0,150,91,3)
add(0,10,2.8,135,42,46)
# Four levels; central and flanking towers rise above low wings.
add(0,8,45,31,44,15)
for x in [-29,29]:add(x,-10,3,19,17,54)
for x in [-29,29]:
 gable(x,-18,56.7,21,4,8)
 arch_cut(x,-18.5,55,12,7,3)
 for dx in [-5.6,0,5.6]:cut(x+dx,-18.5,46,2.7,3.2,8)
 # Tall front pier pairs, terminating at the projecting upper window bay.
 for dx in [-6.5,6.5]:column(x+dx,-20,3,1.6,43)
 cut(x,-18.5,7,7,3.4,34)
 for z in [18,29,40]:add(x,-19,z,9,1.8,1.4)
gable(0,-13,59.7,34,4,8)
arch_cut(0,-14,58,18,9,3.4)
add(0,-14,58,34,3.4,1.6)
for x in [-10,-3.3,3.3,10]:cut(x,-13.5,51,3.2,3.5,5)
# Semicircular portico with genuine open space beneath; rear half joins wall.
cap=Manifold.cylinder(2.8,18,18,circular_segments=80).translate((0,-10,27))
parts.append(cap)
for x,y in [(-14,-20),(-8,-25),(8,-25),(14,-20)]:column(x,y,3,1.4,25)
cut(0,-11,3,20,5,24)
# Upper recessed central bay with tall shallow glazing, backed by wall.
cut(0,-12,31,24,4,16)
for x in [-10,-5,5,10]:details.append(box(x,-11.5,29,1.4,3.5,19))
add(0,-13.5,47,28,4,1.8)
# Left/right wings visible in photo: three window ranks, upper arches and relief panels.
for x in [-60,-50,-40,40,50,60]:
 for z in [12,24]:cut(x,-11, z,6.7,3.3,8)
 arch_cut(x,-11,36,6.7,9,3.3)
for x in [-53,53]:
 add(x,-11,47,26,3,1.6)
 for dx in [-9,0,9]:gable(x+dx,-12,48.5,6,2,2.3)
# Newly inspected official high-angle photo 1789: roof pavilions are actual pitched volumes.
# Tall rear-central tower rises behind the smaller front pediment.
add(0,9,58,22,22,8)
gable(0,9,65.7,25,25,11)
arch_cut(0,-2.1,63,13,10,3)
# Roof pavilions near each end sit within the long wings, rather than at the extreme edge.
for x in [-53,53]:
 add(x,1,45,13,25,11)
 gable(x,1,55.7,16,28,8)
 arch_cut(x,-11.5,46,8.5,10,3.3)
for r,z in [(20,3),(19.5,3.7),(19,4.4)]:parts.append(Manifold.cylinder(.9,r,r,circular_segments=80).translate((0,-10,z)))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
