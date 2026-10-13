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
# High rear teaching bar, stepped low return, prominent capped end tower and Hakka courtyard halls.
add(0,0,0,150,132,3)
add(5,35,2.8,111,26,84)
add(-49,5,2.8,25,72,40)
add(61,34,2.8,16,29,101)
# Seven-storey inner frontage; frame bays and horizontal band beneath upper two levels.
for x in range(-39,50,11):
 for z in [9,20,31,42,53,64,75]:cut(x,21.5,z,8.5,3,7.4)
for x in range(-44,55,11):details.append(box(x,20.2,65,1.7,2.7,21))
add(5,20,85.5,113,3.5,2)
# Small intermediate eave along the high bar, fused to facade.
add(5,20,62,112,5,1.7)
# End tower slit glazing and projecting cap platform with a shallow pitched roof.
cut(65,19,10,4.2,3,76)
for z in range(18,81,12):details.append(box(65,20,z,4.8,2,1))
add(61,34,87,22,34,2.2)
for x in [55,67]:add(x,34,102,1.8,28,6)
gable(61,34,108,24,34,5)
# Low return side, open gallery recess at its upper storey.
cut(-35.8,3,29,3.5,57,8)
for y in range(-19,29,12):details.append(box(-35.2,y,29,3,1.7,9))
# Two low gable-front pavilions on courtyard edge. Roof ridge bump suggests Hakka parapet.
for x in [-38,35]:
 add(x,-27,2.8,24,35,20)
 gable(x,-27,22.7,28,38,7)
 add(x,-44.9,28.4,3,2.4,2.4)
 cut(x,-45,3,9,3,13)
 for xx in [x-9,x+9]:cut(xx,-45,5,3.5,3,11)
 # Deep side entry arcade, backed by inner solid wall.
 cut(x+12,-28,3,6,27,14)
 for y in [-40,-28,-16]:details.append(box(x+12,y,3,2,2,16))
# Low covered colonnade joins the pavilions; open below, firmly joined through the base.
add(0,-34,18,58,10,2.2)
for x in [-24,-12,0,12,24]:add(x,-37,3,1.8,2,15.3)
# Traditional shallow roof profile above connecting arcade.
gable(0,-34,20,58,12,2)
# Rear/outer wall is plain because contractor photos emphasize courtyard and lake sides.
step(35,-50,28,3)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
