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
# Bailing Hall surviving front pavilion only. The rebuilt Hall of Fame behind is excluded.
add(0,0,0,130,150,3)
add(0,0,3,100,124,2)
add(0,3,4.8,85,104,36.2)
# Deep glazed wall recesses across the visible front and left/right long elevations.
cut(0,-49,6,79,6,33)
for x in [-42.5]:cut(x,0,6,6,94,33)
# Structural piers and their projecting footing blocks.
for x in [-42,-14,14,42]:
 det(x,-49.5,5,3.4,6,36)
 det(x,-50,5,5,7,1.4)
for x in [-42.5]:
 for y in [-48,-24,0,24,48]:
  det(x,y,5,6,3.4,36)
  det(x,y,5,7,5,1.4)
# Coarse glazing mullions, two tall glass registers plus transoms.
for x in range(-38,39,8):det(x,-49,6,1.1,4,33)
for z in [7,13,20,36,39]:det(0,-49,z,82,4,1.1 if z!=20 else 2)
for side in [-1]:
 for y in range(-44,46,8):det(side*42.5,y,6,4,1.1,33)
 for z in [7,13,20,36,39]:det(side*42.5,0,z,4,99,1.1 if z!=20 else 2)
# Entrance leaves replace the lower glazing of one front bay.
cut(0,-49.5,6,10,6,14)
for x in [-5,0,5]:det(x,-49.7,6,1.2,4,14)
det(0,-49.7,19,11,4,1.2)
# Roof overhang and thick segmented fascia; notches follow visible edges.
add(0,2,40,95,114,2)
add(0,2,42,92,111,5)
for x in [-34.5,-11.5,11.5,34.5]:add(x,-55,42,21.8,4,5)
for side in [-1]:
 for y in [-40,-14,12,38]:add(side*46,y,42,4,24.5,5)
# Shallow upper rim expresses the dark coping without material-dependent color.
add(0,2,47,92,111,.9)
# Exposed underside roof ribs merge into the pavilion, avoiding unsupported floating slats.
for x in range(-40,41,8):det(x,-50.5,39,1.4,8,2)
# Public front steps, landscape and furnishings omitted.
add(0,-62,3,30,6,1)
add(0,-58,3,26,5,2)
# Unknown rear is plain, no attached Hall of Fame crown, interior or equipment.
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
