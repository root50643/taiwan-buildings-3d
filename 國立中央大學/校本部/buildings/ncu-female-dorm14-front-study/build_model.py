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
# Asymmetric stepped primary facade. This is an entrance-massing study, not a fully surveyed dormitory.
add(0,0,0,150,83,3)
modules=[(-56,48),(-40,72),(-24,90),(-8,108),(8,120),(24,120),(40,78),(56,78)]
for x,h in modules:
 add(x,7,2.8,16,49,h)
 # Offset primary volumes and large projecting balcony/screen bands.
 for z in np.arange(8,h-4,10):
  if x==-8 and z<65:continue
  add(x,-18,z,15,4,7)
  for dx in [-4.8,0,4.8]:cut(x+dx,-20,z+1.2,3.5,3,4.6)
  # Narrow lower clerestory kept behind the projecting opaque frame.
  cut(x,-17.5,z-2,13,3,1.5)
# Deep central entrance canyon, remains backed rather than pretending to know the whole court.
cut(-8,-5,3,18,45,62)
# Deeply recessed rear wall has only visible coarse openings; no invented interior rooms.
for z in [8,21,35,50]:
 for x in [-13,-7,-1]:cut(x,17.5,z,3.5,3,6)
# Low internal bridges visible behind entrance arch.
for z in [17,30,45]:details.append(box(-8,7,z,18,3,2))
# Half-round entrance roof on robust columns, not fine glazing spokes.
for x in [-19,3]:add(x,-26,3,2.5,3,42)
arch_trim(-8,-26,34,22,18)
# Rectangular plinth wall with sparse open arcade bays in front of low glazed band.
for x in [-56,-38,-20,8,26,44,61]:
 add(x,-29,3,5,5,25)
 add(x+3.7,-29,3,2.4,5,18)
# Low front canopy linking the piers to the main facade; entry left open.
for x,w in [(-43,39),(32,60)]:add(x,-22,12,w,12,1.7)
step(-8,-36,25,3)
# Rear facade kept plain: 2008 opposite-view photograph is not fully registered to the front footprint.
# Roof machinery and antenna masts omitted, not inferred from old distant image.
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
