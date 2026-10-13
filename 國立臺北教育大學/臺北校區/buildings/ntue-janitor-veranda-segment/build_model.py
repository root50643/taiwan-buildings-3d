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

def segment(x,y,z,w,h,rise,depth):
 spring=z+h-rise
 pts=[(x-w/2,z),(x+w/2,z),(x+w/2,spring)]
 pts += [(x+w/2*math.cos(t),spring+rise*math.sin(t)) for t in np.linspace(0,math.pi,33)[1:]]
 return profile(pts,y,depth)
def segment_trim(x,y,z,w,h,rise,th=2.0):
 return segment(x,y,z,w+2*th,h+th,rise+th,2.4)-segment(x,y-.1,z-.2,w,h+.2,rise,3.2)
# Old janitor/music-room visible end and three-bay veranda segment. Does NOT include second toilet building.
add(0,0,0,150,105,3)
add(0,3,2.8,134,85,3)
add(0,12,5.5,126,42,39)
# Unequal front/rear roof slopes extend over a deep open veranda.
roof=profile([(-39,43),(36,43),(14,68)],0,134).rotate((0,0,90))
parts.append(roof)
# Visible left gable: narrow high louver; other end is a plain model cutoff.
cut(-67,14,51,5,7,11)
for z in [53,56,59]:details.append(box(-67,14,z,2.2,7.5,1.2))
# Rearward glazing plane, two broad glazed doors and a narrow central window.
for x in [-38,38]:cut(x,-9,6,21,5,29)
cut(0,-9,21,13,5,15)
for x in [-43,-33,33,43]:details.append(box(x,-8,7,1.3,3.2,27))
for z in [18,29]:
 for x in [-38,38]:details.append(box(x,-8,z,21,3.2,1.4))
# Four supported posts delimit the selected three-bay segment, not whole-building column count.
for x in [-57,-19,19,57]:
 add(x,-35,5.5,4.6,4.6,5)
 add(x,-35,10,3.2,3.2,34)
 for sign in [-1,1]:
  poly=[(x,35),(x+sign*9,43),(x+sign*7,43),(x-sign*1,36)]
  if sign<0:poly.reverse()
  details.append(profile(poly,-35,3.2))
# Front beam ties the thickened braces and every column into the roof.
add(0,-35,42,128,4,3)
# No guessed back windows, roofs of detached toilet, trees, utility boxes or sale machines.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
