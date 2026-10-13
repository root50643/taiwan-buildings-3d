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
# Hui-Sun Hall, 1993-generation FRONT BLOCK SECTION in 2021/2024 photos.
# Full auditorium chamber, rear roof and solar equipment are not represented.
add(0,0,0,150,64,3)
# Broad forecourt plinth and recessed entry stairs.
add(0,3,2.8,139,34,2.1)
for i in range(5):add(0,-27+i*2,2.8,58,2.3,.6*(i+1))
# Recessed glazed ground face behind a genuine open colonnade.
add(0,12,4.6,132,21,17.7)
for x in [-52,-32,-12,12,32,52]:cut(x,1.5,6,15,2.7,7)
# Lower first-floor bar with continuous recess and structural mullions.
parts.append(roundedbox(0,5,14.5,139,32,8.8,2.2))
cut(0,-11,17,134,3.0,4.0)
for x in range(-64,65,7):details.append(box(x,-11.3,17,1.1,2.6,4.0))
# Upper broad two-storey bar oversails the recessed lower structure.
parts.append(roundedbox(0,5,26.5,142,38,22.8,2.7))
for z in [31,41]:
 cut(0,-14,z,108,3.5,4.0)
 for x in range(-52,53,4):details.append(box(x,-14.4,z,1.0,3.0,4.0))
 # Paired small square end windows distinguish the heavy rounded ends.
 for x in [-65,-59,59,65]:cut(x,-14,z,2.4,3.4,3.0)
# Deep horizontal notch under upper bar remains open along the whole frontage.
# Back wall at y=1.5 connects upper bar, central gateposts and ground structure.
add(0,11,22,136,23,7)
for x in [-65,-43,-21,0,21,43,65]:add(x,-9,4.5,2.1,3.2,22.5)
# Three heavier entrance piers plus connected horizontal entry canopy.
for x in [-19,0,19]:add(x,-12.5,4.5,2.6,4.5,22.2)
add(0,-12,13,56,8,1.8)
# Shallow slab bands / sign plaque are deliberately connected to the actual facade.
add(0,-14.4,37,140,1.2,1.1)
add(0,-14.4,25.8,139,1.2,1.2)
add(0,-14.7,37.3,37,1.1,2)
# Roof thickness retained; rear is the section's deliberately plain cut boundary.
add(0,5,48.7,140,36,1.5)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
