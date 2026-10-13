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
# SB Minsheng: rounded corner stair/window bay and long stacked corridor facade.
add(0,0,0,150,91,3)
add(8,9,2.8,112,39,74)
# Rounded near-left corner, joined into the bar rather than a free cylinder.
parts.append(Manifold.cylinder(75,18,18,circular_segments=80).translate((-47,0,2.8)))
# Five curved window ribbons with heavy spandrel bands.
for z in [8,22,36,50,64]:
 outer=Manifold.cylinder(8,18.5,18.5,circular_segments=80).translate((-47,0,z))
 inner=Manifold.cylinder(8.4,16.4,16.4,circular_segments=80).translate((-47,0,z-.2))
 cuts.append((outer-inner)^box(-51,-10,z,35,27,8.2))
 for deg in [180,210,240,270,300]:
  a=math.radians(deg);details.append(box(-47+17.1*math.cos(a),17.1*math.sin(a),z,1.1,1.1,8))
# Deep long gallery bays, strong vertical piers extend past roof.
for z in [8,22,36,50,64]:
 cut(15,-10.5,z,88,6,8)
for x in [-28,-9,10,29,48,64]:add(x,-12,3,2.4,4.4,79)
for z in [18,32,46,60,74]:add(15,-11,z,99,3,1.8)
add(7,9,76.5,113,41,2)
# Visible rectangular stair-core wall rises well above the curved glazing bay.
# Source crops the very top: plain termination records visible height, not invented machinery.
add(-59,-1,2.8,12,31,101)
for z in [86,95]:cut(-59,-16.5,z,3.5,3,4)
add(-39,10,77.5,3,13,7)
# Small entrance at left transition, not a fabricated full-width portico.
cut(-29,-11,3,10,6,8)
step(-29,-27,25,3)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
