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
# J: ten-storey nursing tower; photographed southeast-facing corner.
add(0,0,0,150,107,3)
# Main tall mass and its shorter left/rear wing, independently estimated depth.
add(13,10,2.8,100,65,104)
add(-48,14,2.8,27,57,105)
add(-36,15,2.8,18,58,75)
# Two-storey front arcade, open with a backed wall and substantial piers.
cut(10,-18,3,101,19,20)
for x in [-34,-17,0,17,34,51]:details.append(box(x,-25,3,3.2,5,21))
# Eight upper window ranks, with the characteristic alternating louver panels.
for z in range(27,105,10):
 for x in [-26,-10,6,22,38,54]:
  cut(x,-22.3,z,12,3.4,4.9)
  add(x,-23,z+5.2,13,2.2,1.1)
  cut(x,-22.3,z+6.8,10,2.8,1.5)
# Green-glazed vertical stair bands at front edges, recessed in tall white pylons.
for x in [-37,65]:
 add(x,-20,2.8,10,14,117)
 cut(x,-27,23,3.8,3,87)
 for z in range(25,111,10):details.append(box(x,-26.5,z,4,2.2,1.1))
# Projecting low left front bay has six storeys and its own tile hip cap.
add(-52,-19,2.8,27,25,69)
for z in range(25,68,9):
 for x in [-60,-47]:cut(x,-31.4,z,8,3.1,5)
hip(-52,-19,71,30,28,3.2)
# Deep side-facing balcony slots between the tall side pylons, not a blank wall.
for z in range(28,105,10):cut(-60,15,z,7,34,6.5)
for y in [-13,38]:
 add(-64,y,3,6,10,112)
 cut(-67,y,23,2.8,3.8,81)
# Roofscape stepped tiled caps and paired broad tower heads.
hip(12,9,106,101,67,3.4)
add(-21,18,107,22,30,13)
add(53,20,107,20,28,10)
hip(-21,5,108,29,24,3.0)
# Raised broken pediment visible over central front bay.
add(17,-18.5,105.5,30,10,2.5)
gable(17,-22,107,30,5,7)
arch_cut(17,-24,107,13,5,3.0)
add(17,-24,107,32,3,1.3)
# Unseen rear remains a simple estimated envelope, no invented window scheme.

# Additional public 2004 photograph identifies 科技教學大樓 at entry.
# Deep west-open court: do not fill the photo-visible multi-storey void.
cut(-20,13,3,104,28,125)
# Six stacked connector decks span between north and south wings.
for z in [24,34,44,54,64,74]:
 details.append(box(-40,13,z,11,31,2.2))
 # Backed 1.2mm parapets, open above rather than flat infill across the whole court.
 for x in [-45,-35]:details.append(box(x,13,z+2,1.2,31,2.0))
# Monumental open entry canopy at the courtyard mouth with substantial posts.
details.append(box(-66,13,22,18,39,2.5))
for y in [-5,31]:details.append(box(-70,y,3,4,4,21))
# Raised approach under entry; source-derived staircase simplified.
for i in range(3):details.append(box(-73+i*1.5,13,3,2.0,35,.8*(i+1)))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
