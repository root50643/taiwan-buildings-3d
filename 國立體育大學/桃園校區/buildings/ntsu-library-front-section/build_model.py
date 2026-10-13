"""Photo-derived entrance section; millimetres, self-built approximate geometry.
Unobserved rear is a plain cut end, not a claimed reconstruction of the whole building.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
P=[];C=[];D=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):P.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):C.append(box(x,y,z,w,d,h))
def cyl(x,y,z,r,h):P.append(Manifold.cylinder(h,r,r,circular_segments=32).translate((x,y,z)))

# The observed front and short left return only; plain back is the section cut.
add(0,0,0,150,95,3)
add(0,12,2.8,130,47,83)
# Corner stone pier and opposite solid end, five occupied bands including parking.
add(-58,-14,2.8,10,10,89)
add(61,-12,2.8,11,10,85)
# Tall recessed glass bands with backed vertical sunshades, three upper major window rows.
for z in [31,49,67]:
 cut(0,-11, z,107,4,14)
 add(0,-14,z-2.1,112,9,2.2)
 for k in range(27):
  x=-51+3.92*k
  D.append(box(x,-12,z,1.2,7.0,14))
add(0,-14,82,113,9,2.2)
# Lower entrance glazing is partially concealed by the rising staircase.
cut(0,-11,15,107,4,12)
for x in [-43,-22,0,22,43]:D.append(box(x,-12,15,1.5,7.0,12))
# Parking undercroft openings, retained as deep rectangular recesses.
for x in [-43,-21,1]:cut(x,-11,3,17,7,9)
# Left return long open balcony bands seen in official side angle.
for z in [14,31,49,67]:cut(-65,13,z,4,37,12)
# Facade staircase ascends from front-left toward the entry landing on right.
for i in range(20):add(-54+i*4.5,-32,2.8,4.6,17,1+(i+1)*.78)
add(42,-25,2.8,32,30,17)
# Solid low parapet follows stair; larger than fragile handrail wire.
for i in range(20):add(-54+i*4.5,-41,3.6+(i+1)*.78,4.6,1.8,3)
# Main building remains photo section, no fabricated rear window grid.

solid=P[0]
for p in P[1:]:solid=solid+p
for c in C:solid=solid-c
for d in D:solid=solid+d
assert len(solid.decompose())==1
m=solid.to_mesh64();mesh=trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,len(mesh.faces),mesh.is_watertight)
