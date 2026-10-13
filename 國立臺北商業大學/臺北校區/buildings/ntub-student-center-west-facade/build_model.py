'''國立臺北商業大學學生活動中心西向主立面段。2023公開照片近似，非全棟。毫米。'''
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
# Deliberate architectural SECTION rather than invented complete building depth.
# Front faces -Y. Flat rear is the artificial cut plane, not the real rear elevation.
add(0,0,0,150,48,3)
add(0,3,2.8,138,12,70)
# Seven structural bays, eight main piers. No glass mullions promoted to columns.
for x in [-69+i*(138/7) for i in range(8)]:
 add(x,-3.7,20,2.2,3.3,50)
# Upper continuous clerestory subdivided by heavy piers, shallow glazing recess.
for i in range(7):
 x=-69+(i+.5)*138/7
 cut(x,-3.7,56.8,17.4,3.8,11.6)
 # Fin rhythm visually approximated, thickened for 150mm scale. They are backed.
 for j in range(7):details.append(box(x-7.5+j*2.5,-4.1,56.3,1.15,4.2,12.5))
 # Narrow lower strip window; retain a broad blank central wall panel.
 cut(x,-3.7,31.6,17.4,3.8,4.4)
 # Window subdivisions are shallow backed details, not freestanding posts.
 for j in [-5,0,5]:details.append(box(x+j,-2.0,31.5,.9,2.0,4.6))
# Heavy flat upper cornice, as visible from high-angle photo22.
add(0,-3.2,69.5,142,5.2,3.7)
# Lower side bays have deep vertical sunshades, distinct from structural piers.
for side in [-1,1]:
 cut(side*51,-3.5,8,33,3.4,17.6)
 for x in [37,43,49,55,61,67]:details.append(box(side*x,-5.8,7.6,1.35,6.8,18.4))
# Entrance glass recess under canopy. Three broad portal groups, no invented corridor.
cut(0,-3.5,6.8,61,3.5,16)
for x in [-30,-10,10,30]:details.append(box(x,-2.0,6.5,1.15,2.0,16.5))
for x in [-20,0,20]:details.append(box(x,-2.0,6.5,.95,2.0,16.5))
details.append(box(0,-2.0,16.3,62,2.0,1.1))
# Deep entrance canopy and lowered central sign panel, not a pitched roof.
add(0,-8.3,23.3,73,15,3.2)
add(0,-14.8,22.2,27,2.5,5.4)
# Canopy support piers shown between doors. Fused at foot, rear and canopy.
for x in [-10,10]:add(x,-7.2,6.0,2.2,4.8,17.8)
# Broad low stairway, six robust treads.
for i in range(6):add(0,-19.3+i*1.6,2.8,70,3.1,.65*(i+1))
# Small left landing sidewall; no thin decorative handrails included.
add(-37,-10,2.8,2,16,6.4)
solid=parts[0]
for p in parts[1:]:solid+=p
for c in cuts:solid-=c
for p in details:solid+=p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print(mesh.extents,mesh.is_watertight)
