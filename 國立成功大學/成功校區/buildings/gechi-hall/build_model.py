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
# Taller nave with front gable, low side corridors and four-column entrance.
add(0,0,0,102,150,3)
add(0,4,2.9,61,127,43)
parts.append(gable(0,4,45.7,65,130,18))
# Front pediment is slightly proud of the main roof.
add(0,-60,2.9,64,3.8,43)
parts.append(gable(0,-60,45.7,65,4,18))
for x in [-39,39]:
 add(x,3,2.9,18,128,21)
 add(x,3,23.6,19.5,130,1.4)
 # Corridors expressed as shallow recesses, not a hollow building.
 for yy in [-45,-23,-1,21,43]:
  c=box(x+(-8 if x<0 else 8),yy,5,2.8,15,16);cuts.append(c)
# Four entrance columns and a connected roof; actual overhang requires support.
add(0,-64,3,78,16,1.5)
for x in [-33,-11,11,33]:
 add(x,-69,4.4,4,4,18)
 add(x,-69,4.4,5.5,5.5,2)
 add(x,-69,21,5.5,5.5,1.6)
add(0,-64,22.2,79,17,2)
for x in [-19,-4.4,4.4,19]:recess(x,-62.0,29,5.3,11.4,2.0)
# Raised paired arch mouldings over the middle two rectangular windows.
for x in [-4.4,4.4]:
 outer=arch(x,-62.2,37,8.4,7,1.4);inner=arch(x,-62.2,36.8,6.8,6.2,2)
 parts.append(outer-inner)
cuts.append(disk(0,-62.2,50,3.5,2))
# Oculus crossbar represented by solid material in the recess.


for x in range(-27,28,6):
 zz=45.7+18*(1-abs(x)/32.5)-2.1
 add(x,-62,zz,1.4,1.6,2.2)
# Upper clerestory windows on each side; spacing inferred from side photo.
for x in [-30.65,30.65]:
 for yy in [-42,-20,2,24,46]:cuts.append(box(x,yy,30,1.6,6,10))

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
