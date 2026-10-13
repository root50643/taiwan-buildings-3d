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
# Long two-storey arcaded building, two north entrance pavilions.
add(0,0,0,150,47,2.7)
add(0,1,2.6,140,33,31)
add(0,1,33.2,142,35,1.6)
add(0,1,34.7,142,35,1.1)
# Eleven repetitive arcades; their widths and relief depths are photo estimates.
xs=[-62,-50,-23,-11.5,0,11.5,23,50,62]
for x in xs:
 arcrecess(x,-15.6,6,9.4,11.3,3.2)
 arcrecess(x,-15.6,20,9.4,12.7,3.2)
 # Balustrades are strong solid relief rather than delicate freestanding bars.
 add(x,-16.15,19,10,1.5,2.8)
 for dx in [-3,-1.5,0,1.5,3]:recess(x+dx,-16.95,19.7,.65,1.5,.6)
for x in [-36.5,36.5]:
 add(x,-17,2.6,16,6,32)
 arcrecess(x,-20.1,5,10.3,11.8,3.5)
 arcrecess(x,-20.1,20,10.3,14.1,3.5)
 add(x,-19.5,18.0,12,2,2.2)
 parts.append(gable(x,-17,35,17,6,3.8))
 for dx in [-7,7]:
  add(x+dx,-19,3,2.6,3,32)
  add(x+dx,-19,34.8,4.2,4.2,2)
 for i in range(3):add(x,-21+i,2.7+i*.7,12,4-i, .8)
# Three arches per end from public side photograph; rear left deliberately plain.
for x in [-70,70]:
 for yy in [-9,1,11]:
  for z,h in [(6,11),(20,12)]:
   cuts.append(arch(yy,0,z,7.4,h,2).rotate((0,0,90)).translate((x,0,0)))
# Solid corner pilasters and roofline rhythm.
for x in [-69,-57,-44,-29,-17,-5.8,5.8,17,29,44,57,69]:add(x,-16.1,3,1.3,1.8,30.5)

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
