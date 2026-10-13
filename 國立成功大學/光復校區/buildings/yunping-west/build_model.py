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
# Yunping west block only, A028: public exterior footprint is a T, not a single slab.
add(0,0,0,150,134,3)
# Low southern transverse block and the taller north-south shaft.
add(0,-42,2.9,136,25,35)
add(-25,1,2.9,36,92,91)
add(-25,38,2.9,62,28,91)
# Tall south facade: lower recessed frame and upper narrow-window rhythm.
for zz in [10,20,30]:
 for xx in [-37,-29,-21,-13]:recess(xx,-54.6,zz,6,6.2,2.1)
for zz in [43,54,65,76]:
 for xx in [-37,-29,-21,-13]:recess(xx,-45.1,zz,6,6,2)
for xx in [-38,-33,-28,-23,-18,-13]:recess(xx,-45.1,85,2.6,6.3,2)
# Lower frontage frame stands proud of the tall shaft.
for xx in [-42,-34,-26,-18,-8]:add(xx,-55.1,3,1.3,2,34)
for zz in [12,23,34]:add(-25,-55.1,zz,35,2,1)
# The low block's large rectangular portal is a deep exterior recess.
recess(20,-54.6,3.1,34,24,20)
add(20,-56,3,42,7,3)
for xx in [0,40]:add(xx,-55,3,3,5,25)
add(20,-55,27,43,5,3)
for xx in [-61,-51,1,11,21,31,41,51,61]:
 recess(xx,-54.6,31,7,4.8,1.8)
# Shaft side windows and two taller glass bands on the internal rear-facing side.
for zz in [8,19,30,41,52,63,74,85]:
 for yy in [-31,-21,-11,-1,9,19,29]:
  if yy>=24 or (zz<38 and yy<-28):continue
  cuts.append(box(-43.1,yy,zz,2,7,6))
  cuts.append(box(-6.9,yy,zz,2,7,6))
# North transverse bar and its inward-facing seven-tier bays.
for zz in [8,19,30,41,52,63,74,85]:
 for xx in [-49,-39,-29,-19,-9,1]:recess(xx,52.1,zz,7,6,2)
# End wall windows seen in west-block corner photographs.
for zz in [8,19,30,41,52,63,74]:
 for yy in [31,41]:cuts.append(box(-56.1,yy,zz,2,6,5.5))
# No east-block geometry; their common low link ends at the public map boundary.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
