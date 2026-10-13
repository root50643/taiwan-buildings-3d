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
# Entrance-end study only: hall depth truncated; no full-building claim.
add(0,0,0,150,105,3)
# low auditorium block left; rear cut face intentionally undecorated.
add(-29,9,2.8,72,64,49)
add(-29,9,51,78,69,3)
# Lower glazed entry wall is set far behind two prominent outer piers.
add(20,10,2.8,55,43,41)
for x in [1,19,37]:cut(x,-11.5,4,14,4,30)
for z in [13,23]:add(19,-12,z,54,1.1,1.1)
# Tall brick stair tower on right front with a glazed narrow outer strip.
add(52,4,2.8,24,50,81)
add(52,4,83,26,52,1.5)
for z in [5,21,37,53,69]:
 cut(63,4,z,4,8,12)
 cut(61,-21,z,5,3,12)
# Two-storey high open portal and gallery, glass backed well behind it.
for x in [-10,39]:add(x,-29,3,4,6,48)
add(15,-21,49,61,24,3)
add(15,-23,36,58,17,2.8)
# upper gallery remains a deep open recess; front solid balustrade.
add(15,-31,38,54,2,4.5)
for x in [3,18,33]:add(x,-21,39,1.6,2,11)
# Curve balcony on left portal corner joins the main hall, not separate shell.
bal=Manifold.cylinder(2.5,9,9,circular_segments=40).translate((-17,-23,36))
parts.append(bal)
ring=Manifold.cylinder(6,9,9,circular_segments=40)-Manifold.cylinder(7,7.3,7.3,circular_segments=40).translate((0,0,-.5))
parts.append(ring.translate((-17,-23,38)))
# Roof clerestory and small rear stepped volume observed above hall.
add(-20,15,53.5,25,23,8)
for x in range(-29,-9,4):cut(x,3.5,56,2.1,3,3.6)
add(-20,15,61,27,25,1.5)
# High side ribbon, little lower wall fenestration; avoid imagined window grids.
cut(-64,10,39,4,48,6)
for i in range(4):add(15,-40+i*2,2.8,60,2.5,.7+i*.8)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
