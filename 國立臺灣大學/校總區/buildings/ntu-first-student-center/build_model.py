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

def ell(x,y,z,rx,ry,h):return Manifold.cylinder(h,1,1,circular_segments=128).scale((rx,ry,1)).translate((x,y,z))
def circle_cut(x,y,z,r,d):cuts.append(Manifold.cylinder(d,r,r,circular_segments=24).rotate((90,0,0)).translate((x,y+d/2,z)))
def ramp_x(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x+w/2,z+h)],y,d))
# M11. Historic front block; later rear annex and rooftop equipment excluded.
add(0,0,0,150,84,3)
# Seven-bay width and shallow public-facing historic mass from official description.
add(0,5,2.8,144,56,28)
# Continuous folded outline read from official illustrated full facade:
# five full ridges with rising half-folds at the two ends.
for x in [-48,-24,0,24,48]:gable(x,5,30,24.4,59,8.5)
parts.append(profile([(-72,30),(-60,30),(-72,38.5)],5,59))
parts.append(profile([(60,30),(72,30),(72,38.5)],5,59))
# Ground and upper level grid windows; robust backed recesses.
for x in [-65,-48,-24,24,48,65]:
 cut(x,-23,5,14.5,2,10)
 cut(x,-23,20,14.5,2,8)
 for xx in [x-4,x,x+4]:details.append(box(xx,-23,5,1,1.4,10))
 for xx in [x-4,x,x+4]:details.append(box(xx,-23,20,1,1.4,8))
 for z in [9,13,23,26]:details.append(box(x,-23,z,14.5,1.4,.9))
cut(0,-23,4,11,2.5,13)
cut(0,-23,20,14.5,2,8)
# Door centerline and round handles represented as minimal relief.
details.append(box(0,-23.5,4,1,1.5,13))
for x in [-1.5,1.5]:details.append(Manifold.cylinder(.8,1.3,1.3,circular_segments=20).rotate((90,0,0)).translate((x,-23.4,7)))
# Exterior columns at fold valleys and high projecting roof edge.
for x in [-60,-36,-12,12,36,60]:add(x,-25,3,2.4,3.6,28)
for x in [-48,-24,0,24,48]:
 circle_cut(x,-24.5,33,1.2,3)
add(0,-24,17.5,144,2.5,1.7)
step(0,-34,37,5)
ramp_x(-34,-32,2.8,38,9,4)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
