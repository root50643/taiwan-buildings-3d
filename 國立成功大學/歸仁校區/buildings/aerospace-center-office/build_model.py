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
# Aerospace center office I023: two-storey detached office exterior, no research equipment.
add(0,0,0,150,150,3)
add(0,0,2.9,110,128,51)
add(0,0,53,113,131,1.6)
# Three broad end bays, with flat simplified sunshades over the lower windows.
for xx in [-35,0,35]:
 for dx in [-6.75,-2.25,2.25,6.75]:
  for zz in [32,39]:recess(xx+dx,-64.1,zz,3.6,6,2.4)
 if xx==-35:recess(xx,-64.1,4,12,20,2.5)
 else:
  recess(xx,-64.1,10,20,11,2.5)
  add(xx,-66,22,24,5.5,1.2)
# Long return: regularly spaced large two-level windows and deep upper bays.
for yy in [-49,-29,-9,11,31,51]:
 for zz in [9,32]:
  for dy in [-4.5,0,4.5]:
   cuts.append(box(-55.1,yy+dy,zz,2.5,3.5,12))
   cuts.append(box(55.1,yy+dy,zz,2.5,3.5,12))
 # Shallow concrete uprights and upper cornice define the outside rhythm.
for yy in [-60,-40,-20,0,20,40,60]:
 add(55.4,yy,27,1.8,2,25)
 add(-55.4,yy,27,1.8,2,25)
add(55.4,0,51,1.8,127,2)
add(-55.4,0,51,1.8,127,2)
# Simple raised parapet follows the observed flat roof perimeter.
add(0,-64,54,112,1.2,2)
add(0,64,54,112,1.2,2)
add(-55.4,0,54,1.2,127,2)
add(55.4,0,54,1.2,127,2)
# Rear facade is unverified and kept plain; neighbouring low sheds omitted.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
