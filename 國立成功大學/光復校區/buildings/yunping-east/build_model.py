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
# Yunping east block only, A029: C-shaped exterior envelope open to the east.
add(0,0,0,150,128,3)
add(0,-40,2.9,136,25,91)
add(-48,0,2.9,28,84,91)
add(-6,38,2.9,112,26,91)
# Long outward frontage, with prominent lower grey frame and upper brick tiers.
for zz in [8,19,30,43,54,65,76]:
 for xx in range(-60,61,10):
  if zz<23 and xx in [-10,0]:continue
  recess(xx,-52.6,zz,7.3,6.2,2.2)
for xx in range(-61,62,5):recess(xx,-52.6,85,2.7,6.3,2)
for xx in range(-65,66,10):add(xx,-53,3,1.2,2,33)
for zz in [14,25,36]:add(0,-53,zz,134,2,1.2)
# Square small entry porch on the outward face.
add(-8,-57,3,23,13,20)
recess(-8,-63.6,4,16,15.5,10)
# Court-facing long bars carry projecting balcony bands and glazed openings.
for yy,sign in [(-27.5,1),(25,-1)]:
 for zz in [8,19,30,41,52,63,74,85]:
  for xx in [-26,-13,0,13,26,39,48]:
   if yy>0 and xx>44:continue
   recess(xx,yy+sign*.1,zz,9.6,5.8,2.2)
  add(10,yy+sign*.8,zz-1,88,3,1.3)
# Inner west end with the tall central glazed strip and arched doorway.
# Strip is on x=-34 (court-facing side), represented by real shallow relief.
for zz in range(24,83,9):
 for yy in [-7,0,7]:cuts.append(box(-33.9,yy,zz,2.2,5.5,7))
cuts.append(arch(0,0,4,14,15,8).rotate((0,0,90)).translate((-33.5,0,0)))
# Outer west face and short bar ends: limited visible openings, not invented interiors.
for zz in [10,22,34,46,58,70,82]:
 for yy in [-28,29]:cuts.append(box(-62.1,yy,zz,2,5,5))
# A few narrow end openings at the two eastern ends.
for zz in [10,22,34,46,58,70,82]:
 cuts.append(box(68.1,-40,zz,2,6,5))
 cuts.append(box(50.1,38,zz,2,6,5))

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
