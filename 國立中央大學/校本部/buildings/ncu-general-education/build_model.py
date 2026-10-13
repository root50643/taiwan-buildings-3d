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
# Low long teaching block with rounded stair-core edge and suspended entrance volume.
add(0,0,0,150,100,3)
add(7,8,2.8,112,63,62)
# Left stair core has a rounded front outer corner rather than a box silhouette.
core=box(-51,5,2.8,27,73,68)
corner=Manifold.cylinder(68,6,6,circular_segments=48).translate((-58.5,-25.5,2.8))
core=core-box(-62,-29,2,9,9,70)+corner
parts.append(core)
# Upper front teaching band projects over deep two-storey entry bay.
add(10,-24,34,103,16,31)
cut(-13,-25,3,49,18,29)
for x in [-31,0]:details.append(box(x,-32,3,2.6,4,31.4))
# Gallery floor behind the portico; openings remain under and above it.
details.append(box(-13,-16,18,48,10,2.2))
# Repetitive horizontal classroom glazing with continuous intermediate lintels.
for z in [38,52]:
 cut(10,-32.2,z,98,3,8)
 for x in range(-35,57,13):details.append(box(x,-32.2,z,1.4,3.5,8))
# Lower right windows, omitted where trees obscure far end.
for z in [7,22]:
 for x in [20,34,48]:cut(x,-23.5,z,10,3,7)
# Narrow stair-core side slots visible beside smooth rounded wall.
for z in [19,38,55]:cut(-40,-31,z,7,3,6)
add(10,-24,64.5,105,18,1.5)
step(-14,-40,47,3)
# Rear depth and outer unseen window placement simplified, no duplicated frontage.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
