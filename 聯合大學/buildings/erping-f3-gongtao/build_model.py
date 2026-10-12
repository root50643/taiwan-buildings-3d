"""F3：官方照片近似外觀；單位 mm，非測量模型。"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold,OpType
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
# Four storeys with a taller solar pergola and descending forecourt.
add(0,0,0,150,106,2.4)
# Raised terrace is deliberately local to this building; no neighboring halls.
add(0,8,2.3,146,78,5)
add(0,18,7.2,140,44,58)
# Deep vertical piers; louvers between pairs, encoded as solid printable relief.
for x in range(-54,67,12):add(x,-5,8,1.9,3,56)
for x in [-48,-36,-24,-12,12,24,36,48,60]:
 add(x,-4.5,8,4.8,2,55)
 for xx in [x-1.6,x,x+1.6]:add(xx,-5.8,8,.8,1.8,55)
for z in [12,26,40,54]:
 for x in [-58,-42,-30,-18,-6,2,18,30,42,54]:
  cut(x,-4,z,6.5,2.4,7.5)
  add(x,-4.9,z+5.8,6.5,1.6,.8)
  add(x,-4.9,z,.8,1.6,7.2)
# Leftmost enclosed service bay has three small windows per floor.
for z in [12,26,40,54]:
 for x in [-67,-63,-59]:cut(x,-4,z+3,2.7,2.3,3.7)
add(0,18,65,143,46,5.2)
# Roof solar pergola. Closely spaced robust posts support the real raised canopy silhouette.
for x in range(-66,67,12):
 for y in [0,18,36]:add(x,y,70,1.2,1.2,5.3)
for y in [0,18,36]:add(0,y,74,138,1.3,1.3)
add(0,18,75,140,40,1.2)
for x in range(-66,67,6):cut(x,18,75.55,.65,39,.75)
for y in [7,17,27]:cut(0,y,75.55,138,.65,.75)
# Central entry with thick projecting side cheeks and a broad name lintel.
cut(0,-4,10.5,13,2.7,11)
for x in [-8.7,8.7]:add(x,-7,7,3,8,17)
add(0,-7,21.8,20.5,9,3.4)
for z in [12,14,16,18,20]:cut(0,-5.1,z,12,1,.65)
for i in range(5):add(0,-17+i*1.3,7+i*.65,16,2,.85)
# Round inlaid plaza: recessed annulus, then the wide descent to the lower path.
add(0,-24,7,39,24,.8)
ring=Manifold.cylinder(.8,11.4,11.4,96)-Manifold.cylinder(1,10.6,10.6,96).translate((0,0,-.1))
cuts.append(ring.translate((0,-24,7.25)))
for i in range(9):add(0,-49+i*2,2.3+i*.56,22,2.5,.8)
# Rear and side walls remain deliberately unfenestrated: not established by the photos.
result=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
m=result.to_mesh(); mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight,len(mesh.split()))
