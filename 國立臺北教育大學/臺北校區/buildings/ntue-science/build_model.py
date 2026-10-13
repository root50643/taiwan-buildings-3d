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
# Science hall T plan. Front arcade and vertical triple-arch central stair retained.
add(0,0,0,150,120,3)
add(0,-34,2.8,138,35,65)
add(0,19,2.8,31,76,65)
# Low parapets only; no inferred rooftop service buildings.
for y in [-51.5,-16.5]:add(0,y,67.2,139,1.5,1.7)
for x in [-69,69]:add(x,-34,67.2,1.5,36,1.7)
for x in [-15.5,15.5]:add(x,19,67.2,1.5,76,1.7)
add(0,57,67.2,32,1.5,1.7)
# Front five upper rows; side wings visible as 3 groups each, window depth not glass.
for x in [-61,-48,-35,-22,22,35,48,61]:
 for z in [20,32,44,56]:
  cut(x,-51.5,z,10.4,4.5,7.2)
  details.append(box(x,-52,z-1.0,10.8,2.2,1.1))
 # Ground-level wide glazing.
 cut(x,-51.5,4.5,10.4,4.8,10)
# Projecting entry central section, trio of tall round-headed window slots.
add(0,-54,3,39,8,14)
for x,w in [(-13,7),(0,10),(13,7)]:arch_cut(x,-58,3.1,w,10.5,9)
add(0,-55,15.8,41,8.5,1.5)
# Slightly proud stair panel with non-identical three arch heights.
parts.append(profile([(-17,17),(17,17),(17,70),(12,72),(6,73.6),(0,74.5),(-7,73.8),(-13,73),(-17,72)],-52.6,3.8))
for x,w,h in [(-12,5.4,50),(0,8.5,53),(12,5.4,48)]:
 arch_cut(x,-54.5,18,w,h,4.3)
 # Main vertical mullions and five horizontal floor bands, backed to pane recess.
 details.append(box(x,-53.3,17.8,1.2,3.5, h-1.6))
 for z in [30,42,54]:details.append(box(x,-53.3,z,w+.6,3.5,1.6))
# Actual rear court faces: long wing windows with lower louver shades,
# perpendicular wing windows six rows; unknown outer ends remain plain.
for x in [25,36,47,58]:
 for z in [6,18,30,42,54]:
  cut(x,-16.5,z,8.5,4,7.2)
  add(x,-14.8,z+6.6,9.3,3.4,1.4)
for y in [-5,12,29]:
 for z in [6,18,30,42,54]:
  cut(15.5,y,z,4,12.5,7.2)
# Narrow end bay on photographed perpendicular courtyard wing.
for z in [6,18,30,42,54]:cut(15.5,48,z,4,5.8,7.2)
# Official photo-page note records new waterproof sloped roof in ROC111-112.
# Low dual-ridge cover is an explicit pitch/ridge approximation, not surveyed.
parts.append(profile([(-17.5,67),(17.5,67),(0,71)],0,138).rotate((0,0,90)).translate((0,-34,0)))
parts.append(profile([(-15.5,67),(15.5,67),(0,71)],19,76))
# Front broad shallow entrance steps.
for i in range(3):add(0,-59+i*1.1,2.8,37,1.7,.6*(i+1))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
