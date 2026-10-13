"""F2：官方照片近似外觀；單位 mm，非測量模型。"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold,OpType
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
# Three-storey brick hall: front at Y=-15, rooftop two solar arrays.
add(0,0,0,150,76,2.4)
add(0,7,2.3,140,44,44)
add(0,7,46,142,45,1.5)
# Alternating deep brick piers and narrow pale structural strips.
for x in range(-65,66,10):
 add(x,-15.7,3,1.2,2.5,42)
for x in range(-60,61,10):add(x,-16,3,3.2,3,40)
# Two lighter wide strips are recognisable in the original facade.
for x in [-45,45]:add(x,-16.2,2.4,3.8,3.4,44)
for z in [7,21,35]:
 for x in range(-65,66,10):
  for dx in [-2.5,2.5]:cut(x+dx,-15,z,2.6,2.2,7.5)
# Central recessed entrance and large flat-roof portico with two outer piers.
cut(0,-15,3,27,3,8)
add(0,-20,2.3,37,18,1.2)
for x in [-15.5,15.5]:
 add(x,-25,3,2.5,3.5,13)
 add(x,-25,3,3.1,4,2.4)
 add(x,-25,15.5,3.4,4.2,1)
add(0,-20,13.7,36,17,2.5)
# Low parapet around porch roof, leaving a visible shallow basin.
for x in [-17,17]:add(x,-20,16,1.3,17,1.5)
add(0,-28,16,35,1.3,1.5)
for i in range(3):add(0,-31+i*1.6,2.3+i*.45,36,2,.6)
# Low raised solar collectors, two long bands; integral frames and thickened posts.
for yy in [-5,18]:
 for x in range(-65,66,13):add(x,yy,47,1.3,12,2.2)
 add(0,yy,49,136,15,1.2)
 for x in range(-63,64,7):cut(x,yy,49.65,.65,14,.7)
 cut(0,yy,49.65,134,.65,.7)
# Roof-end and side evidence is limited: leave non-documented wall faces plain.
for i in range(3):add(0,-36+i*1.5,2.3+i*.45,140,2,.6)
result=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
m=result.to_mesh(); mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight,len(mesh.split()))
