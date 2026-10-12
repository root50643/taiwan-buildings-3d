"""NHRI Zhunan existing biologics pilot-plant main exterior, photo-derived mm miniature.
Models main tall mass and attached low wing only; no laboratory or service layout.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
# Base is 150 mm deep; standalone approximate scale.
add(0,0,0,128,150,3)
# Tall flat-roof rectangular slab and low two-level glazed wing visible in both sources.
add(-21,0,2.8,46,123,79)
add(30,-22,2.8,58,64,29)
# Taller end frame and roof-edge coping; no inferred mechanical/roof equipment.
add(-18,-56,80,43,11,4.4)
add(-44.2,0,80.5,1.6,125,1.5)
# Broad long-side recessed glazing, leaving stone ribs between six bays.
for y in [-49,-29,-9,11,31,51]:
 for z in [23,37,51,65]:
  cut(-44.0,y,z,1.6,16.8,11.5)
  for yy in [y-5.4,y,y+5.4]:details.append(box(-43.6,yy,z,1.4,1.0,11.5))
# Horizontal white sunshade bands, small robust projection, photo-observed long side.
for z in [21,35,49,63,77.5]:add(-44.7,0,z,2.2,124,1.45)
# Narrow end glass strip and a broader grid within the tall white portal.
for x,w in [(-39,6.5),(-15,18.0)]:
 for z in [22,36,50,64]:
  cut(x,-61.5,z,w,1.6,11.8)
  for xx in np.arange(x-w/2+3.0,x+w/2,3.6):details.append(box(float(xx),-61.6,z,1.0,1.8,11.8))
# Right front-edge strip visible beyond the white end frame.
for z in [22,36,50,64]:cut(1.0,-61.5,z,1.6,1.6,11.8)
# Recessed ground-floor entrance zone, backed by a solid wall; stout outer columns.
cut(-21,-59.9,3,37,4.8,16.0)
for x in [-41,-1.5]:details.append(box(x,-61.0,3,3.3,3.0,18))
# Long-side stone colonnade reading as relief, not fabricated internal room divisions.
for y in [-49,-29,-9,11,31,51]:cut(-44,y,5,1.7,14.3,12)
# Low wing: two continuous glass ribbons divided by visible slender mullions.
for z in [6,19]:
 cut(32,-54.0,z,49,1.6,9.8)
 cut(59.0,-22,z,1.6,54,9.8)
 for x in np.arange(11,56,7.5):details.append(box(float(x),-54.05,z,1.0,1.8,9.8))
 for y in np.arange(-45,3,8):details.append(box(59.05,float(y),z,1.8,1.0,9.8))
# Shallow public entrance steps, joined to the plinth.
for i in range(3):add(-24,-66+i*1.5,3,18,1.7,.7*(i+1))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for q in details:solid=solid+q
solid=solid.simplify(.0001);m=solid.to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.update_faces(mesh.nondegenerate_faces());mesh.update_faces(mesh.unique_faces());mesh.remove_unreferenced_vertices()
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('Dimensions mm',mesh.extents,'watertight',mesh.is_watertight,'solid count',len(solid.decompose()))
