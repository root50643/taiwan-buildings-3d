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
# Official street and oblique aerial photos show a long stepped low front block,
# a taller central rear mass and visible solar-panel roof surfaces.
add(0,0,0,150,100,3)
add(0,-18,2.8,136,28,31)
add(-51,-20,3,34,32,31)
add(52,-20,3,32,32,31)
add(-10,14,2.8,42,39,46)
add(30,20,2.8,43,25,29)
# Three front levels, deep horizontal strip glazing with interrupted white piers.
for x,w,y in [(-51,30,-36),(-12,39,-32),(25,29,-32),(52,27,-36)]:
 for z in [6,16,26]:
  cut(x,y,z,w,3,5.5)
  for xx in np.arange(x-w/2+4,x+w/2,5):det(float(xx),y-.1,z,1.2,3,5.5)
# Shallow reveals emphasize facade setbacks at the junctions.
# Stepped blocks provide the reveals without thin corner slivers.
# Street entry porch on two square columns, solid backed and fused.
add(9,-37,12,25,13,3)
for x in [-1,19]:add(x,-41,3,2.2,3.2,9.5)
cut(9,-32,3.2,18,2.2,8.7)
for x in [3,9,15]:det(x,-32.5,3.3,1.2,4,8)
# Street-visible corner windows.
for z in [6,16,26]:
 for y in [-28,-18,-9]:cut(68,y,z,2,6,5.5)
# Higher rear cube's known silhouette, no invented back windows.
add(-10,14,47.5,43,40,1.5)
# Broad shallow rooftop solar arrays, recognized in official aerial photo.
# Thick plates and incised seams, no fragile floating frames or hidden systems.
for x,w,y,d,z in [(-28,76,-18,22,33.5),(38,46,-18,22,33.5),(-10,35,14,29,49)]:
 parts.append(wedge([(x-w/2,z),(x+w/2,z),(x+w/2,z+2),(x-w/2,z+.6)],y,d))
 for xx in np.arange(x-w/2+5,x+w/2,6):cut(float(xx),y,z+.55,.45,d+.3,2)
# Low relief rather than exact solar cell hardware.
for i in range(3):add(9,-46+i*1.5,3,28,1.8,.6*(i+1))

solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
