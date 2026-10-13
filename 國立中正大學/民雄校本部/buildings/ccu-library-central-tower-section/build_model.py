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

# Central library tower + its entrance portico. Low three-storey east/west units omitted.
add(0,0,0,150,136,3)
add(0,5,2.8,108,76,69)
# Central brick stepped front pediment and flank roof shoulders.
parts.append(profile([(-50,70),(50,70),(50,76),(31,76),(31,82),(0,101),(-31,82),(-31,76),(-50,76)],-25,16))
add(-47,24,69,14,40,20);add(47,24,69,14,40,20)
add(0,30,68,80,28,11)
# Low rear projecting loggia, deep open bays, and semicircular upper reading-room drum.
add(0,45,2.8,62,24,60)
for x in [-23,-7,9,25]:
 for z in [11,24,37]:cut(x,56, z,12,4,9)
for x in [-24,-12,0,12,24]:cut(x,56,51,7,4,7)
column(0,40,59,19,22)
# Backed curved glazing around drum, interrupted by robust piers.
for ang in range(10,171,15):
 a=math.radians(ang);x=19*math.cos(a);y=40+19*math.sin(a)
 cuts.append(box(0,0,65,5.6,3,11).rotate((0,0,ang-90)).translate((x,y,0)))
# Recessed upper back galleries with roof framing.
for x in [-29,29]:
 cut(x,43,72,17,3.5,5)
# The main entrance pavilion stands forward with four tall columns and open undercroft.
add(0,-47,28,112,26,5)
for x in [-53,-18,18,53]:add(x,-58,3,3.8,5,26)
for x in [-53,53]:add(x,-37,3,3.8,5,26)
# Facade wall of portico and central triangular glazed gable.
add(0,-58,31,112,3.5,10)
gable(0,-48,39,44,23,15)
cuts.append(profile([(-18,40),(18,40),(0,51)],-60,3.0))
for x in [-43,-30,30,43]:cut(x,-60,33,8,3,6)
for x in [-11,0,11]:details.append(box(x,-60,40,1.4,3,8 if x==0 else 3.5))
# Retained tall recessed entrance behind the open portico.
cut(0,-33,3,50,3.5,26)
for x in [-18,-6,6,18]:details.append(box(x,-33.5,3,1.5,3.2,26))
# Upper glazed apex panel observed in the frontal photograph.
cut(0,-33.5,86,27,3,8)
cuts.append(profile([(-13.5,94),(13.5,94),(0,101)],-33.5,3))
details.append(box(0,-33.5,86,1.5,3,14))
# Upper front arrangement: broad glazed panel, four short central windows and flank pairs.
cut(0,-34,70,41,3.5,10)
for x in [-16,-8,0,8,16]:details.append(box(x,-34,70,1.4,3.5,10))
for x in [-17,-6,6,17]:cut(x,-34,60,7,3.5,6)
for x in [-42,42]:
 for z in [44,58,75]:cut(x,-34,z,8,3.5,8)
for z in [43,57,68]:add(0,-33.5,z,108,2.3,1.5)
# Rear and side windows follow photo-visible uneven large-core/window groups.
for x in [-45,-35,35,45]:
 for z in [9,19,29,39,49,59,73]:cut(x,43,z,5,3,6.2)
for side in [-1,1]:
 for y in [-23,-10,3,16,29]:
  for z in [11,23,35,47,59]:cut(side*54,y,z,3,8,5.8)
# Multiple short front stairs. Garden/pillars in distant foreground are not part of tower.
for i in range(5):add(0,-66+i*1.6,2.8,104,2,.55*(i+1))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert str(solid.status())=='Error.NoError' and solid.volume()>0 and len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
