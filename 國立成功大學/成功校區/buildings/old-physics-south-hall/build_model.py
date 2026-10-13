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
# Only the single-storey 1930 south hall, not the later physics towers or rear block.
add(0,0,0,150,62,3)
add(0,0,2.9,140,36,27)
add(0,0,28.6,144,40,1.8)
parts.append(hip(0,0,30,145,41,9))
# Tall lower windows and separate small transoms are the defining facade feature.
for xx in [-63,-54,-45,-36,-27,-18,0,9,18,27,36,45,54,63]:
 for dx in [-1.55,1.55]:
  for zz,hh in [(7,5.5),(13.2,5.6),(21,2.3),(24,2.3)]:recess(xx+dx,-18.1,zz,2.45,hh,1.7)
recess(-9,-18.1,5.5,6.5,16,2)
add(-9,-21,3,11,8,1.5);add(-9,-20,4.4,9,6,1.5)
add(-9,-20,22,11,6,1.3)
# Back face is a conservative shallow repetition; exact later appendages not resolved.
for xx in range(-63,64,9):
 recess(xx,18.1,7,5.5,11.8,1.4)
 recess(xx,18.1,21,5.5,5.3,1.4)
# End faces are mostly plain in partly occluded garden views.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
