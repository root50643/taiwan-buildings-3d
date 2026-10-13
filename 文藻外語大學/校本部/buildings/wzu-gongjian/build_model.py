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
# Gongjian former library: three distinct window strata over entrance hall.
add(0,0,0,150,110,3)
add(0,9,2.8,120,68,90)
# Front piers divide broad glazed panels; decorated spandrel panels are backed relief.
for x in [-43,-14,15,44]:
 for z,h in [(28,6),(48,10),(70,16)]:
  cut(x,-25,z,24,3.4,h)
  for dx in [-8,0,8]:details.append(box(x+dx,-25,z,1.1,3.2,h))
  if z==70:details.append(box(x,-25,z+8,24,3.2,1.1))
 for z in [37,60]:
  for xx in [x-6,x+6]:
   outer=[(xx-5,z+1),(xx-4,z),(xx+4,z),(xx+5,z+1),(xx+5,z+5),(xx+4,z+6),(xx-4,z+6),(xx-5,z+5)]
   inner=[(xx-3.8,z+1.5),(xx-3.2,z+1.1),(xx+3.2,z+1.1),(xx+3.8,z+1.5),(xx+3.8,z+4.5),(xx+3.2,z+4.9),(xx-3.2,z+4.9),(xx-3.8,z+4.5)]
   details.append(profile(outer,-25.7,2.0)-profile(inner,-27,3.0))

for x in [-59,-29,1,30,59]:add(x,-25.5,22,1.8,2,69)
# Visible right flank: narrow windows on lower floors and tall windows on top floor.
for z,h in [(28,5),(49,5),(70,15)]:
 for y in [-15,0,15,30]:cut(60,y,z,3.4,10,h)
# Entrance recess below small traditional hipped canopy, two substantial columns.
cut(-2,-25,3,32,7,19)
for x in [-23,20]:column(x,-33,3,1.6,18)
hip(-2,-31,21,58,20,4.8)
# Shallow traditional eave at the main flat terrace, not a generic pitched roof.
add(0,9,92.4,128,75,2.2)
# Thickened traditional eave lip: shallow run with lifted endpoints, not a flat box.
def upturned_lip(cx,cy,z,half,depth,rot=False):
 p=[(-half,z+2.6),(-half+3,z+.8),(-half+9,z),(half-9,z),(half-3,z+.8),(half,z+2.6),(half,z+4.1),(half-3,z+2.3),(half-9,z+1.5),(-half+9,z+1.5),(-half+3,z+2.3),(-half,z+4.1)]
 m=profile(p,0,depth)
 if rot:m=m.rotate((0,0,90))
 parts.append(m.translate((cx,cy,0)))
for yy in [-27,45]:upturned_lip(0,yy,91,67,7)
for xx in [-60,60]:upturned_lip(xx,9,91,39,7,True)
upturned_lip(-2,-39.5,20.5,30,4.5)
# Terrace parapet with open horizontal slots, perimeter posts tied to cap beam.
for y in [-28,46]:
 add(0,y,94.4,126,1.7,5)
 for x in range(-53,54,16):cut(x,y,95.5,12,3,2)
for x in [-62,62]:
 add(x,9,94.4,1.7,75,5)
 for y in [-18,-2,14,30]:cut(x,y,95.5,3,12,2)
for x in [-62,-46,-30,-14,2,18,34,50,62]:
 for y in [-28,46]:add(x,y,94,2.1,2.1,7)
for i in range(6):add(-2,-47+i*2,2.8,44,2.3,1+i*1.3)
# Back intentionally simplified, no copied front window rows.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
