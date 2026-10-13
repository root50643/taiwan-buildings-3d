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
# Wenhui: measured-plan-derived compound footprint, two-storey main section.
# x transverse, y depth: principal entrance at negative y.
add(0,0,0,108,150,3)
# Front two-storey end 11.9m wide; middle 9.9m; rear 13.9m one-storey terraces.
add(0,-45,2.8,83.3,29.4,42)
add(0,0,2.8,69.3,63,42)
add(0,43,2.8,97.3,36.1,21)
add(0,43,23,44.1,36.1,21.8)
# Main entry projecting granite frame and deep glazing recess.
add(0,-61,2.8,31.5,7,42)
cut(0,-64,4,24,3.8,36)
# Upper glazing split 4 columns by 4 rows; low door side lights.
for x in [-8,-1,6]:details.append(box(x,-62.7,5,1.2,3.0,35.8))
for z in [17,24,31,38]:details.append(box(0,-62.7,z,25.5,3.0,1.2))
add(0,-65.5,20.5,35,8,1.6)
# Outer side window pairs documented in side photo, with recessed upper lintels.
for side in [-1,1]:
 for y in [-42,-16,10]:
  for z in [8,29]:cut(side*(41.65 if y==-42 else 34.65),y,z,3.2,10,10)
# Plan-documented low terrace decks, backed parapets 1.4mm.
for x in [-36,36]:
 add(x,44,23,25,34,1.8)
 add(x+(-11.5 if x<0 else 11.5),44,24,1.4,35,2.2)
 add(x,60.5,24,25,1.4,2.2)
# Wall top coping, no invented rooftop plant or unknown rear fenestration.
add(0,-45,44,84.5,30.5,1.4)
add(0,0,44,70.5,63,1.4)
add(0,43,44,45.5,36.5,1.4)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
