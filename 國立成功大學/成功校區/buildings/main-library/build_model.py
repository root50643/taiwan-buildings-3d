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
# Main exterior volumes; the upper facade projects 19 mm beyond the lower wall.
add(0,0,0,150,116,3)
add(-5,13,2.9,124,67,46)
add(-8,-31.5,24,118,27,27)
# Proud full-height stair tower, distinct from the low roof volumes.
add(58,-26,2.9,22,30,64)
add(58,-20,57,22,18,10)
add(57,17,26,24,58,25)
add(-7,13,48,96,59,3)
# Solid glazing plane behind projecting shade blades; each blade is real geometry.
for x in [-56,-36,-16,4,24,44]:
 recess(x,-45.1,30,16,15,4)
 recess(x,-45.1,25.3,16,3.1,2)
 for z in [30,32.5,35,37.5,40,42.5]:add(x,-45.5,z,18,5.8,1.2) # 1 mm overlap into each side pier survives recess subtraction
# Lower glazing is deeply set back below the upper cantilever.
for x in [-56,-36,-16,4,24,44]:
 for z in [6,16]:recess(x,-20.6,z,16,6.5,2)
# Substantial columns directly support the deep upper projection.
for x in [-64,-44,-24,-4,16,36,48]:
 parts.append(M.cylinder(21.2,1.55,1.55,24).translate((x,-37,2.9)))
for zz in [9,20,31,42,55]:recess(58,-41.1,zz,5,5.5,2)
for yy in [1,19,37]:
 for zz in [29,38,46]:cuts.append(box(69.1,yy,zz,2,13,3.8))
# Low entrance and separate slender foreground colonnade.
add(-18,-38,3,38,27,14)
for x in [-31,-18,-5]:recess(x,-51.6,4.5,7,10.5,2)
add(-18,-38,16.5,39,28,1.4)
for x in [-64,-52,-40,13,25,37,49,61]:
 parts.append(M.cylinder(11.5,1.3,1.3,24).translate((x,-48,3)))
add(0,-46.5,14,138,7,1.8)
# Solid miniature; no interior or below-grade plaza.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
