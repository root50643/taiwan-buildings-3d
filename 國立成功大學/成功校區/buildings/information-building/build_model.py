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
# Information Building high block B006; excludes adjacent physics/chemistry long wing.
add(0,0,0,150,142,3)
add(0,0,2.9,92,106,128)
# Main frontage of slim vertical windows, current 2026 school material photos.
for zz in [12,29,46,63,80,97,114]:
 for xx in range(-40,41,5):
  if zz==12 and xx in [-35,-30,-25,-20]:continue
  if zz in [29,46] and xx in [-30,-25,-20,-15]:continue
  recess(xx,-53.1,zz,2.9,10,2.3)
# Larger irregular central/low window bays retain the visible variation.
for zz in [29,46]:
 for xx in [-30,-18]:recess(xx,-53.1,zz,9,8,2.3)
# Top rectangular frame and two visibly open slots, open through the shallow parapet.
add(0,-49,130,90,8,13)
for xx in [-26,26]:cuts.append(box(xx,-49,132,25,10,7))
# Raised exterior entry and stair approach; no ground-floor fictitious pavilion.
recess(-27,-53.1,25,11,13,3)
for i in range(10):add(-27,-66+i*1.4,3,20,2.2,2.3*(i+1))
add(-27,-53,24.6,23,11,2.5)
parts.append(M.cylinder(2.4,11,11,48).translate((-27,-55,24.6)))
add(-27,-56,38,19,10,1.5)
# Small corner support is thickened for printing; detailed metal rails omitted.
add(-35,-58,26,1.5,1.5,12.5)
# Red-brick end mass with sparse openings and long return's regular bays.
for zz in [12,29,46,63,80,97,114]:
 cuts.append(box(-46.1,-7,zz,2.2,7,6))
 cuts.append(box(46.1,2,zz,2.2,14,7))
# Unseen full rear remains conservative solid; no made-up equipment or floor layouts.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
