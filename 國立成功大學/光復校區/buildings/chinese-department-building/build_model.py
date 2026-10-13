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
# A024 one connected irregular Chinese Department building, excluding nearby artifacts museum.
add(0,0,0,104,150,3)
# Front pair of gabled rooms are asymmetrical, as observed in school photographs.
add(-31,-48,2.9,29,35,22)
add(31,-48,2.9,29,35,24)
parts.append(gable(-31,-48,24,34,40,8))
parts.append(gable(31,-48,26,34,40,8))
# Joined middle/rear courtyard wings, shape from public GIS exterior outline only.
add(-35,12,2.9,15,88,28)
add(35,27,2.9,15,62,28)
add(0,2,2.9,83,17,28)
add(0,59,2.9,83,18,28)
# Northern outside court open above; front entrance cover is supported on stout columns.
add(0,-30,2.9,52,13,18)
add(0,-56,18,43,23,2)
for x in [-18,-6,6,18]:add(x,-65,3,2.5,3,16)
# A little upward edge to the straight portal canopy, not a curved palace roof.
parts.append(prism([(-23,19),(-20,19),(-20,21),(-23,22)],24,-56))
parts.append(prism([(20,19),(23,19),(23,22),(20,21)],24,-56))
# Gable octagonal vents and long slender recesses, scaled up for relief readability.
for x,z in [(-31,27),(31,29)]:
 pts=[(x+1.6*__import__('math').cos(a),z+1.6*__import__('math').sin(a)) for a in np.linspace(0,2*np.pi,9)[:-1]]
 cuts.append(prism(pts,1.7,-68.1))
# Front gable panels remain mostly solid; photographs show brick fields, not window grids.
for x in [-31,31]:
 recess(x,-65.6,5,19,12,1.2)
 for xx in [x-12,x+12]:add(xx,-66,3,1.2,1.3,22)
# Three-level external gallery rhythm in visible open court; widths approximate.
for z in [7,15,23]:
 for yy in [17,29,41,52]:
  cuts.append(box(-27.4,yy,z,2,8,5))
  cuts.append(box(27.4,yy,z,2,8,5))
 for x in [-29,-17,-5,7,19,31]:recess(x,10.6,z,8.3,5,2)
for z in [11.8,19.8,27.8]:
 add(-27.4,33,z,1.5,51,1)
 add(27.4,33,z,1.5,51,1)
# Back outside elevation not fully photographed: no invented opening schedule.
# Shallow roof rims indicate the flat gallery roofs without machinery.
for x in [-35,35]:add(x,35,30.5,16,66,1.1)
add(0,59,30.5,84,19,1.1)

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
