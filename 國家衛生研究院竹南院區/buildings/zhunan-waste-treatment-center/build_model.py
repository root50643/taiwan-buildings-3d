"""NHRI Zhunan waste-center public exterior only. Photo-derived dimensions in mm.
The shutters stay closed relief: no service, process, pipe or equipment layout.
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
add(0,0,0,150,84,3)
# One broad tall parapet-front rectangle and visibly lower left attached extension.
add(14,4,2.8,104,55,48)
add(-54,7,2.8,33,43,32)
add(-43,8,34.4,13,39,5)
# Broad closed roller shutters: shallow panels, deliberately never through-openings.
for x,w in [(-10,35),(34,42)]:
 cut(x,-23.5,3,w,1.8,22.5)
 for z in np.arange(4.4,24,2.0):cuts.append(box(x,-22.7,float(z),w-1.0,.35,.42))
 add(x,-24.1,25.5,w+1.3,2.0,2.2)
# Public-facing left entrance window panel visible in panorama, partly screened by trees.
for x in [-64,-57,-50]:cut(x,-14.5,4.5,5.5,1.6,11.5)
add(-55,-15.1,22.5,28,2.5,2.8)
# Coarse exterior tile-joint relief, not individual fragile tiles.
for x in np.arange(-36,66,9):cut(float(x),-23.5,28.3,.3,.65,21.5)
for z in [33,41.5,49.5]:cut(14,-23.5,z,104,.65,.3)
# Photo-observed coping line, robust integrated roof edge.
add(14,-23.1,50.5,104.8,2.2,1.1)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
solid=solid.simplify(.0001);m=solid.to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.update_faces(mesh.nondegenerate_faces());mesh.update_faces(mesh.unique_faces());mesh.remove_unreferenced_vertices()
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('Dimensions mm',mesh.extents,'watertight',mesh.is_watertight,'solid count',len(solid.decompose()))
