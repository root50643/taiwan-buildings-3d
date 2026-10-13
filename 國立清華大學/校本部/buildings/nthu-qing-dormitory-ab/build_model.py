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
# Scope: publicly photographed Qing Dormitory A/B pair, not C/D/E or whole complex.
add(0,0,0,150,100,3)
def tr(m,x,y,a):return m.rotate((0,0,a)).translate((x,y,0))
for side in [-1,1]:
 x=side*34;y=3;a=-side*12
 parts.append(tr(box(0,0,2.8,58,33,117.2),x,y,a))
 # Six window groups and three rounded exterior ledges per floor, simplified.
 for z in range(8,109,10):
  for xx in [-22,-13,-4,5,14,23]:cuts.append(tr(box(xx,-16.5,z,7,4,5.8),x,y,a))
  for xx in [-18,0,18]:
   details.append(tr(ellipse(xx,-17.8,z-1,3.2,2.8,1.3),x,y,a))
 for xx in [-28,-9,10,28]:details.append(tr(box(xx,-16.8,3,1.8,4,120),x,y,a))
 # Strong horizontal spandrels and top parapet.
 for z in range(5,117,10):details.append(tr(box(0,-16.8,z,57,2.8,1.2),x,y,a))
 parts.append(tr(box(0,0,119,60,35,2),x,y,a))
 # Rounded end landings attached to an opaque end-core silhouette.
 outer=side*28
 for z in range(9,110,10):parts.append(tr(ellipse(outer,2,z,4,13,1.4),x,y,a))
# Tall central glazed seam and upward folded cap.
add(0,-11,2.8,16,19,121.2)
cut(0,-20.5,8,11.5,3,111)
for z in range(9,120,5):det(0,-20.5,z,12,3.5,1)
for x in [-3,3]:det(x,-20.5,8,1.1,3.5,111)
parts.append(wedge([(-9,123),(9,123),(9,129),(0,126),(-9,129)],-11,20))
# Entrance canopy deliberately thickened and simplified.
add(0,-25,14,22,12,2)
for x in [-9,9]:add(x,-28,3,1.8,2,11.3)
for i in range(4):add(0,-38+i*4,3,25,5,1+i*.8)
# Unseen rear is plain; no room, security/access or residents' objects are modeled.
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
