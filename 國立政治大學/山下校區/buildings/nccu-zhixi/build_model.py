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
# C-shaped two-storey historic hall, with genuinely open forecourt.
# The public 2021 inventory plans establish the complete outline, not interiors.
add(0,0,0,150,82,3)
WING_D=53;WING_W=32;CENTER_W=38
add(0,16,2.8,132,17,24)
for x in [-66+WING_W/2,66-WING_W/2]:add(x,16-(WING_D-17)/2,2.8,WING_W,WING_D,24)
# Central portal breaks forward from the rear bar into the forecourt.
add(0,5,2.8,CENTER_W,15,25.2)
# Three-panel Guofu / five-panel Zhixi high glazing, deliberately distinguishable.
for x in [-13.6, -6.8, 0.0, 6.8, 13.6]:
 cut(x,-2.5,14,5.3,3.0,9)
 details.append(box(x,-3.0,18,5.3,2.0,1.0))
cut(0,-2.5,3, CENTER_W-5,5,9.6)
for x in [-CENTER_W/2+2,CENTER_W/2-2]:add(x,-3.0,3,2.0,3.0,25)
add(0,-3.3,26.5,CENTER_W+1,3,1.5)
add(0,-3.8,12.0,CENTER_W+1,5.5,1.3)
# Entrance steps are integrated into the solid.
step(0,-9,CENTER_W-4,3)
# Window bays and brows along visible courtyard elevations.
for x in [-27,27]:
 for z in [6,18]:cut(x,7.5,z,8,2.6,6)
for side in [-1,1]:
 inner=side*(66-WING_W)
 for y in [4,-8]:
  for z in [6,18]:cut(inner,y,z,3,8,6)
 # End walls with two separate windows, as seen in the inventory side image.
 for x in [side*(66-WING_W/2)-6,side*(66-WING_W/2)+6]:
  for z in [6,18]:cut(x,24.5-WING_D,z,7,3,6)
 # Slender facade piers and broad floor-level eyebrow remain attached.
 add(inner,16-(WING_D-17)/2,14,1.5,WING_D,1.2)
# Hipped tile roof outline and connected thickened eaves; no individual sub-mm tiles.
add(0,16,26.4,135,20,1.2)
hip(0,16,27.2,135,20,4)
for x in [-66+WING_W/2,66-WING_W/2]:
 add(x,16-(WING_D-17)/2,26.4,WING_W+3,WING_D+3,1.2)
 parts.append(CrossSection.square((WING_W+3,WING_D+3),center=True).extrude(4,scale_top=(.03,.68)).translate((x,16-(WING_D-17)/2,27.2)))
# Rear has only outline evidence; blank wall is a declared simplification.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
