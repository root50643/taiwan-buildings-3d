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
# Two official front and oblique exterior photos: square tower, projecting
# upper central gable, lower triangular portico and full-height center seam.
add(0,0,0,150,118,3)
add(0,5,2.8,112,68,85)
# Central facade's forward mass at top and lower entrance level.
add(0,-31,67,43,7,20)
parts.append(wedge([(-22,86),(22,86),(0,92)],-31,7))
add(0,-31,13,43,7,18)
# Central vertical spine, visually continuing from pitched upper cap.
add(0,-35,31,1.6,2,61)
# Ground and repeated front windows; middle upper block is independently cut.
for z in [7,18,29,40,51,62,73]:
 for x in [-47,-39,-31,31,39,47]:cut(x,-29,z,4.7,1.8,6)
 if z in [40,51,62]:
  for x in [-16,-7,7,16]:cut(x,-29,z,4.8,1.8,6)
for z in [19,74]:
 for x in [-16,-6,6,16]:cut(x,-34.5,z,4.8,1.8,6)
# White horizontal bands are attached low relief, with corner continuity.
for z in [15,26,37,48,59,70,81,87]:
 for x,w in [(-40,32),(40,32)]:det(x,-29,z,w,1.1,.9)
 det(56,5,z,1.1,68,.9)
# Observed long right side facade, divided into several vertical bays.
for z in [7,18,29,40,51,62,73]:
 for y in [-20,-10,0,10,20,30]:cut(56,y,z,1.8,5.3,6)
# Portico's broad shallow pediment and strengthened freestanding columns.
add(0,-38,13,48,21,2.2)
parts.append(wedge([(-24,15),(24,15),(0,20.4)],-38,21))
for x in [-20,-7,7,20]:column(x,-46.5,3,1.5,10.2)
# Entry is shallow, not an internal room.
cut(0,-29,3.2,30,2.4,8.8)
for x in [-10,0,10]:det(x,-29.1,3.2,1,3,8.8)
# Compact external stair; public sculpture omitted.
for i in range(5):add(0,-53+i*1.5,3,48,1.8,.65*(i+1))

solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
