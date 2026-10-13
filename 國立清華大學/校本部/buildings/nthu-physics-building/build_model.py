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
# Physics exterior: stepped high/low wings, expressed grid, roof pavilions.
add(0,0,0,150,124,3)
add(-31,7,2.8,69,82,74.2)
add(36,-7,2.8,65,54,39.2)
# High central front recess between the two pavilion-topped vertical bays.
cut(-28,-34,31,15,7,46.2)
for z in [31,45,59,73]:det(-28,-34,z,15,7.5,2)
# Seven storeys, small arched-headed windows on solid backing.
def archwin(x,y,z):
 cut(x,y,z,5.2,3,5.3)
 c=Manifold.cylinder(3,2.6,2.6,circular_segments=24).rotate((90,0,0)).translate((x,y+1.5,z+5.3))
 cuts.append(c)
for z in [6,16,26,36,46,56,66]:
 for x in [-59,-47,-10,-0.5]:archwin(x,-34,z)
for z in [6,16,26]:
 for x in [12,24,36,48,60]:archwin(x,-34,z)
# Lowwing top band has broad rectangular glazing.
for x in [12,24,36,48,60]:cut(x,-34,34,8,3,5)
# Long left side grid; windows kept simple where detail less certain.
for z in [6,16,26,36,46,56,66]:
 for y in [-24,-10,4,18,32,43]:cut(-65.5,y,z,3,7,6)
# Projecting frame grid has real depth, not image texture.
for x in [-65,-53,-41,-16,-4,7,19,31,43,55,67]:
 h=74 if x<5 else 39
 det(x,-34.5,3,1.4,4,h)
for z in [13,23,33,43,53,63,73]:
 det(-31,-34.5,z,69,4,1.4)
 if z<40:det(36,-34.5,z,65,4,1.4)
for y in [-32,-18,-4,10,24,38,47]:det(-66,y,3,3.5,1.4,74)
for z in [13,23,33,43,53,63,73]:det(-66,7,z,3.5,82,1.4)
# Pavilion frames and thick gently rounded eave edges visible in photos.
def pavilion(x,y,z,w,d,h):
 add(x,y,z,w,d,2)
 for xx in [x-w/2+2,x+w/2-2]:
  for yy in [y-d/2+2,y+d/2-2]:add(xx,yy,z,2.5,2.5,h)
 # Intermediate central uprights on long front, connected to base and eave.
 for yy in [y-d/2+2,y+d/2-2]:add(x,yy,z,2.1,2.5,h)
 add(x,y,z+h-2,w+5,d+5,3)
 # Front/back halfround undersides make distinctive heavy rolled lips.
 for yy in [y-d/2-1,y+d/2+1]:
  barrel=Manifold.cylinder(w+5,2.5,2.5,circular_segments=32).rotate((0,90,0)).translate((x-w/2-2.5,yy,z+h-1))
  parts.append(barrel)
 # Strong horizontal beam below cap.
 add(x,y-d/2+1,z+h-5,w,2.5,1.5)
for args in [(-52,-19,77,25,27,19),(-6,-19,77,22,27,12),(-52,33,77,25,25,12),(45,-16,42,36,25,16)]:pavilion(*args)
# Two exterior front porticoes with heavy rounded roofs, only low public facade.
for x,w in [(-20,44),(43,43)]:
 for xx in [x-w/2+3,x+w/2-3]:add(xx,-42,3,2.5,10,26)
 add(x,-40,28,w,17,3)
 parts.append(Manifold.cylinder(w,2.5,2.5,circular_segments=32).rotate((0,90,0)).translate((x-w/2,-47,30)))
# Unknown rear elevations plain. Roof pavilion positions/depth are approximations.
solid=parts[0]
for p in parts[1:]: solid=solid+p
for c in cuts: solid=solid-c
for p in details: solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
