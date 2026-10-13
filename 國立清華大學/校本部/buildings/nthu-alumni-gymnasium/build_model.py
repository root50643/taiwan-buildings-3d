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
# Long hall and tall entrance block, based on actual visible photos.
add(0,0,0,150,96,3)
add(0,4,2.8,132,67,29)
add(-48,-1,29,35,59,15)
# Projecting lower entrance volume and shallow arcade recess.
add(-41,-32,3,49,8,20)
cut(-31,-36,3.2,25,3,7.5)
column(-29,-35.5,3,1.3,8)
column(-19,-35.5,3,1.3,8)
# Entrance louver panels as 0.6mm backed grooves.
for z in [12,13.7,15.4,17.1,18.8]:
 cut(-28,-36,z,19,1.2,.7)
 cut(-58,-36,z,10,1.2,.7)
# Circular window depressions on observed tall end of front facade.
for x,z in [(-60,32),(-49,36),(-39,31),(-33,37),(-52,28),(-35,28)]:
 cuts.append(Manifold.cylinder(1.8,1.1,1.1,circular_segments=24).rotate((90,0,0)).translate((x,-29,z)))
# Long elevation clerestory band; thin corrugations intentionally omitted.
for x in range(-24,64,8):cut(x,-29.5,26,6.2,1.5,3.7)
# Repeated saw-tooth roof forms visible above the long facade.
for x in range(-26,64,12):
 parts.append(wedge([(x,31),(x+11,31),(x+9,34),(x+1,34)],4,63))
# Back is a plain inferred envelope; no unobserved rear windows invented.

solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
