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
# N1. Two-storey pavilion, opposing official oblique exterior photos.
add(0,0,0,150,102,3)
add(5,4,2.8,108,61,53)
# Exposed stair-slot cut in the long brick face (backed, not internal reconstruction).
cut(12,-26.5,10,9,5,40)
add(5,4,55,111,64,1.6)
# Glazed lower left corner and recessed upper terrace.
cut(-37,-26.5,6,29,4,22)
cut(-49,1,6,4,41,22)
cut(-37,-23.5,31,30,10,22)
add(-38,-32,29,35,14,2.5)
# Balcony railing is a solid 2-mm parapet instead of fragile wires.
add(-38,-37.7,31,35,2,5)
# Right return balcony and its canopy, verified on the side photo.
cut(58,7,30,10,38,23)
add(60,7,29,14,43,2.5)
add(65.7,7,31,2,43,5)
add(57,7,54,23,46,2)
for y in [-12,26]:add(64,y,31,2.5,2.5,24)
for x in [-48,-38,-28]:details.append(box(x,-27.3,6,1.3,2.1,22))
# Ground-floor side entrance simplified.
cut(59,8,5,2.5,13,19)
# Public ramp and landing, with low print-safe edging rather than metal balusters.
ramp_x(-6,-38,2.8,108,10,5)
add(48,-37,3,12,13,5)
step(-41,-44,26,5)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
