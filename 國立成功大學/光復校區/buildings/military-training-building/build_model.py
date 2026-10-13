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
# A014 public exterior; no systems, equipment or interior configuration.
add(0,0,0,150,86,3)
add(0,0,2.9,132,62,34)
parts.append(hip(0,0,36,139,69,4))
# Two-storey deep external portico bays with shallow bevelled heads.
for x in range(-55,56,11):
 pts=[(x-4,3.5),(x+4,3.5),(x+4,15),(x+2,16.4),(x-2,16.4),(x-4,15)]
 cuts.append(prism(pts,10,-31.1))
 pts=[(x-4,23),(x+4,23),(x+4,32.5),(x+2,33.7),(x-2,33.7),(x-4,32.5)]
 cuts.append(prism(pts,10,-31.1))
 recess(x,-31.1,19,8,2.5,10)
 # The uncut short horizontal strip is a thickened portico railing.
# Photographed short end: slender lower apertures and a few small upper windows.
for yy in [-20,0,20]:
 cuts.append(box(-66.1,yy,5,2.2,5,10))
 cuts.append(box(-66.1,yy,25,2.2,6.5,5))
# Opposite portico rhythm is approximate; no internal hall model.
for x in range(-55,56,11):
 recess(x,31.1,6,7.5,10,3)
 recess(x,31.1,23,7.5,10,3)
add(0,-32.5,18,133,3.4,1.2)
add(-16,-35,16.5,20,10,1.3)
# Keep other end plain, and omit rooftop/security equipment and signs.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
