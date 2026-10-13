"""Original photo-derived NTHU exterior miniature, dimensions in millimetres.
No source 3D assets, survey plans, or interior arrangements used.
Run: python build_model.py (see requirements.txt).
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h): return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h): parts.append(box(x,y,z,w,d,h))
def det(x,y,z,w,d,h): details.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h): cuts.append(box(x,y,z,w,d,h))
def ellipse(x,y,z,rx,ry,h): return Manifold.cylinder(h,1,1,circular_segments=96).scale((rx,ry,1)).translate((x,y,z))
def wedge(poly,y,depth): return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def column(x,y,z,r,h): parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
# Official three exterior photos show high L-return, deep glazing entry and grids.
add(0,0,0,150,130,3)
add(0,-17,2.8,126,43,103.2)
add(43,25,2.8,40,75,103.2)
# Main front: central horizontal recessed strips above a three-storey glazed portal.
for z in [45,57,69,81,93]:
 cut(0,-38.5,z,59,5,7)
 for x in range(-26,30,7):det(x,-38.5,z,1.1,5.5,7)
# Narrow paired vertical bays flanking entrance.
for z in [9,21,33,45,57,69,81,93]:
 for x in [-54,-45,-36,36,45,54]:cut(x,-38.5,z,5.8,3.5,8)
# Giant front glazed recess is a single stepped volume with a thick frame.
cut(0,-38.5,8,61,7,31)
for x in [-25,-13,0,13,25]:det(x,-36,8,1.5,7,31)
for z in [9,18,27,37]:det(0,-36,z,59,7,1.5)
for x in [-32,32]:det(x,-40,4,3.5,7,36)
add(0,-40,38,67,7,3)
# Lake-facing back of main wing exposed only to left of perpendicular return.
for z in [9,21,33,45,57,69,81,93]:
 for x in range(-57,22,8):cut(x,4.5,z,5,3.5,8)
 # Inner return wall and external long wing: dense vertical window grid.
 for y in [12,23,34,45,55]:
  cut(23,y,z,3.5,6.5,8)
 for y in [-31,-20,-9,2,13,24,35,46,56]:cut(63,y,z,3.5,6.5,8)
 # Left exterior carries long horizontal window bands seen in pond view.
 cut(-63,-17,z,3.5,30,7)
 for y in [-28,-17,-6]:det(-63,y,z,4,1.2,7)
# The return end elevation is plain: no complete photo of that face.
# Broad front steps shortened to fit an independent base, landscaping omitted.
for i in range(5):add(0,-58+i*4,3,66,5,1+i*1.15)
# No invented plant-room objects; flat solid roof envelope, nominal low parapet.
add(0,-17,105,128,45,1.8)
add(43,25,105,42,77,1.8)
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
