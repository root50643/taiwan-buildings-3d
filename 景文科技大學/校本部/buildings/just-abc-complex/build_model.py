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
# ABC connected complex: ONE model, not three duplicates of the shared A/C pictogram.
# Source 1785 shows central B, inner balcony faces of both wings, rear links and two courts.
add(0,0,0,150,109,3)
# Three prongs joined along the far spine; photo/map-derived depths are estimates.
add(0,31,2.8,138,17,47)
for x in [-54,54]:add(x,1,2.8,28,74,50)
add(0,6,2.8,41,50,57)
# B's front window groups, strong pilasters and narrow central upright motif.
for z in [7,17,27,37,47]:
 for x,w in [(-14,8),(-5,6),(5,6),(14,8)]:cut(x,-19,z,w,3.5,7)
for x in [-10,10]:details.append(box(x,-19.4,17,2.4,2,42))
add(0,-19.5,23,3.7,2,36)
for z in [26,36,46]:cut(0,-20, z,1.5,2.7,5)
# Raised curved cap at the upper end of the centre line.
parts.append(arch(0,-19.5,54,5.4,6,2))
# Broad shallow roof, triangular raised pediment with genuine dark recess behind it.
hip(0,6,59.4,47,54,5.8)
gable(0,-19.5,60,45,4.5,11)
cuts.append(profile([(-14,61.5),(14,61.5),(0,68.4)],-21.3,2.7))
# Photo's two broad side slots at the shoulder of the pediment.
for x in [-18,18]:cut(x,-20,59.4,5.5,4,3.2)
# Rooftop centre stair room and paired tanks shown clearly in 1785.
add(0,19,60,16,15,13.6)
for x in [-5,5]:column(x,20,73.4,2,4)
# Inner courtyard sides: broad balcony openings split by structural posts.
for side in [-1,1]:
 for z in [8,18,28,38,47]:
  for y in [-26,-9,8,25]:cut(side*40,y,z,3.8,12,5.5)
  add(side*39.8,1,z+5.2,2.3,71,1.2)
 # Top circulation room; no invented detailed exterior end face.
 add(side*54,18,52.6,23,18,5)
# Exposed rear link faces inside each courtyard show long open strips.
for x in [-29,29]:
 for z in [10,21,32,43]:cut(x,22.5,z,16,3.4,5.5)
# Curving front entry canopy, integrated platform and two round columns.
add(0,-25,16,48,15,2.4)
parts.append(Manifold.cylinder(2.4,17,17,circular_segments=80).translate((0,-25,16)) ^ box(0,-35,16,38,22,2.5))
for x in [-20,20]:column(x,-30.5,3,1.6,14)
cut(0,-19,3,19,6,11)
for i in range(6):add(0,-46+i*2,2.8,30,2.3,1+i*1.1)
# A/C far ends, exterior sides and unseen rear window patterns deliberately plain.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
