"""Photo-informed exterior miniature. Units mm; no survey precision claimed.
Python 3.12; pip install numpy==2.5.4 trimesh==5.1.1 manifold3d==3.5.4
Run python build_model.py from any working directory. Output beside this file.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold as M, CrossSection as C
OUT=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h):return M.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def prism(points,depth,y):return C([points]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def gable(x,y,z,w,d,h):return prism([(x-w/2,z),(x+w/2,z),(x,z+h)],d,y)
def hip(x,y,z,w,d,h):
 pts=np.array([[x+sx*w/2,y+sy*d/2,z] for sx in [-1,1] for sy in [-1,1]]+[[x-w/2+min(w,d)*.38,y,z+h],[x+w/2-min(w,d)*.38,y,z+h]])
 return M.hull_points(pts)
def arch(x,y,z,w,h,d):
 r=w/2; spring=z+h-r
 pts=[(x-r,z),(x+r,z)]+[(x+r*np.cos(t),spring+r*np.sin(t)) for t in np.linspace(0,np.pi,25)]
 return prism(pts,d,y)
def disk(x,y,z,r,d):return M.cylinder(d,r,r,48).rotate((90,0,0)).translate((x,y+d/2,z))
def recess(x,y,z,w,h,d=1.6):cuts.append(box(x,y,z,w,d,h))
def arcrecess(x,y,z,w,h,d=1.6):cuts.append(arch(x,y,z,w,h,d))
# Science north / chemistry high bar, excluding shared low connecting lobby.
add(0,0,0,150,86,3)
add(-7,0,2.9,122,57,121)
# Tall glass-clad external end stair volume represented as backed grid relief.
add(57,-8,2.9,18,42,124)
for z in range(7,121,13):
 for x in [-57,-44,-31,-18,-5,8,21,34,47]:recess(x,-28.6,z,6.1,8.1,2.8)
 for x in [52,57,62]:
  for dz in [0,4.8]:recess(x,-29.1,z+dz,3.2,3.6,1.4)
 for yy in [-23,-14,-5,4,10]:cuts.append(box(66.1,yy,z,1.7,5.7,8.2))
# Broad exposed end returns; opposite street side is simplified U-glass banding.
for z in range(7,121,13):
 for yy in [-18,-6,6,18]:cuts.append(box(-68.1,yy,z,1.8,5,8))
 for x in range(-58,49,10):recess(x,28.6,z,7.4,8.4,1.2)
# Horizontal grids indicate exterior cladding only; no stair flights or equipment.
for z in range(6,124,6):add(57,-29.4,z,18.4,1.3,1)
add(-38,8,123,28,25,6)

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
