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
# S48 original four-storey Food Science building front, excluding S49 R&D annex.
add(0,0,0,150,86,3)
add(0,5,2.8,136,49,67)
add(0,5,69,138,51,1.5)
# Long front has grouped upper glazing separated by broad brick-like spandrels.
for z in [23,40,57]:
 for x in [-55,-34,-13,26,48]:
  if z==23 and x==26:continue
  cut(x,-19.5,z,16,3,9)
  details.append(box(x,-19.1,z,1,1.9,9))
  details.append(box(x,-19.1,z+6,15.5,1.9,.9))
for x in [-57,-41,-25,-9,51,64]:
 cut(x,-19.5,5,11,3,12)
 details.append(box(x,-19.1,5,1,1.9,12))
# Off-centre entrance bay beneath a broad solid fascia, with visible glazed band above.
add(22,-21,3,35,8,32)
cut(22,-25,4,23,3,14)
for x in [15,22,29]:details.append(box(x,-24.6,4,1.1,2,14))
cut(22,-25,25,29,3,9)
for x in [14,22,30]:details.append(box(x,-24.6,25,1,2,9))
add(22,-24,18.5,35,10,5.5)
# Low side ribbon windows and tall blind piers documented in left oblique.
for y in [-12,6,22]:
 for z in [10,29,46,63]:cut(-68,y,z,3,11,4)
for y in [-20,-2,15,29]:add(-68,y,3,1.6,2,67)
for z in [20,37,54]:add(0,-19.6,z,137,1.6,1.3)
# No invented rear window layout, roof plant, signage or attached food-R&D building.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
