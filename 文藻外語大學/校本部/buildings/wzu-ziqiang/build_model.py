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
# Three-storey Ziqiang, with visibly exposed zigzag end stairs.
add(0,0,0,150,94,3)
add(5,9,3,119,38,64)
for z in [3,24,45]:
 add(5,-17,z,124,16,2.2)
 for x in [-54,-34,-14,6,26,46,64]:add(x,-22,z,2.7,2.7,22)
 add(5,-23,z+2,124,2.0,5.3)
 for x in [-44,-24,-4,16,36,55]:cut(x,-23,z+3.4,13,3.5,2)
 for x in [-44,-24,-4,16,36,55]:cut(x,-10,z+9,14,3,8)
# Observed front entry interrupts the ground balustrade between two structural piers.
cut(36,-23,3,16,6,9)
cut(36,-10,5,14,4,13)
for i in range(5):add(36,-36+i*2.2,2.8,26,2.5,.45+i*.5)
# Exposed end stairs: solid 2.4mm flight slabs with open underside, tied by landings.
def stair_flight(y0,z0,y1,z1):
 p=[(y0,z0),(y1,z1),(y1,z1+2.4),(y0,z0+2.4)]
 if (y1-y0)<0:p=p[::-1]
 parts.append(profile(p,0,8).rotate((0,0,90)).translate((-62,0,0)))
stair_flight(-28,3,9,23.8)
stair_flight(9,24,-28,44.8)
stair_flight(-28,45,9,65.7)
for y,z in [(9,24),(-28,45),(9,66)]:add(-60,y,z-.8,17,10,4.1)
# Thick stair parapets follow flights, without closing the large under-stair void.
for y0,z0,y1,z1 in [(-28,3,9,23.8),(9,24,-28,44.8),(-28,45,9,65.7)]:
 p=[(y0,z0+2),(y1,z1+2),(y1,z1+6),(y0,z0+6)]
 if y1<y0:p=p[::-1]
 parts.append(profile(p,0,1.8).rotate((0,0,90)).translate((-65.1,0,0)))
hip(3,2,66.5,139,56,4.5)
add(45,20,66.4,10,11,9.4)
# Right end/rear simplified; linked adjacent building omitted at boundary.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
