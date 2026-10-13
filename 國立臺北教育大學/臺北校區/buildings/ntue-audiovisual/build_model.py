"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. Public plan outlines guide massing; interiors are not reconstructed.
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
# Five-storey AV building, front and both end perspectives from official pp30-31.
add(0,0,0,150,100,3)
# Plan-derived irregular footprint: long teaching bar, extended west wing and two rear stair cores.
add(0,-24,2.8,136,35,82)
add(-52,8,2.8,32,77,82)
add(-30,16,2.8,14,42,82)
add(43,13,2.8,31,37,82)
# Five-floor teaching facade: three broad lower window bands, a sparse slit storey, top horizontal slots.
for z in [7,23,39]:
 for x,w in [(-9,24),(20,21),(44,14)]:
  cut(x,-41.5,z,w,5.2,9)
  # Deliberately broad principal subdivisions; pane grid not treated as structural piers.
  details.append(box(x,-40,z,1.3,2.8,9))
for x in [-16,-9,9,16,34,41,53]:cut(x,-41.5,57,2.4,5,11)
for x,w in [(-12,17),(16,20),(44,19)]:cut(x,-41.5,75,w,5,4.5)
# Tall left entrance recess with glazing retained deep behind its projecting brick frame.
cut(-51,-41.5,3,25,23,30)
for x in [-58,-51,-44]:cut(x,-30,5,5.2,3.8,24)
for z in [39,55,71]:cut(-52,-41.5,z,25,5,9)
# Right end: two-storey covered corner and three upper broad window groups.
cut(60,-38,3,16,18,29)
for z in [39,55,71]:cut(60,-41.5,z,9,5,9)
# Corner pier, beams and glazing divisions added after opening subtraction.
details.append(box(65,-43,3,3.2,3.2,30))
for z in [16,29]:details.append(box(-51,-29.4,z,25,1.8,1.5))
for x in [-58,-51,-44]:details.append(box(x,-29.4,3,1.5,1.8,28))
# The right side lower horizontal band is visible on p31; other side/rear windows remain unknown.
cut(68,-8,23,5,20,7)
# Flat roof edge without conjectural mechanical equipment.
for x,y,w,d in [(0,-42,137,1.8),(-68,1,1.8,88),(68,-24,1.8,36),(-52,46.5,33,1.8),(43,31.5,32,1.8)]:add(x,y,84.3,w,d,1.8)
for i in range(3):details.append(box(-51,-49+i*1.8,2.8,30,2.1,.6*(i+1)))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
