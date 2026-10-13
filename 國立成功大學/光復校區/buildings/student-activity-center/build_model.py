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
# A018 continuous L-shaped student center, including its joined western wing.
add(0,0,0,150,98,3)
# Connected low/core mass and west return: not merging surrounding separate buildings.
add(13,13,2.9,108,36,22)
add(-50,-3,2.9,34,78,29)
add(21,16,23,86,30,10)
add(26,19,32,61,23,6)
# Large projecting front terrace above the recessed colonnaded ground level.
add(15,-12,17,104,23,2.2)
add(15,-21.7,18.9,104,2,5)
# Upper terraces step back and retain broad concrete/framed parapet bands.
for z,yy,w,d in [(25,-3,96,10),(33,6,80,5)]:
 add(18,yy,z,w,d,1.5);add(18,yy-2.4,z+1.3,w,1.3,3)
for x in [-30,0,31,61]:add(x,-19,3,2.6,2.8,15.8)
# Long front glazed backing, leaving solid strips for transoms/mullions.
for x in range(-34,66,10):
 for z in [5.5,10.5]:recess(x,-5.1,z,7.8,3.6,2)
for x in range(-16,59,9):recess(x,0.9,27,6.4,3.2,2)
# Upper far-back band and stepped west-wing exterior window rows.
for x in range(-31,66,10):
 for z in [7,14,21]:recess(x,31.1,z,7,4,1.8)
for y in [-31,-18,-5,8,21,31]:
 for z in [6,13,20,27]:cuts.append(box(-67.1,y,z,2,8,3.5))
for z in [10,17,24,31]:add(-50,-41.4,z,35,2,1.1)
for x in [-59,-50,-41]:
 for z in [5,12,19,26]:recess(x,-42.1,z,6,3.6,1.8)
# Exterior broad stair/ramp is a coarse stepped solid, not interior circulation.
for k in range(10):add(-6+1.7*k,-23,3+1.3*k,3,10,1.8)
add(9,-23,15,9,10,2)
# Plinth steps below main frontage.
add(15,-32,3,108,8,1.4);add(15,-29,4.3,104,7,1.3)
# Roof surfaces simplified; no installations, courtyard trees or sculptures.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
