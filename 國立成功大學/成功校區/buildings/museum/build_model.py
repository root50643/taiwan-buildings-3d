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
# Broad two-storey frontage, central gable and shallow arched porte cochere.
add(0,0,0,150,61,2.8)
add(0,3,2.7,140,37,29)
parts.append(hip(0,3,31.4,143,40,7))
add(0,-16,2.7,28,5,33)
parts.append(gable(0,-16,35.5,31,6,7))
# Central arched entrance projection represented as an open shallow recess.
add(0,-22,2.7,29,13,19)
add(0,-22,21.3,31,14,1.2)
arcrecess(0,-28.0,2.8,21,14.5,3.0)
for x in [-9,0,9]:arcrecess(x,-18.6,24,5.1 if x else 6.3,9.2,1.8)
parts.append(disk(0,-19,37.0,2.1,1.0))
# Paired vertical windows from observed facade; pane mullions retained as solid strips.
for x in [-62,-54,-44,-36,-25,-18,18,25,36,44,54,62]:
 for z,h in [(6,8),(16,3),(21,8)]:recess(x,-15.65,z,4.1,h,1.5)
# Window surrounds are intentionally shallow for printability.
for x in [-62,-54,-44,-36,-25,-18,18,25,36,44,54,62]:
 add(x,-15.75,5.4,5.4,1.2,.8)
add(0,-15.75,19.6,139,1.3,.8)
# Rear and return volumes are estimates; deliberately plain.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
