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
# Creative Building, front to athletic field. Three upper sun-screen groups.
add(0,0,0,150,109,3)
# Brick plinth, rear hall mass and broad left/right solid bookends.
add(0,0,2.8,132,85,10)
add(0,10,12,132,65,63)
# Lower front gallery is truly recessed 12mm, not shallow engraved arches.
for x in [-47.5,-17,17,47.5]:add(x,-34,11,3.2,5,28)
for x in [-61,61]:add(x,-29,12,12,20,63)
add(0,-31,37,124,12,3)
add(0,-33,10.5,126,7,2)
# Back glazing in lower gallery and the intermediate light balcony edge.
# Back wall details are not legible; leave it plain instead of inventing window groups.
add(0,-34,25.5,118,2.4,1.3)
# Broad upper window slots behind three groups of six vertical louvers.
for c in [-34,0,34]:
 cut(c,-24.0,42,28,5.8,29)
 for dx in [-11,-6.6,-2.2,2.2,6.6,11]:
  add(c+dx,-29,39,1.6,12,36)
# Upper deep side gaps and main broad roof cap.
for x in [-52,52]:cut(x,-27,43,9,13,28)
add(0,0,74,137,91,4.4)
# East stair/entrance is glazed and set behind the solid main front corner.
add(63,21,3,11,41,66)
for y in [7,17,27,37]:
 for z in [8,23,38,53]:cut(68.5,y,z,3.2,8.2,12.7)
# Main entry door and overhanging small canopy, adjacent to older hall.
cut(68.5,4,3.8,4,10,16)
add(69,5,21,11,18,2.1)
# Side entrance parapet and stepped upper concrete volumes visible in side photo.
add(52,25,69,29,35,7)
add(48,28,76,21,25,6)
add(45,30,81.5,13,17,12)
for y in [23,27,31,35]:cut(51.5,y,84,2,1.4,8)
# Unseen west/back elevations kept plain; no invented classroom windows.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.set_tolerance(.0001).simplify(.0001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
