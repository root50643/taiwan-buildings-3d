"""F1 建築一館：依官方照片近似外觀；單位 mm，並非測量模型。"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold,OpType
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
# Front faces negative Y; the neighboring H1 and F2 are deliberately excluded.
add(0,0,0,150,80,2.4)
add(0,7,2.3,140,42,82)
# Long corrugated-looking high roof fascia, thickened to printable relief.
add(0,7,84,142,43,9)
for z in [85.5,87.7,89.9]:cut(0,-14.5,z,140,1.2,.7)
add(0,7,92.5,143,44,1.3)
# Six horizontal clerestory windows on left, two tall vertically aligned windows near center.
for z in [38,64]:
 for x in [-60,-51,-42,-29,-20,-11]:cut(x,-14,z,7.6,2.3,4)
 for x in [-66,-56,-47,-37,-34,-24,-15,-5]:add(x,-15,z-2,1.2,2.5,10)
 add(-35,-15,z-1.5,63,2.4,1.1)
 for x in [-63,-38,-33,-7]:cut(x,-14,z-8,1.0,1.8,5.7)
 cut(8,-14,z-13,13,2.2,16)
 for x in [.5,15.5]:add(x,-15,z-14,1.3,2.4,19)
 add(8,-15,z-14,16,2.4,1.2)
 # Fine center mullion omitted to avoid isolated print detail.
# Ground-floor left slit windows and masonry annex with a sloping cap.
for x in [-61]:cut(x,-14,15,7.8,2.2,4.5)
add(-31,-20,2.3,43,15,16)
# Instead use a robust sloped wedge sharing the annex wall.
from manifold3d import Mesh
v=np.array([[-53,-28,17],[-9,-28,17],[-9,-12,17],[-53,-12,17],[-53,-28,18.5],[-9,-28,18.5],[-9,-12,23],[-53,-12,23]],dtype=np.float32)
f=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]],dtype=np.uint32)
parts.append(Manifold(Mesh(v,f)))
for z in [5,8,11,14]:cut(-31,-27.5,z,41,1.2,.65)
# Right shopfront glazing, its projecting sign fascia, and recessed center doorway.
for x in [25,37,49,61]:cut(x,-14,5,10,2.3,15)
add(44,-16,20,53,6,5)
cut(44,-19,21,49,1.4,2.7)
cut(8,-14,3,12,2.4,16)
add(8,-18,19,16,9,2)
for i in range(3):add(8,-29+i*2,2.3+i*.8,15,8-i*2,.85)
# Forecourt change of level, kept compact rather than including the basketball court.
for i in range(3):add(0,-37+i*2,2.3+i*.65,141,2.5,.8)
# Rear and narrow sides remain blank because the supplied photographs do not establish them.
result=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
m=result.to_mesh(); mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight,len(mesh.split()))
