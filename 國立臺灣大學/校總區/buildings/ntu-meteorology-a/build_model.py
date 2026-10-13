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
# S44 historic A hall: publicly photographed stepped volumes and roof, not B hall.
add(0,0,0,150,114,3)
add(20,8,2.8,80,46,71)
add(-42,8,2.8,44,46,43)
add(-10,-30,2.8,110,36,24)
# Broad lower terrace with low solid parapet. Depression is open sky, never an inner cavity.
for x in [-64,44]:add(x,-30,26.5,1.8,36,2)
add(-10,-48,26.5,110,1.8,2)
# Main flat roof and stepped head, based on high public oblique photographs.
add(20,8,73,83,49,1.4)
add(-42,8,45,47,49,1.4)
add(-8,8,73,21,46,14)
add(-8,8,86.5,23,48,1.3)
# Tall narrow stair strip with round opening in the upper head.
cuts.append(Manifold.cylinder(3,3.1,3.1,circular_segments=40).rotate((90,0,0)).translate((-8,-14,81)))
cut(-8,-15,54,5,3,16)
cut(-8,-15,31,5,3,12)
# Two high arched bays on the visible front, with lower rectangular portions.
for x in [20,44]:
 arch_cut(x,-15,50,9,19,3)
 cut(x,-15,31,9,3,14)
 details.append(box(x,-14.6,60,9.5,2,1))
 details.append(box(x,-14.6,50,1,2,18))
 add(x,-15.6,46,9,1.8,2)
# Two arched windows on the lower left wing.
for x in [-53,-32]:arch_cut(x,-15,30,8,13,3)
# Lower projecting terrace facade: rectangular windows and a low plain canopy.
for x in [-52,-25,2,29]:cut(x,-48,4.5,7,3,20)
add(-20,-51,20,35,13,1.8)
step(-20,-54,32,4)
# Right face seen from above: tall arched upper windows and bottom rectangles.
for y in [-7,9,25]:
 cuts.append(arch(0,0,50,8,19,3).rotate((0,0,90)).translate((60,y,0)))
 cut(60,y,31,3,8,14);cut(60,y,7,3,8,17)
 for z in [56,62]:details.append(box(59.5,y,z,2.5,8.5,1))
# The exposed stair to the taller roof is solid stepped, not a smooth ramp.
for i in range(12):add(6,-8+i*2,74,8,2.2,i+1)
# Modern equipment, exposed services and connections to B/C halls omitted.
# Unknown rear and narrow west openings intentionally plain.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
