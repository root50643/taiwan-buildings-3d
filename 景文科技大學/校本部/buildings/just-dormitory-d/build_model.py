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
# D dormitory: official nine-storey photograph; shallow curved slab instead of five-floor pictogram.
add(0,0,0,150,79,3)
def front_y(x):return 10-0.0034*x*x
xs=np.linspace(-67,67,81)
poly=[(x,front_y(x)) for x in xs]+[(x,front_y(x)+28) for x in xs[::-1]]
parts.append(CrossSection([poly]).extrude(70).translate((0,0,2.8)))
# Nine ranks: first six have deep horizontal sunshade/balcony belts.
for z in [11,19,27,35,43,51]:
 ring=[(x,front_y(x)-1.8) for x in xs]+[(x,front_y(x)+1) for x in xs[::-1]]
 parts.append(CrossSection([ring]).extrude(1.4).translate((0,0,z)))
# Window modules follow tangent of the curved building, cut directly into outer skin.
for z in [5,13,21,29,37,45]:
 for x in np.arange(-61,63,8):
  angle=math.degrees(math.atan(-.0068*x))
  cuts.append(box(0,0,0,4.8,3.8,4.2).rotate((0,0,angle)).translate((x,front_y(x)+.4,z)))
# Upper three almost continuous glazed ribbons, with backed thin mullions.
for z in [54,61,68]:
 for x in np.arange(-62,64,5.2):
  angle=math.degrees(math.atan(-.0068*x))
  cuts.append(box(0,0,0,4.2,3.8,3.5).rotate((0,0,angle)).translate((x,front_y(x)+.4,z)))
# Vertical circulation strips stand proud at left third and far right, as seen.
for x in [-48,66]:
 angle=math.degrees(math.atan(-.0068*x))
 details.append(box(0,0,0,2.6,3.5,71).rotate((0,0,angle)).translate((x,front_y(x)+.3,3)))
# Broad recessed central entry, canopy and low steps.
cut(0,10.2,3,17,6,8)
add(0,5,10.5,24,14,1.8)
step(0,-3,26,4)
# Central narrow rooftop plant enclosure plus lower boxes visible at either end.
add(0,23,72.5,25,16,6)
for x in [-13,13]:add(x,23,72.5,3,17,9)
for x in [-50,54]:add(x,front_y(x)+18,72.5,10,11,4.5)
# Rear deliberately left plain; no mirrored unknown window schedule.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
