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
# G015 2018 swimming/ball-sports building. Detached outdoor pool and CGI scheme excluded.
add(0,0,0,150,150,3)
add(0,1,2.9,132,130,35)
add(0,17,37,132,98,44)
add(-18,-37,37,95,53,28)
# Tall corner louver-clad volume, wholly bonded to main building.
add(52,-39,2.9,24,52,83)
# Coarsened true-relief louver rows wrapping the observed corner; >=1.2 mm high.
for z in range(8,81,3):
 add(52,-65.4,z,24,2,1.25)
 add(64.2,-39,z,2,52,1.25)
# Front lower louver panels, with substantial solid walls behind.
for x in [-54,-30,-6]:
 for z in range(8,43,3):add(x,-64.2,z,17,2,1.25)
# Open high roof frame across the west/front half, anchored to lower building and rear mass.
for x in [-65,-43,-21,1,23]:
 add(x,-62,63,3,4,24)
 add(x,-21,83,3,85,4)
add(-21,-62,83,91,4,4)
# Recessed upper facade bays and thick balcony lips.
for x in [-53,-31,-9,13]:
 recess(x,-63.6,47,13.5,12,2.3)
 add(x,-64.3,45.4,17,3,1.8)
# Deep vertical shading fins on the observed long side, solid inner wall retained.
for yy in [-26,-13,0,13,26,39,52]:
 add(67,yy,41,4,1.8,40)
 cuts.append(box(66.1,yy+5.5,46,2.2,7,29))
# Inward ground-level openings below the side overhang.
for yy in [-20,-2,16,34,52]:cuts.append(box(66.1,yy,5,2.2,11,16))
# Plain unknown rear and roof slab; no roof installations/equipment/interior modeled.

solid=M.batch_boolean(parts, __import__('manifold3d').OpType.Add)
if cuts:solid=solid-M.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError
solid=solid.simplify(0.003)
m=solid.to_mesh(); mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(OUT/'model.stl', mesh.extents, len(mesh.faces))
