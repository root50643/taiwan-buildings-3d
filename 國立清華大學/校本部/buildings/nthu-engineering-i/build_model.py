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
# Official exterior views show an L-shaped tall block, raised corner spine,
# two-storey street entry, top-floor framing and a lower curved courtyard wing.
add(0,0,0,150,138,3)
# Main street-facing long wing and the return wing seen from open courtyard.
add(0,-35,2.8,130,28,91)
add(-51,9,2.8,28,89,91)
add(-44,-35,91,35,29,6)
# Distinct far-end vertical shaft visible in official end elevation photo.
add(64,-27,3,9,20,95)
# Deep horizontal grouped window bands on street facade.
for z in [20,30,40,50,60,70,80]:
 for x,w in [(-44,27),(-6,39),(40,38)]:
  cut(x,-49,z,w,3.5,5.8)
  for xx in np.arange(x-w/2+5,x+w/2,7):det(float(xx),-49.2,z,1.1,4,5.8)
# Strong off-center vertical light-colored frame and upper horizontal frame.
det(-25,-49,14,2.5,3,79)
add(15,-49,66,92,3,1.4)
# Roof-level open-band recess at right, with thick vertical end piers.
cut(38,-49,87,40,4.5,4.3)
# Two-storey entrance recess under tall pilotis at street left.
cut(-45,-49,3.2,31,9,13)
for x in [-57,-45,-33]:det(x,-50,3,1.8,10,13)
# Outer return elevation at x=-65, photographed from the corner.
for z in [20,30,40,50,60,70,80]:
 for y in [-27,-11,5,21,37]:
  cut(-65,y,z,3.5,12,5.8)
  det(-65.2,y,z,4,1,5.8)
# Public courtyard-facing windows visible in second official photo.
for z in [20,30,40,50,60,70,80]:
 cut(-37,16,z,3.5,67,5.8)
 for y in np.arange(-13,48,7):det(-36.8,float(y),z,4,1.1,5.8)
# Far shaft receives only observed narrow corner windows.
for z in [12,23,34,45,56,67,78,89]:cut(68.5,-27,z,1.8,7,5.8)
# Curved low public wing: rear boundary and exact radius are simplified.
low=ellipse(28,20,2.8,38,34,18) ^ box(43,23,2.7,46,70,19)
parts.append(low)
# Low wing attaches only to the common base, one connected printable object.
for y in [3,14,25,36]:cut(20,y,9,2.5,7,5)
# Shallow courtyard stairs following the photographed terraced approach.
for i in range(7):add(-7,54-i*2.5,3,44,3,.8*(i+1))

solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
