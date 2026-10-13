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

def roundedbox(x,y,z,w,d,h,r=2):
 pts=[]
 for cx,cy,angle in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
  for a in np.linspace(angle,angle+90,9):pts.append((x+cx+r*math.cos(math.radians(a)),y+cy+r*math.sin(math.radians(a))))
 return CrossSection([pts]).extrude(h).translate((0,0,z))
# NCHU library LAKESIDE FRONT WING / CORNER SECTION.
# 2024 ground photo + aerial on the library's 2020 event page establish two corners.
# Intentionally truncated at y=23; not an assertion about unobserved rear elevations.
add(0,0,0,150,72,3)
# Elevated front wing and discreet base-level columns behind visible glass.
add(0,10,2.8,138,26,7.2)
for x in [-64,-47,-31,-14,3,20,37,54,65]:add(x,-7.5,3,2.2,3.2,10)
# Left glass-fronted short block and taller opaque left end.
add(-45,5,10,43,37,60)
add(-65,7,3,6,34,77)
# Broad continuous horizontal brise-soleil on the left block: real relief, min1.0.
cut(-44,-13.5,11,37,2.5,53)
for z in range(13,65,4):details.append(box(-44,-14.2,z,39,3.1,1.0))
for x in [-56,-44,-32]:details.append(box(x,-13.9,11,1.1,2.5,53))
# Upper recessed terrace with open air under the overhanging eave.
add(-45,6,70,39,29,10)
cut(-45,-8.5,72,35,4.5,6.8)
for x in [-60,-47,-34]:details.append(box(x,-9.3,72,1.4,3.8,6.8))
add(-45,1.6,79.5,45,37,1.7)
# Tall narrow stair/sign blade separates horizontal glazing from vertical long wing.
add(-20,4,3,11,38,81)
# Narrow glazed side strip beside the sign blade, deliberately backed and thickened.
cut(-25.1,-15,14,2.2,2.4,57)
for z in range(16,70,6):details.append(box(-25.1,-15.3,z,2.2,2.4,1.0))
add(-19.5,-15.3,34,7.5,1.1,42)
# Long right wing. Deep, tall narrow window ribs are the photographed dominant feature.
add(24,8,10,78,30,54)
for x in range(-11,60,3):cut(x,-7,14,1.7,3.4,45)
# Long intermediate roof cornice and top-storey windows set back under large eaves.
add(24,7.5,63,81,32,2.4)
add(24,10,64.8,78,26,11.2)
for x in range(-10,61,7):cut(x,-3,67,4.8,3.2,6.3)
add(24,6,75.3,84,36,1.8)
# Right end wall seen in the aerial: groups of vertical slits plus small clerestory slots.
for y in [0,4,8,12]:cut(63,y,15,2.4,1.6,40)
for y in [-2,3,8,13]:cut(63,y,61,2.4,1.7,2.7)
# Left end corner seen in the 2024 ground photograph: tall narrow glazed strips.
for y in [-2,5,12]:cut(-68,y,15,2.2,2.5,48)
for y in [-2,3,8,13]:cut(-68,y,70,2.2,1.7,3)
# Raised rooftop glass/back block and end penthouse seen in the aerial.
# The recessed roof terrace in front remains genuinely open at the top.
add(10,18,76.5,74,10,9)
for x in [-5,3,11,19,27]:cut(x,13,79,5.5,2.3,4.7)
add(10,18,84.8,77,12,1.4)
add(46,15,76,20,16,15)
for x in [39,44,49,54]:cut(x,7,84,2,2.2,4)
# Opaque roof end to left of the recessed top terrace.
add(-60,13,80,13,18,6)
# Roof rail parapet 1.2mm; horizontal cap attached throughout to underlying cornice.
add(25,-11.5,77,81,1.2,2)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
