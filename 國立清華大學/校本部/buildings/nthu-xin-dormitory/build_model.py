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
# Public front/back exterior photographs, not accommodation/security arrangements.
add(0,0,0,150,140,3)
def tr(m,x,y,a):return m.rotate((0,0,a)).translate((x,y,0))
# Five tall folded facade bays, rotated toward the forecourt; depth is estimated.
for x,y,a in [(-57,-1,24),(-30,8,12),(-5,12,0),(31,8,-12),(58,-1,-24)]:
 parts.append(tr(box(0,0,2.8,17,31,104.2),x,y,a))
 cuts.append(tr(box(0,-15.5,9,12.5,2.6,94),x,y,a))
 for z in [13,25,37,49,61,73,85,97]:
  for xx in [-3.4,3.4]:cuts.append(tr(box(xx,-14.1,z,4.2,3.8,7.4),x,y,a))
 for xx in [-7.5,0,7.5]:details.append(tr(box(xx,-15.5,3,1.5,3.5,104),x,y,a))
# Set-back linking bays with thick balcony spandrels.
for x,y in [(-44,8),(-18,13),(13,13),(45,8)]:
 add(x,y,2.8,18,30,98.2)
 for z in [12,24,36,48,60,72,84,96]:
  if x!=13 or z>=48:cut(x,y-15-1,z,11,7,6)
# Central-right entrance motif: round opening and small gable/oculus at roofline.
add(13,-3,3,15,5,45)
cut(13,-4,5,10,9,20)
cuts.append(Manifold.cylinder(6,4.8,4.8,circular_segments=64).rotate((90,0,0)).translate((13,0,37)))
parts.append(wedge([(5.5,99),(20.5,99),(13,105)],13,30))
cuts.append(Manifold.cylinder(4,2.1,2.1,circular_segments=48).rotate((90,0,0)).translate((13,1,101.8)))
# Opposite public elevation shows a deep rectangular entry frame.
add(0,29,3,35,5,28)
cut(0,31.5,5,21,4,21)
for z in [42,54,66,78,90]:
 for x in [-35,-17,0,17,35]:cut(x,28,z,8,7,7)
# Forecourt round stepped platform, simplified and connected through common base.
parts.append(ellipse(0,-47,3,28,17,2))
parts.append(ellipse(0,-47,4.8,23,13,1.2))
# No air conditioners, personal items, room numbers, access devices or interior mesh.
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
