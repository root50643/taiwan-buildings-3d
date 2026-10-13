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
# I library: long chamfered western end from map; three screen-window ranks above colonnaded ground.
add(0,0,0,150,79,3)
poly=[(-69,-8),(-64,-18),(49,-18),(49,23),(-64,23),(-69,13)]
parts.append(CrossSection([poly]).extrude(43).translate((0,0,2.8)))
# Real photo's right-hand vertical tower rises past recessed top floor.
add(58,2,2.8,19,43,64)
add(58,2,66,22,46,2)
for z in [12,25,38,51]:cut(58,-19.5,z,11,3.6,4)
# Front glazed ground level interrupted by substantial rectangular piers.
for x in [-58,-36,-14,8,30]:cut(x,-17.5,3,17,4.5,10)
# Three ranks of very narrow tall openings; mullions and panels are deliberate relief.
for z in [16,26,36]:
 for x in range(-61,47,7):cut(x,-18,z,3.2,3.2,7)
for x in range(-64,49,7):add(x,-18.4,15,1,1.2,29)
add(-8,-18,44,117,2.7,1.5)
# Recessed fifth level and long oversailing slab visibly above lower facade.
add(-6,10,44,109,25,10)
for x in range(-52,48,16):cut(x,-2.6,46,12,3,6)
add(-6,10,53.5,114,31,1.8)
# Small off-centre rooftop room, not a full extra storey.
add(-27,13,55,27,17,7)
for x in [-34,-21]:cut(x,4.5,56,4,2.7,4)
# Entry canopy observed in separate official dusk photograph.
add(-24,-23,12.5,37,16,1.6)
step(-24,-31,40,4)
# Rear is deliberately blank because no sufficiently clear rear photo was obtained.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
