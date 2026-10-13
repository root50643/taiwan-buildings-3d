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

def prism(poly,z,h):return CrossSection([poly]).extrude(h).translate((0,0,z))
def rotated_box(x,y,z,w,d,h,deg):return box(0,0,0,w,d,h).rotate((0,0,deg)).translate((x,y,z))

def arc_poly(ro,ri,a0=0,a1=180,n=80,cx=0,cy=-28):
 aa=np.radians(np.linspace(a0,a1,n+1));return [(cx+ro*math.cos(t),cy+ro*math.sin(t)) for t in aa]+[(cx+ri*math.cos(t),cy+ri*math.sin(t)) for t in aa[::-1]]
# Eight-storey administration hall: deep monumental entrance, ground pilotis and central open court.
add(0,0,0,150,118,3)
add(0,0,2.8,132,100,104)
# Complete court from public plan, open above base, not an enclosed hollow shell.
cut(0,4,3,46,47,115)
# The monumental front entrance is five floors high and genuinely deep.
cut(0,-45,3,62,29,78)
# Leave the rear wall of the entry recess and its glazed lower doorway.
add(0,-27,3,64,8,78)
cut(0,-32,4,31,5,27)
for x in [-13,-6,6,13]:details.append(box(x,-33,2.8,1.5,5.5,30))
details.append(box(0,-34,30.8,36,8,3))
for x in [-18,18]:details.append(box(x,-33,2.8,4,7,31))
# Structural portal and crossbeams remain freestanding in the entrance void.
for x in [-26,26]:details.append(box(x,-44,2.8,4.5,5,65))
for z in [53,67]:details.append(box(0,-44,z,57,6,3))
# Ground-level side pilotis keep the low undercroft open.
for x in [-49,49]:cut(x,-44,3,25,27,14)
for x in [-64,-36,36,64]:add(x,-49,3,4,5,16)
# The official oblique photograph shows the long ground-floor arcade as well.
for side in [-1,1]:
 cut(side*64,1,3,20,95,14)
 for y in [-44,-26,-8,10,28,45]:details.append(box(side*64,y,2.8,4,4,15))
# Upper two-floor crown and flanking square office windows.
for x in [-59,-48,-37,37,48,59]:
 for z in [24,38,52,66,85,98]:cut(x,-50,z,7,4,7)
for x in [-25,-12,0,12,25]:
 for z in [85,98]:cut(x,-50,z,8,4,7)
 # Upper window groups have narrow vertical slots between the two rows.
 cut(x,-50,91,2.7,4,7)
# Recessed portal backing windows, not a filled generic face.
for z in [39,53,67]:
 for x in range(-25,26,10):cut(x,-31,z,7,3.2,7)
# Side elevations' deep loggia bays, supported by the outer frame.
for side in [-1,1]:
 for y in range(-41,46,7):
  for z in [22,36,50,64,84,98]:cut(side*66,y,z,9,4.7,8)
# Inward-facing gallery strips explicitly follow the real court outline.
for side in [-1,1]:
 for y in [-10,5,20]:
  for z in [22,36,50,64,84,98]:cut(side*23,y,z,4,9,7)
add(0,0,106.4,135,103,1.7)
cut(0,4,106,46,47,5)
# Broad flight of front stairs supports only the base, not the entrance void.
for i in range(7):add(0,-57+i*1.3,2.8,65,1.7,.5+i*.65)
# The unsighted far rear wall is deliberately plain, with full outline retained.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
# Public floor plan has a much longer side than the entry facade.
solid=solid.scale((1,1.7,1));bb=solid.bounding_box();scale=150/max(bb[i+3]-bb[i] for i in range(3));solid=solid.scale((scale,scale,scale))
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
