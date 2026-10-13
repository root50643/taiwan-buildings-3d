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
# Single low former-storehouse building. Long side and front seen in 2024/2025 photos.
add(0,0,0,79,150,3)
add(0,1,2.9,65,136,24)
parts.append(hip(0,1,26.7,70,141,10.6).rotate((0,0,0)))
# For a long-axis Y hipped ridge, construct the roof explicitly.
parts.pop()
pts=np.array([[sx*35,1+sy*70.5,26.7] for sx in [-1,1] for sy in [-1,1]]+[[0,-43,37.3],[0,45,37.3]])
parts.append(M.hull_points(pts))
add(0,1,25.3,68,139,1.8)
# Front two windows, central doorway and low shelter.
for x in [-20,20]:
 recess(x,-67.1,8,8.6,13.5,2.2)
 add(x,-67.7,7.2,10,1.5,1.1)
 add(x,-67.6,20.3,10,1.4,1.2)
recess(0,-67.1,3.2,15.5,19.8,2.3)
add(0,-69.5,22.5,22,7.0,1.8)
# Vertical brick pilasters break the facade.
for x in [-31,-10.5,10.5,31]:add(x,-67.3,3,3.0,1.4,23.2)
for side in [-1,1]:
 for yy in [-52,-32,-12,8,28,48]:
  cuts.append(box(side*32.6,yy,8,2.2,7.7,13.5))
  add(side*33.0,yy,7.2,1.5,9.2,1)
 for yy in [-65,-42,-22,-2,18,38,66]:add(side*32.8,yy,3,1.5,3.0,23.2)
# Rear unobserved: plain wall, no fictional exact openings.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
