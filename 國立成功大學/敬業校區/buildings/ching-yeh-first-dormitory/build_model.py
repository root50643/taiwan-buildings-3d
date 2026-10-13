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
# Ching-Yeh first dormitory F003, public exterior only.
add(0,0,0,150,122,3)
# Broad two-bank frontage and narrower rear projection from public campus outline.
add(0,-14,2.9,126,63,137)
add(0,26,2.9,72,57,132)
add(0,-18,137,22,51,6)
# Central recess: entrance and shallow vertical inter-bank separation.
recess(0,-45.6,3.1,23,9,10)
# Thirteen repeated balcony/window tiers visible in official frontal and corner photos.
for zz in range(13,134,10):
 for xx in [-49,-29,29,49]:
  recess(xx,-45.6,zz,16,6.2,3.8)
  add(xx,-47,zz-1.7,18,5,1.4)
  add(xx,-48.8,zz-1,18,1.1,1.4)
 recess(0,-45.6,zz,13,5.2,1.8)
 # Deep narrow strips between the central core and outer room banks.
 for xx in [-14,14]:recess(xx,-45.6,zz,4,7.5,5)
# Sparse end apertures and rear-facing rhythm: back detail is conservative.
for zz in range(13,134,10):
 for yy in [-30,-10,10]:
  cuts.append(box(-63.1,yy,zz,2,5,5.5));cuts.append(box(63.1,yy,zz,2,5,5.5))
for zz in range(13,125,10):
 for xx in [-26,-13,0,13,26]:recess(xx,54.6,zz,9,5.5,1.5)
# Ground-level broad piers, joined to base and facade, not empty indoor volumes.
for xx in [-57,-39,39,57]:add(xx,-47,3,3,5,9.8)

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
