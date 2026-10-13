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
# Photo map23: five-storey tan slab, left-of-centre glass bay; no invented rear facade.
add(0,0,0,150,108,3)
add(0,8,2.8,132,72,100)
# Central recessed glazed vertical entrance bay, framed by substantial piers.
cut(-17,-28,6,32,4,94)
for x in [-33, -1]:add(x,-29,3,2,3,102)
for x in [-26,-18,-10]:details.append(box(x,-28.1,5,1.1,3.7,95))
for z in [21,40,59,78,97]:details.append(box(-17,-28,z,31,3.7,1.8))
# Five ranks of paired rectangular glazing, in wall panels.
for z in [8,27,46,65,84]:
 for x in [-53,17,43]:
  if x==-53 and z<40:continue
  cut(x,-28,z,17,3.4,9)
  details.append(box(x,-28,z,1.1,3.6,9))
# Left-of-glazing two-storey entry void: broad deep recess and exposed intermediate beam.
cut(-53,-26,3,23,16,38)
details.append(box(-53,-29,21,23,4,2.8))
# Right-hand side visible in oblique official photo, tall recessed repeated bays.
for y in [-18,0,18,36]:
 cut(66,y,8,3.5,12,86)
 for z in [21,40,59,78]:details.append(box(65.5,y,z,3.5,12,2))
add(0,8,102,135,75,2)
add(-17,-34,19,37,14,2)
step(-17,-42,38,3)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
