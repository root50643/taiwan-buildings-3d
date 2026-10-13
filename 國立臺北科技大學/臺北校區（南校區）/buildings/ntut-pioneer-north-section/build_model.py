"""Original parametric photo study of NTUT Pioneer north frontage and short returns.
This is an explicitly cut section, NOT the full building. Millimetres.
North street front faces -Y; model +X is the western stepped return.
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
# A short, flat cut boundary at y=16. This closes the miniature for printing;
# it is not a real facade or a surveyed partition. No invented rear windows.
add(0,0,0,104,52,3)
add(0,9,2.8,83,14,18.7)
# Double-height north colonnade and lobby with four major rectangular piers.
for x in [-35,-12,12,35]:add(x,-13,2.8,4.5,4.8,19.0)
add(0,-.2,20.3,87,32.4,2.6)
# Recessed glazed lobby, backed mullions, connected entrance canopy.
for x in np.linspace(-36,36,13):add(float(x),1.7,3,1.1,2.2,17.7)
for z in [7.7,13.8]:add(0,1.6,z,78,2.4,1.1)
add(-9,-10,11.8,57,15,1.7)
for x in [-34,-9,16]:add(x,-13,11.5,1.6,6.8,2.2)
# Front second/third-storey gallery beneath tower; shadow pocket and wide belt.
add(0,3,22.6,81,26,10.9)
cut(0,-10,24.0,77,3.4,7.2)
for x in np.linspace(-36,36,13):details.append(box(float(x),-9.1,24,1.1,2.4,7.2))
add(0,-1,32.3,87,34,2.6)
add(0,-16.8,34.0,85,1.5,2.5)
# Main tower front, only its first 25 mm of depth retained.
add(0,3.3,34.8,80,25.4,111.2)
# Eight characteristic narrow planes, each with nine protruding louvred boxes
# and adjacent broad recessed windows. Thickened mullions are backed, not free.
for i in range(8):
 x=-35+i*10
 add(x-3.6,-9.5,35.0,2.2,2.2,111.0) # shortened to roof line, no isolated tip
 for j in range(9):
  z=36.2+j*12.0
  if j<8:
   cut(x+.9,-9.3,z+3.2,5.9,3.0,4.1)
   details.append(box(x+.9,-8.7,z+3.2,1.0,2.3,4.1))
   details.append(box(x+.9,-8.7,z+5.1,5.9,2.3,1.0))
  add(x-3.0,-11.2,z,3.7,5.7,4.4)
  # Louver relief: solid-backed 0.9 mm pitch, no detached razor-blades.
  for k in range(3):cut(x-3.0,-14.03,z+.75+k*1.2,3.8,.38,.36)
 # Upper crown has two rows of dark apertures and rising vertical fins.
 for z in [130.0,139.0]:cut(x+.15,-9.3,z,3.1,3.2,4.0)
# East end tall narrow blade, the school lettering is deliberately omitted.
add(-42.0,2.2,30.5,3.3,27.6,115.5)
for z in np.arange(34,145,4.4):cut(-42.0,-11.7,float(z),3.4,.45,.3)
# West return: retain the near hanging box and its large open terrace below.
# The second more distant box, rear flank, and roof equipment are out of scope.
# Lower screen and side continuation of the podium.
add(42.1,6.8,3.0,3.5,18.4,26.5)
add(42.2,-.2,30.0,9.2,32.4,3.0)
# Near side upper suspended mass with terrace below and a supporting pier.
add(43.2,2.5,77.0,10.4,23.0,46.5)
add(42.4,4.1,47.0,3.2,3.4,30.4)
add(42.4,-.2,45.8,9.0,32.4,2.6)
# The flank recess is a large architectural void, not shallow embossing.
cut(42.0,5.5,49.0,12.0,19.0,26.0)
# Reconnect the backing/cut plane behind the terrace; this is the section backing.
add(38.0,13.8,33.0,4.0,4.4,92)
# Sparse staggered small square windows on the hanging volume.
for yy,z in [(-4,86),(8,95),(-4,107),(8,117)]:cut(48.3,yy,z,2.0,2.3,2.3)
# Open roof-side loggia; major posts and beams preserved.
for yy in [-8.5,11.5]:add(44.7,yy,122.8,2.4,2.6,22.1)
add(44.7,1.5,143.2,2.4,22.6,2.4)
add(39.8,1.5,143.2,11.7,2.6,2.4)
add(44.8,1.5,123,2.6,22.6,2.0)
# Entrance platform/three low broad steps.
for j in range(3):add(0,-20+j*2,2.8,83,2.6,.55*(j+1))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1,[(p.volume(),p.bounding_box()) for p in solid.decompose()]
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
# Uniform independent scale, including base, to exactly 150 mm overall.
mesh.apply_scale(150.0/mesh.extents.max())
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight,'faces',len(mesh.faces))
