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
# As-built public courtyard/aerial photographs in official archive PDF p6.
# Asymmetric U simplified to orthogonal wings; no internal room layouts.
add(0,0,0,150,140,3)
add(-49,9,2.8,30,100,102.2)
add(48,12,2.8,34,98,107.2)
add(0,48,2.8,102,26,100.2)
# Long recessed courtyard windows, stout mullions and staggered projecting frames.
for z in [9,21,33,45,57,69,81,93]:
 cut(-34,-4,z,3.8,77,6)
 cut(31,7 if z<33 else -1,z,3.8,54 if z<33 else 70,6)
 cut(-1,35,z,65,3.8,6)
 for y in range(-33,56,7):
  det(-34,y,z,4.2,1.1,6);det(31,y,z,4.2,1.1,6)
 for x in range(-29,32,7):det(x,35,z,1.1,4.2,6)
# Irregular thick concrete window frames project into courtyard in mid/lower levels.
for side,y,z,w in [(-1,-8,23,28),(-1,24,47,28),(1,-10,35,23),(1,24,23,27),(1,25,59,23)]:
 x=-32 if side<0 else 29
 for zz in [z,z+10]:det(x,y,zz,6,w,2)
 for yy in [y-w/2+1,y+w/2-1]:det(x,yy,z,6,2,12)
# Left outer end glazed vertical bay and broad solid white end wall.
cut(-55,-41,15,15,3.5,61)
for z in range(15,78,12):det(-55,-41,z,15,4,2)
for x in [-61,-49]:det(x,-41,15,1.6,4,62)
# Right brick front/end core has scattered small square punched windows.
for z in [16,30,44,58,72,86,100]:
 if z>29:cut(49,-37,z,4,3,4)
 for y in [-20,0,20,40]:cut(65,y,z,3,3,4)
# Brick courses are represented sparsely as recessed horizontal lines.
for z in [55,82]:cut(49,-37,z,29,1.2,0.9)
# Distinct red lattice portal: front left tall screen and overhead long truss.
# Main loadbearing members deliberately thickened; architectural red colour omitted.
for x in [-61,-45]:add(x,-44,3,2.4,4,109)
for z in range(5,109,10):add(-53,-44,z,18,4,1.8)
# Finer screen verticals all intersect rails and bottom base.
for x in [-57,-53,-49]:add(x,-44,3,1.1,2.6,109)
add(0,-44,100,126,5,2.4)
add(0,-44,110,126,5,2.4)
for x in range(-59,64,10):add(x,-44,102,1.8,5,8.2)
for x in range(-59,55,20):
 parts.append(wedge([(x,102),(x+2.2,102),(x+20,110),(x+17.8,110)],-44,2.5))
add(61,-39,100,4,14,12.4)
# Lower brick lecture-hall exterior with broad ribbed roof and tall facade fins.
add(20,-42,2.8,54,43,29.2)
add(20,-42,31,56,44,1.8)
for x in range(-5,48,4):det(x,-42,32,1.1,42,0.9)
for x in [0,10,20,30,40]:det(x,-64,5,2,5,23)
cut(10,-63.5,22,7,2.5,2.5)
add(56,-48,3,18,22,26)
for x in [51,60]:
 for z in [9,19]:cut(x,-59,z,2.8,2,3)
# Short stepped approach, not a reproduction of landscaping or parking layout.
for i in range(4):add(-18,-57+i*4,3,19,5,1+i*1.3)
# Unseen rear reduced to solid wings; no speculative roof machinery or interiors.
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
