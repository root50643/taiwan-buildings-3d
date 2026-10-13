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
# Taiwan Literature E101: one red-brick former office048 block only.
add(0,0,0,150,86,3)
add(0,0,2.9,130,54,28)
parts.append(hip(0,0,30,135,59,13))
# Small western return in public external footprint, plain where unphotographed.
add(-68,1,2.9,10,22,25)
parts.append(gable(-68,1,27,12,24,5))
# Seven round exterior arch bays, with solid window backing and shallow window muntins.
for x in [-54,-36,-18,0,18,36,54]:
 if x:arcrecess(x,-27.4,6,12,20,4)
 if x:
  for dx in [-2.3,2.3]:
   for z in [9,13.8,18.6]:recess(x+dx,-25.1,z,3.5,3.6,1.8)
  add(x,-27.8,6,12.5,1.8,1)
  # Broad arch-ring accent embedded in facade, not a detached shell.
 # Low basement vents in photograph, enlarged into solid-backed shallow slots.
 if x:arcrecess(x,-27.2,3.8,7,2.2,1.2)
# Centre projecting gable parapet and white shoulder motifs.
add(0,-29,3,19,5,30)
parts.append(gable(0,-29,33,21,5,9))
arcrecess(0,-31.6,5.7,12,21,4)
for x in [-10,10]:add(x,-29,30,3,6,7)
add(0,-31.9,29,1.8,1,8)
# Four triangular dormers front only; reverse roof unverified left simple.
for x in [-42,-21,21,42]:
 parts.append(gable(x,-13,35,12,12,7))
 cuts.append(prism([(x-3.8,36.2),(x+3.8,36.2),(x,40.2)],1.8,-19.2))
# Thin eaves made stout; no fragile flagpoles, vegetation or lettering.
add(0,-28.8,29.7,135,1.7,1.2)
add(0,28.8,29.7,135,1.7,1.2)
# Unseen rear has no invented door schedule or internal corridors.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
