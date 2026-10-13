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
# Photo-based mass: deeply recessed central facade and exposed side balcony slots.
add(0,0,0,150,120,3)
add(0,4,2.8,100,76,100)
# Higher corner mass visible at the front-right corner.
add(40,-24,100,20,20,7)
add(-43,31,100,14,22,5)
# Main four-storey central void. This is an exterior recess, not an interior room.
cut(-8,-34,33,43,16,45)
# Deep perimeter frame projects forward and crosses multiple storeys.
add(-34,-35,31,9,7,54)
add(19,-35,31,10,7,54)
add(-8,-35,78,62,7,7)
# Two tall round piers inside the multi-storey recess, backed into wall.
for x in [-19,4]:
 details.append(Manifold.cylinder(44,1.8,1.8,circular_segments=32).translate((x,-28,33)))
# Storey window bands recessed at the back of the large central opening.
for z in [36,47,58,69]:
 cut(-8,-26,z,40,1.8,7)
 for x in [-26,-21,-16,-11,-6,-1,4,9]:det(x,-26.1,z,.7,2.5,7)
 det(-8,-26.1,z+3.2,40,2.5,.7)
# Irregular front window groups around the recess rather than uniform wallpaper.
for z in [13,24,35,46,57,68,79,90]:
 for x in [-45,39]: cut(x,-34,z,6.5,1.8,6.5)
for z in [37,49,61,73,89]:
 for x in [-34,20]:cut(x,-39,z,13,8.5,5)
# Top floor recessed glazing, below the projecting roof shade.
cut(-9,-34,89,39,5,7)
for x in [-24,-15,-6,3,12]:det(x,-33.6,89,1,5,7)
# Side elevation: two full-height balcony recesses create distinct vertical bays.
for y in [-16,32]:
 cut(50,y,12,14,12,87)
 for z in [12,23,34,45,56,67,78,89]:
  det(46.8,y,z,8,12,1.3)
  det(49.8,y,z+1.3,1.2,12,2.2)
# Side wall windows between recessed bays, front corner wall left intact.
for z in [36,47,58,69,80,91]:
 for y in [-31,-3,8,19,40]:cut(50,y,z,1.8,6.5 if y==-31 else 5.5,6.5) # v2 open corner notch fully
# Lower side rectangle projects distinctly, as in official aerial-angle photo.
add(51,8,11,6,36,21)
for z in [14,24]:
 for y in [-4,7,18]:cut(54,y,z,1.8,6,6)
# Lower front portal: deep brick-framed band and glazed entrance.
add(-8,-37,3,57,9,29)
cut(-10,-42,5,43,5.5,23) # v2 remove 0.25mm step lip
for x in [-28,-21,-14,-7,0,7]:det(x,-41.2,5,.8,5,23)
for z in [12,20]:det(-10,-41.2,z,43,5,.8)
# Entrance name pier is kept blank; no unreadable copied text.
add(18,-41,3,5.5,2,29)
# Supported roof shade perimeter.
add(-13,-34,101,66,3,1.5)
for x in range(-43,19,6):add(x,-34,100.8,1.5,5,1.7)
add(50,9,101,3,47,1.5)
for y in range(-13,32,6):add(50,y,100.8,5,1.5,1.7)
for i in range(6):add(-10,-52+i*1.8,3,48,2,.7*(i+1))

solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
