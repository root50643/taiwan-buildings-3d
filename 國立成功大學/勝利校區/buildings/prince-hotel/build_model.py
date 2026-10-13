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
# Original NCKU Alumni Hall / current Prince Hotel: main clock-tower block only.
add(0,0,0,150,108,3)
add(-5,15,2.9,110,62,110)
add(-5,15,111,119,70,2.5)
# Clock tower on front corner, separated in height and facade depth.
add(44,-13,3,24,26,135)
add(44,-13,137,29,31,3)
for z in [116,124]:add(44,-13,z,28,30,1.4)
# Clock faces: shallow round discs on two public sides; no trademark lettering.
parts.append(disk(44,-26.4,131,4.1,1.2))
parts.append(M.cylinder(1.2,4.1,4.1,48).rotate((0,90,0)).translate((56,-13,131)))
for x in [37,43,49]:
 for z in range(37,111,9):recess(x,-26.2,z,4,7,2)
# Main repeated hotel balcony facade: deep shadow bays, vertical piers and slabs.
for x in [-49,-33,-17,-1,15]:
 for z in range(35,108,11):recess(x,-16.1,z,12,8,3)
for z in range(32,111,11):add(-18,-17.5,z,83,4,1.4)
# Low arched podium joining circular corner turret, distinct from neighboring dorms.
add(0,-26,2.9,129,31,28)
for x in [-52,-30,-8,14]:arcrecess(x,-41.6,7,16,19,2)
parts.append(M.cylinder(31,19,19,64).translate((49,-26,2.9)))
parts.append(M.cylinder(2.2,21,21,64).translate((49,-26,33)))
for x in [41,56]:arcrecess(x,-43.7,12,10,15,2.3)
# Deep rear / roof not fully documented; use plain solid volumes, no invented glazing.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
