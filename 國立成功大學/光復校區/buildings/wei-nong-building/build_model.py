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
# A013 continuous linked building, two offset long bars and substantial end wings.
add(0,0,0,120,150,3)
add(-27,0,2.9,26,136,47)
add(27,0,2.9,26,136,47)
add(-28,-52,2.9,40,32,50)
add(28,52,2.9,40,32,50)
# Cross-links enclose an open exterior courtyard; no interior rooms modeled.
add(0,-33,2.9,33,10,36)
add(0,35,2.9,33,6,36)
# Three-level central entrance behind the forecourt, with strong horizontal lips.
for z in [5,16,27]:recess(0,-38.1,z,24,7.4,3.2)
for z in [13,24,35]:add(0,-38.6,z,31,2.6,2.1)
for i in range(5):add(0,-45+i*1.2,3+i*.6,25,4.5,1)
# Long observed outer corridor elevations: coarse four-level openings and floor bands.
for side in [-1,1]:
 for y in [-54,-40,-26,-12,2,16,30,44,58]:
  xx=48.1 if (side<0 and y<-36) or (side>0 and y>36) else 40.1
  for z in [6,17,28,39]:cuts.append(box(side*xx,y,z,2.6,9.5,7.4))
# Forecourt-facing balcony openings: broad recesses and visibly splayed upper edges.
# Both front wings are open facades in the exterior photographs, not blank brick ends.
for x,w in [(-38,13),(-20,13),(21,10),(33,10)]:
 for z in [8,19,30,41]:
  pp=[(x-w/2,z),(x+w/2,z),(x+w/2-1.3,z+7.8),(x-w/2+1.3,z+7.8)]
  cuts.append(prism(pp,7,-68.1))
  add(x,-68.6,z-2,w+1.6,3.8,1.8)
# Rear short end retains source-observed blank brick and narrow stair windows.
for z in [9,21,33,45]:recess(38,68.1,z,2.5,4.5,2.2)
# Inner open-air facades retain modest floor rhythm, rather than detailed rooms.
for x in [-13.9,13.9]:
 for y in [-20,-6,8,22]:
  for z in [7,19,31]:cuts.append(box(x,y,z,2,7.5,5.5))
# Flat roof planes and low raised stair tops simplified from the visible external massing.
add(-27,-51,51,20,17,2)
add(27,51,51,20,17,2)

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
