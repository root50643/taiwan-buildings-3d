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
# Stepped science/mathematics hall: low left wing, intermediate core and taller right bar.
add(0,0,0,150,113,3)
add(-41,15,2.8,50,64,62)
add(-7,14,2.8,22,66,91)
add(13,7,2.8,20,81,103)
add(42,0,2.8,42,95,109)
# Two-storey projecting entrance pavilion before stair-stepped facade.
add(7,-39,2.8,32,27,29)
cut(7,-52.5,3,17,3,12)
cut(7,-52.5,18,26,3,8)
# Main facade individual bays, horizontal high clerestory slots.
for x,front,h in [(-57,-17,61),(-40,-17,61),(-23,-17,61),(-7,-19,89),(13,-33.5,101),(30,-47.5,108),(48,-47.5,108)]:
 for z in range(9,h-6,15):
  if x==13 and z<33:continue
  cut(x,front,z,12,3,7)
  cut(x,front,z+8,12,3,2.4)
# Front returns show side openings and depth offsets, not an uninterrupted rectangular mass.
for z in [38,53,68,83]:cut(3,-27,z,3,8,7)
# Roofline small ventilation slots only where visible.
for x in [-11,-3,10,17]:cut(x,-20 if x<0 else -34,96 if x>0 else 85,3,3,2.4)
step(7,-55,30,3)
# Rear silhouette and depth estimated; no invented rear windows.
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
