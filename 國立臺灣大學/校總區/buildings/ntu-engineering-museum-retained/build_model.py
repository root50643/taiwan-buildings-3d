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
# N51: restored museum's retained right-hand building; no removed centre or detached wall.
add(0,0,0,150,81,3)
add(-11,7,2.8,106,42,38)
# Long ridge roof; gabled end in the official 2023 oblique photograph.
roof=profile([(-23,40),(23,40),(0,49)],0,110).rotate((0,0,90)).translate((-11,7,0))
parts.append(roof)
# Plain high gable walls, narrow end vents are observed but not equipment details.
for x in [-64,42]:
 for yy in [3,7,11]:cut(x,yy,39,2.6,1.5,5)
# The tall industrial windows and alternating little ventilation openings.
for x in range(-57,40,12):
 cut(x,-14,6,7.4,2.5,11)
 cut(x,-14,26,7.4,2.5,10)
 cut(x,-14,20,6.6,2.5,3)
 cut(x,-14,38,6.6,2.5,2.3)
 for z,h in [(6,11),(26,10)]:
  details.append(box(x,-14,z,1,1.7,h))
  details.append(box(x,-14,z+h/2,7.4,1.7,.9))
for x in range(-63,44,12):add(x,-14.8,3,1.3,2,37)
add(-11,-15,18,108,3,1.3)
add(-11,-15,36.8,108,3,1.3)
# Low adjoining end volume photographed with its own hipped roof.
add(55,7,2.8,27,42,21)
hip(55,7,23,30,46,7)
for x in [49,60]:
 cut(x,-14,5,7,2.5,11)
 cut(x,-14,19,7,2.5,2.5)
# Distinct visible exterior steps; solid cores avoid thin underside shells.
# Low stepped parapets, rather than a continuous inclined slab, keep treads readable.
for i in range(15):
 x=33-i*2.5; h=(i+1)*1.25
 add(x,-27,2.8,2.8,13,h)
 for y in [-32.9,-21.1]:add(x,y,2.8+h-.2,2.8,1.2,1.4)
add(-4,-24,20.5,10,17,1.5)
# Unseen long rear deliberately plain; no imagined interior or neighbouring new buildings.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
