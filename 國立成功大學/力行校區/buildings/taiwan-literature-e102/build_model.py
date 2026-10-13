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
# Taiwan Literature E102, former barracks042; one distinct rectangular brick block.
add(0,0,0,150,86,3)
add(0,0,2.9,132,62,37)
parts.append(gable(0,0,39,67,138,19).rotate((0,0,90)))
# Long side tall paired sash windows, simplified at rear where not photographed.
for x in [-54,-36,-18,0,18,36,54]:
 for dx in [-2.2,2.2]:
  for z in [9,14.5,20,25.5]:recess(x+dx,-31.1,z,3.4,4.5,1.8)
 add(x,-31.7,8,11,2,1.5)
# Left gable: two tall windows and side-positioned door visible in GIS corner photo.
for yy in [-6,14]:
 for dy in [-2.4,2.4]:
  for z in [9,14.5,20,25.5]:cuts.append(box(-66.1,yy+dy,z,1.9,3.6,4.5))
 add(-66.7,yy,8,2,11,1.4)
cuts.append(box(-66.1,-24,4,2.2,8,22))
cuts.append(box(-69.1,0,44,1.8,3.8,7))
# Simplified sill/base plinth and an exterior door step, no connecting corridor.
add(0,0,2.9,133,63,2)
add(-69,-24,3,8,13,1.7)
add(-68,-24,4.5,6,11,1.4)
add(0,-32,39,136,1.7,1.1);add(0,32,39,136,1.7,1.1)
# Rear and opposite end intentionally plain: no evidence for precise openings.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
