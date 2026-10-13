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
# Two deep monumental open loggias meet a solid corner pier, evident in
# official MBA street photograph and OIR drone exterior photo.
add(0,0,0,150,146,3)
add(0,-8,2.8,100,70,102)
# Lower long wing beyond the main tower, distinctly stepped down.
add(0,43,2.8,100,34,78)
# Deep exterior recesses on front and right elevation; no interior plan.
cut(-5,-43,7,47,32,78)
cut(50,-8,7,32,32,78)
# Windows at back of the two loggias, with strong floor dividers.
for z in [10,20,30,40,50,60,70,80]:
 cut(-5,-27,z,43,1.8,6.5)
 for x in [-24,-16,-8,0,8,16]:det(x,-27.2,z,.9,2.5,6.5)
 cut(34,-8,z,1.8,29,6.5)
 for y in [-20,-12,-4,4]:det(34.2,y,z,2.5,.9,6.5)
# Narrow tall windows in the continuous upper beam, visible on both faces.
for x in np.arange(-44,46,6):cut(float(x),-43,90,2.6,2.4,9)
for y in np.arange(-37,25,6):cut(50,float(y),90,2.4,2.6,9)
# Full-height balcony strip on left and far-right piers.
cut(-40,-43,7,11,7,78)
cut(50,18,7,7,10,78)
for z in [8,18,28,38,48,58,68,78]:
 det(-40,-44,z,12,5,2.2)
 det(51,18,z,5,11,2.2)
# Thin horizontal masonry-course bands are robust relief, not brick texture.
for z in [15,25,35,45,55,65,75,85,101]:
 for x,w in [(-40,20),(35,30)]:det(x,-43.1,z,w,1.2,1.2)
 for y,d in [(-33,20),(18,18)]:det(50.1,y,z,1.2,d,1.2)
# Lower rear wing: continuous strip windows and substantial lower piers.
for z in [20,30,40,50,60,70]:
 cut(50,43,z,2.5,28,6.5)
 for y in [32,38,44,50,56]:det(50.1,y,z,2.5,.9,6.5)
cut(50,43,3.2,5.5,29,13)
for y in [30,38,46,54]:det(50, y,3,5,2,13)
# Public-art tubing deliberately omitted: fragile and not structural geometry.
# Entry steps inside the visible loggia.
for i in range(5):add(-5,-38+i*2.2,3,34,2.5,.7*(i+1))

solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
