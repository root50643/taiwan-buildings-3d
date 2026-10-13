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
# Library/Information Building: documented entry corner segment.
# Based on M+ completed-building archival photograph and official 2016 entrance photo.
# Rear is an intentional plain sectional closure: no claim to complete building depth.
add(0,0,0,150,105,3)
# Lower ground glazing sits deeply behind pilotis / upper projecting wall.
add(0,9,3,122,50,20)
# Separate entrance columns and true open porch.
for x in [-21,8,38,64]:add(x,-29,3,3.2,3.8,26)
add(4,-19,20,120,26,12)
# Upper 3-level sawtooth front: wide wall panels step in front of narrow window slots.
add(0,7,31,135,67,51)
# Broad end walls are slightly taller. These are the library's key silhouette.
add(-59,0,29,20,69,55)
add(61,5,29,14,71,64)
# Left service tower appears behind the front massing.
add(-45,22,3,19,36,86)
# Each projecting front bay is a narrow window stack, NOT uniform strip windows.
for x,z0,height in [(-34,31,47),(0,31,54),(39,34,57)]:
 add(x,-28, z0,12,8,height)
 for z in [z0+4,z0+18,z0+32]:
  cut(x,-32.1,z,9,4.5,10)
  details.append(box(x,-32,z,1.1,4,10))
  details.append(box(x,-32,z+5,9,4,1.1))
 # Stout bottom sill becomes one joined volume.
 add(x,-31,z0,13.5,8,2)
# Narrow ground/mid openings visible beneath the overhanging front.
for x in [-21,8,38]:cut(x,-32,22,4,3,8)
for x in [-25,-11,3,17,31,45]:cut(x,-16,5,10,3,13)
# Characteristic sharply pitched entrance canopy over the offset left doorway.
gable(-29,-33,22,34,15,8)
cut(-29,-36,22,26,19,3.5)
# Side faces repeat the sawtooth window stacks progressively along the return.
for y in [-8,7,22,37]:
 add(67,y,34,7,11,47)
 for z in [37,51,65]:
  cut(70.4,y,z,4,8,10)
  details.append(box(70.2,y,z,3.5,1.1,10))
  details.append(box(70.2,y,z+5,3.5,8,1.1))
# Ground porch glazing on right return.
for y in [-6,9,24,38]:cut(61,y,6,3.5,10,11)
# Five broad entry steps extend over the entire porch frontage.
for i in range(5):add(9,-46+i*3,2.8,124,3.3,.8+i*.7)
# Horizontal stripe courses are shallow relief, not color textures.
for z in [40,54,68]:
 add(1,-27,z,132,1.3,1.3)
 add(67,5,z,1.3,64,1.3)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
