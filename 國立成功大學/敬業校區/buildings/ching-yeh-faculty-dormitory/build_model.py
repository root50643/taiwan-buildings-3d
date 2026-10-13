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
# Ching-Yeh faculty single-room dormitory F004, one U-shaped exterior building.
add(0,0,0,150,108,3)
add(0,18,2.9,136,29,63)
add(-46,-11,2.9,39,75,63)
add(46,-11,2.9,39,75,63)
# Six tiers and broad continuous concrete bands seen in both street corner images.
for zz in [7,17,27,37,47,57]:
 # Front end screens: regular small perforations, enlarged for reliable printing.
 for xx in [-46,46]:
  for dx in [-10.5,-7,-3.5,0,3.5,7,10.5]:
   for dz in [0,2.1,4.2]:recess(xx+dx,-48.6,zz+dz,2.2,1.35,1.6)
 # Outer long side apertures, conservatively repeated.
 for yy in [-35,-19,-3,13,25]:
  cuts.append(box(-68.1 if yy>=3 else -65.6,yy,zz,2,10,5.6));cuts.append(box(68.1 if yy>=3 else 65.6,yy,zz,2,10,5.6))
 # Courtyard-facing rear frontage and side alcoves.
 for xx in [-18,-6,6,18]:recess(xx,3.4,zz,8.5,6.5,3.8)
 for yy in [-34,-20,-6]:
  cuts.append(box(-26.4,yy,zz,6,9,6.5));cuts.append(box(26.4,yy,zz,6,9,6.5))
 # Horizontal bands on the end faces and on the outer sides.
 for xx in [-46,46]:add(xx,-49,zz+7,39.6,1.5,1.1)
 add(-66,0,zz+7,1.5,65,1.1);add(66,0,zz+7,1.5,65,1.1)
# Entrance stair and stout square colonnade in the U-shaped approach.
add(0,-6,3,36,20,1.5);add(0,-3,4.4,33,14,1.4)
for xx in [-22,22]:add(xx,-9,3,2.8,2.8,22)
add(0,-9,24,47,7,1.8)
# Rear is not fully photographed: shallow plain rhythm rather than fabricated balconies.
for zz in [7,17,27,37,47,57]:
 for xx in [-57,-43,-29,-15,-1,13,27,41,55]:recess(xx,32.6,zz,9,5.5,1.5)

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
