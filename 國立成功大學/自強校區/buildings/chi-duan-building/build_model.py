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
# Independent modern infill; adjacent red-brick departmental blocks omitted.
add(0,0,0,150,109,3)
add(0,8,2.9,113,74,105)
# Broad projecting perimeter frame on the glazed entrance elevation.
add(-59,-34,17,7,20,98);add(59,-34,17,7,20,98)
add(0,-34,107,125,20,8)
# Lower facade is set back, upper glazing and shade shelves are actual relief.
for z in [23,45,68,90]:
 for x in [-45,-27,-9,9,27,45]:recess(x,-29.1,z,15,15,2.4)
 if z>=45:add(0,-34,z-1,111,12,1.5)
for x in [-50,0,50]:add(x,-35,3,3.5,4,104)
add(22,-40,21,66,16,2.5)
add(0,-33,3,116,12,2.5)
# Rear from school material photos: narrow window pairs and broad louver screen.
for z in [10,31,52,73,94]:
 for x in [-42,-23]:recess(x,45.1,z,3.8,11,2)
 recess(-4,45.1,z,17,15,2)
for x in range(10,55,3):add(x,45.8,18,1.2,2,82)
for z in [24,45,66,87]:recess(20,46.3,z,13,12,3.5)
# Unobserved connecting sides plain; no connected adjacent buildings included.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
