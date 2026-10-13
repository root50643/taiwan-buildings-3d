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
# Public photographs show three-storey concrete frame with broad eaves,
# long recessed window bands, expressed vertical piers and a small entry canopy.
add(0,0,0,150,118,3)
add(0,0,2.8,126,84,33)
# Perimeter roof overhang, robust continuous thick slab.
add(0,0,35,132,90,2.2)
# Front and right-side three-level windows are broad recesses, not sticker texture.
for z in [6,17,28]:
 cut(0,-42,z,120,4,5.6)
 for x in np.arange(-58,60,7):det(float(x),-42,z,1.1,4.5,5.6)
 cut(63,0,z,4,77,5.6)
 for y in np.arange(-34,37,7):det(63,float(y),z,4.5,1.1,5.6)
# Expressed structural piers stand proud all three storeys and support eaves.
for x in [-59,-35,-11,13,37,61]:
 det(x,-43,3,1.8,5,32.4)
 add(x,-44,34,1.8,5,2)
for y in [-37,-13,11,35]:
 det(64,y,3,5,1.8,32.4)
 add(65,y,34,5,1.8,2)
# Small, shallow entry canopy seen in the street approach.
add(-19,-47,11,29,14,1.8)
for x in [-31,-7]:add(x,-52,3,1.8,1.8,8.2)
# The official text states a glazed center; roof not clearly visible in photos.
# Use a low simple opaque cap, explicitly approximate, not an invented roof plant.
add(0,0,37.1,66,42,1.2)
for x in [-22,-11,0,11,22]:cut(x,0,37.8,.6,42.2,.7)
# Back and left, not clearly visible, deliberately plain.

solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
