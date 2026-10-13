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
# Rectangular hall with shallow cylindrical vault; front is the curved gable face.
add(0,0,0,150,113,3)
add(0,4,2.9,129,85,32)
add(0,2,32.5,142,99,8)
# Barrel roof profile sampled densely, solid section with no enclosed interior shell.
xx=np.linspace(-71,71,49)
pts=[(-71,39.9),(71,39.9)]+[(float(x),float(40+12*(1-(x/71)**2))) for x in xx[::-1]]
parts.append(prism(pts,97,2))
# Tall flared exterior piers and repeated window band seen on multiple elevations.
for x in np.linspace(-66,66,10):
 add(float(x),-44,3,3.5,5,28)
 # Flared capital/haunch joins column to upper fascia, not fragile freestanding brackets.
 parts.append(M.hull_points(np.array([[x+sx*1.75,-44+sy*2.5,27] for sx in [-1,1] for sy in [-1,1]]+[[x+sx*3.7,-44+sy*4.5,33] for sx in [-1,1] for sy in [-1,1]])))
for x in np.arange(-67,68,4):recess(float(x),-47.6,34.8,2.9,4.1,1.8)
# Lower front openings remain shallow behind the piers.
for x in np.arange(-58,59,14):recess(float(x),-38.6,6,10,6,1.6)
# Side piers/window band and rear stair inferred from observed side/corner photos.
for side in [-1,1]:
 for yy in [-28,-10,8,26,44]:
  add(side*66.5,yy,3,4,4.2,29.6)
 for yy in np.arange(-41,47,4):cuts.append(box(side*71.1,float(yy),34.8,1.8,2.9,4.1))
# Rear has simplified band and centre exterior stair, seen only obliquely.
for x in np.arange(-64,65,6):recess(float(x),51.6,34.8,4.4,4.1,1.8)


solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
