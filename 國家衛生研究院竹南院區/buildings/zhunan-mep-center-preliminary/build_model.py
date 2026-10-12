"""NHRI Zhunan MEP center: approximate public-exterior massing in millimeters.
Identity is MEDIUM confidence, from an old labeled map and the 2017 aerial.
No facade openings, roof equipment, pipes, interior, or service layout is inferred.
Run with the dependencies in requirements.txt. Output is beside this script.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold
OUT=Path(__file__).resolve().parent
parts=[]
def box(x,y,z,w,d,h):
    return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):
    parts.append(box(x,y,z,w,d,h))
# Independent miniature: the integrated base is exactly 150 mm long.
add(0,0,0,150,72,3)
# Only the broad stepped/L-shaped exterior silhouette is supported by the aerial.
# The end volume projects beyond the long wing; all lengths/heights are estimates.
add(-45,0,2.8,40,50,20.7)
add(18,4,2.8,94,42,18.7)
# Shallow roof-edge relief follows the visible low flat-roof outline.
# The roof remains fully solid and unoccupied; no inner shell or service layout.
for x,y,w,d in [(-64.2,0,1.6,50),(-45,-24.2,40,1.6),(-45,24.2,40,1.6)]:
    add(x,y,23.3,w,d,1.5)
# The elevated left-end roof edge stops where the lower long wing begins.
add(-25.8,0,23.3,1.6,50,1.5)
for x,y,w,d in [(64.2,4,1.6,42),(20,24.2,90,1.6),(20,-16.2,90,1.6)]:
    add(x,y,21.3,w,d,1.5)
solid=parts[0]
for p in parts[1:]:
    solid=solid+p
solid=solid.simplify(.0001)
m=solid.to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.update_faces(mesh.nondegenerate_faces());mesh.update_faces(mesh.unique_faces());mesh.remove_unreferenced_vertices()
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('Dimensions mm',mesh.extents,'watertight',mesh.is_watertight,'solid count',len(solid.decompose()))
