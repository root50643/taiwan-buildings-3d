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
# Three-storey Zhuangjing: deep front galleries and slotted solid balustrades.
add(0,0,0,150,86,3)
add(0,8,2.8,128,36,68.2)
# Broad gallery slabs and piers in front of a real recessed classroom wall.
for z in [7,28,49]:
 add(0,-16,z,133,16,2.3)
 for x in [-62,-42,-22,-2,18,38,61]:add(x,-21,z,2.8,2.8,22)
 add(0,-22,z+2.1,133,2,5.5)
 for x in [-52,-32,-12,8,28,49]:cut(x,-22,z+3.6,14,3.5,2.1)
 for x in [-52,-32,-12,8,28,48]:cut(x,-10,z+9,15,3,9)
# Ground entrance staircase is visibly offset to left in photo.
for i in range(6):add(-34,-35+i*1.7,2.8,25,2,.9+i*.75)
# Thin tiled shallow hipped cap; printed solid not individual tiles.
hip(0,3,70.5,142,53,4.8)
# Rooftop ventilation equipment groups visible above flat inner roof line.
add(-39,15,71,13,12,10)
for x in [13,29,45]:add(x,15,71,10,10,11)
# Short return gallery on the right end continues the railing slots.
for z in [7,28,49]:
 add(63,5,z,6,43,2.2)
 add(65,5,z+2.1,2,43,5.5)
 for y in [-9,6,20]:cut(65,y,z+3.6,3.5,9,2.1)
# Rear remains plain; no direct rear photo.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
