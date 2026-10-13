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
# F Humanities: two official photographs show hipped roofs, a tall recessed column portico,
# long side balcony slabs, and a low entrance/shop canopy on the opposite end.
add(0,0,0,150,106,3)
add(0,10,2.8,126,62,59)
# Large open front portico bay and paired round columns reach the upper arcade.
cut(0,-20,3,48,12,36)
for x in [-28,28]:column(x,-25,3,2.1,38)
add(0,-23,38,64,15,3)
# Upper arch windows and broad entablature photographed above the portico.
# Main identifying feature: ONE large arched upper opening over the open column portico.
add(0,-12,38,62,20,28)
arch_cut(0,-22,41,44,23,3.4)
details.append(arch(0,-22.5,40,48,26,2.4)-arch(0,-22.6,41,44,23,3))
for x in [-14,0,14]:details.append(box(x,-21.3,41,1.2,2.4,16))
add(0,-22,65.5,65,4,1.6)
# Left and right side windows, with low ground-floor arches.
for x in [-54,-39,39,54]:
 arch_cut(x,-21,7,10,10,3.4)
 for z in [23,36,48]:cut(x,-21,z,8.5,3.4,7)
# Main hipped roof with substantial overhanging eave, not generic flat cap.
parts.append(CrossSection.square((132,67),center=True).extrude(9,scale_top=(.62,.35)).translate((0,10,61.5)))
# Higher near-end circulation tower and narrow horizontal strips from second photograph.
add(54,13,3,17,57,69)
for z in [13,24,35,46,57,66]:cut(62.5,12,z,3.3,35,3.2)
parts.append(CrossSection.square((22,62),center=True).extrude(6,scale_top=(.45,.62)).translate((54,13,71.6)))
# Visible long return has deep horizontal balcony slots and shading slabs.
for z in [15,26,37,48]:
 cut(-62.5,10,z,3.5,48,6)
 add(-63,10,z+5.7,3,52,1.4)
# Low opposite-end storefront vestibule (second photo) is attached at the right return.
add(65,16,2.8,18,30,13)
parts.append(CrossSection.square((20,34),center=True).extrude(4,scale_top=(.70,.48)).translate((65,16,15.5)))
cut(74,16,3,3,24,9)
# Small raised flat canopy in front of the ground-floor entry.
add(70,16,12,10,38,1.6)
for y in [0,32]:add(74,y,3,1.8,1.8,10)
step(0,-34,49,4)
# Official Humanities02 is the same named building, showing an alternate end and its return.
# Map its short-end column frame to +X and long balcony return to +Y; no cardinal azimuth claim.
cut(60,16,25,18,40,34)
# Two major tall edge piers support the upper occupied room over the deep multi-level recess.
for y in [-5,37]:details.append(box(65,y,23,3.8,3.8,38))
add(63,16,58,7,46,3.3)
for y in [0,13,26,36]:cut(62.5,y,63,3.5,8,4)
# Continuous return balconies are observed in photo02, therefore not left as an unknown solid rear.
for z in [16,27,38,49]:
 cut(-3,40.8,z,113,4,6.5)
 add(-3,41.5,z+6.1,116,3,1.4)
 for x in [-52,-15,24,50]:details.append(box(x,40.7,z,2.2,4,6.5))
# Only hidden courtyard/roof surfaces remain plain. Depth and camera orientation are estimates.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
