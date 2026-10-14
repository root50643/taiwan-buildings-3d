"""2021北護學思樓，官方平面／完工照片限定近似。Units: final millimetres.
X positive east; Y positive north; model long axis not rotated to true north.
Height is bounded image-proportioned, not the unallocated project 49.9m claim.
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
L=136.8;D=64.8;BASE=3
F=[3,11.5,19.4,27.2,34.5,41.8,49.1,56.4,63.7,71,78.3,86.2]
add(0,0,0,150,78,3)
# Ground-floor colonnade and recessed glazed envelope; solid 2F/3F podium above.
add(0,0,2.8,129,54,8.8)
for y in [-31.2,31.2]:
 for x in [-66,-50,-34,-18,-2,14,30,46,66]:add(x,y,2.8,2.6,2.6,9)
for x in [-67,67]:
 for y in [-20,20]:add(x,y,2.8,2.6,2.6,9)
core=box(0,0,11.5,L,D,74.7)
# Eccentric court above 3F and two externally open short-side notches.
for v in [box(12.7,0,27.2,31.5,16.4,80),box(-60,0,11.5,18,16.4,74.7),box(65,0,11.5,12,16.4,52.2),box(60,0,63.7,18,16.4,22.5)]:core=core-v
parts.append(core)
# West conference roof and two separate equipment pavilions, all court-clear.
add(-48.5,0,85.7,39.8,65.8,3.3)
add(-17,0,86.0,15,38,3.8)
add(37,0,86.0,14,30,3.3)
# Solar fields are shallow, backed rectangles, not separate thin floating panels.
add(-17,3,89.5,13,24,1.0)
add(37,3,89.0,12,20,1.0)
# End equipment blocks, restrained to photographed roof zone.
for x in [51,60]:
 for y in [-24,24]:add(x,y,86.0,6,6,2.8)
# Roof perimeter and court rim have a robust 1.5mm actual section.
for y in [-31.7,31.7]:add(0,y,85.7,137.5,1.5,1.8)
for x in [-67.7,67.7]:
 for y in [-20,20]:add(x,y,85.7,1.5,23.2,1.8)
for y in [-8.8,8.8]:add(12.7,y,85.7,32.8,1.5,1.8)
for x in [-3.8,29.2]:add(x,0,85.7,1.5,19,1.8)
# West upper grille closes only the mouth, leaving the recess behind open below.
add(-67.7,0,64.0,1.5,17.2,22)
for y in np.arange(-7,7.1,2.3):cut(-68.45,y,65.2,.6,1.1,19.5)
# Major facade slabs are continuous. Window cuts stay >1mm clear of each slab.
for z in F[1:]:
 for y in [-32.5,32.5]:add(0,y,z-.4,137.6,1.4,1.2)
# Pronounced south structural grid, unlike north's inset four-row panel.
for x in [-65.5,-50.5,-35.5,-20.5,-5.5,9.5,24.5,39.5]:add(x,-33.0,11.5,2.6,1.6,66.8)
for x in [-66,-50,-34,-18,-2,14,30,46]:
 add(x,32.8,11.5,2.4,1.6,22.5)
 add(x,32.8,64.0,2.4,1.6,7.0)
# South (playing-field) elevation: seven large teaching bays, slender stair strip,
# and independent eastern outer bay. Dense glass mullions remain backed.
south_centers=[-58,-43,-28,-13,2,17,32]
for fi in range(2,10):
 z=F[fi]+1.5;h=F[fi+1]-F[fi]-2.8
 for x in south_centers:
  # Two low-level opaque spandrels are intentionally not turned into glazed voids.
  if fi==2 and x in [-28,2]:continue
  cut(x,-32.45,z,12.2,1.1,h)
  for dx in [-3.8,0,3.8]:details.append(box(x+dx,-32.1,z,1.0,.7,h))
for z,h in [(F[10]+1.5,5.2)]:
 for x in np.arange(-61,37,6.4):
  for dx in [-1.1,1.1]:cut(x+dx,-32.45,z,1.35,1.1,h)
# South tall east circulation bar, flanked by a narrow stair-glass strip.
add(43,-32.75,11.5,5.5,2.3,74.7)
for fi in range(1,11):
 z=F[fi]+1.5;h=F[fi+1]-F[fi]-2.8
 cut(38.6,-32.6,z,3.0,1.2,h)
 cut(56.8,-32.45,z,15.0,1.1,h)
 for x in [51.8,56.8,61.8]:details.append(box(x,-32.1,z,1.05,.7,h))
# South ground entrance and clerestory are in the inset wall, not free meshes.
for x in [-56,-40,-24,-8,8,24,40,56]:cut(x,-27,4.2,11,1.0,5.8)
# North facade: lower and ninth-floor wide glazing, 5F-8F framed office pattern,
# then two upper office rows and the west conference grille.
for fi in [1,2,3,8]:
 z=F[fi]+1.5;h=F[fi+1]-F[fi]-2.8
 for x in [-58,-42,-26,-10,6,22,38]:
  cut(x,32.45,z,12.6,1.1,h)
  for dx in [-4,0,4]:details.append(box(x+dx,32.1,z,1.0,.7,h))
for fi in [4,5,6,7]:
 z=F[fi]+1.4;h=F[fi+1]-F[fi]-2.7
 # Left-to-right pattern includes paired lights with unequal panel groups.
 for x in np.arange(-62,27,6.5):
  for dx in [-1.15,1.15]:cut(x+dx,32.45,z,1.5,1.1,h)
 for x in [35.5,43]:cut(x,32.45,z,5.7,1.1,h)
# Distinct large frame around middle four rows; all pieces fused to backing.
for x in [-67,28.5]:add(x,32.8,34.0,1.8,1.7,30.4)
for z in [34.0,63.3]:add(-19.2,32.8,z,97,1.7,1.5)
for fi in [9,10]:
 z=F[fi]+1.4;h=F[fi+1]-F[fi]-2.7
 for x in np.arange(-25,47,6.4):
  for dx in [-1.15,1.15]:cut(x+dx,32.45,z,1.5,1.1,h)
# Western conference grille is one two-storey recessed field, not paired slit rows.
cut(-49,32.45,72.4,33,1.1,12.4)
for x in np.arange(-64,-32,2.4):details.append(box(x,32.1,72.4,1.05,.7,12.4))
details.append(box(-49,32.1,78.3,33,.7,1.1))
# North east solid tower stripe with narrow vertical light slots.
add(57,32.7,11.5,12,2,74.7)
for x in [53.2,59.7]:cut(x,33.7,15,1.7,1.0,53)
for fi in [9,10]:cut(57,33.7,F[fi]+1.4,2.3,1.0,4.8)
# Court inner openings; unmistakable open rectangular well with floor preserved.
for fi in range(3,11):
 z=F[fi]+1.4;h=F[fi+1]-F[fi]-2.8
 for y in [-8.2,8.2]:
  for x in [1,8.8,16.6,24.4]:cut(x,y,z,5.7,1.0,h)
# Both end slots have recessed stair landings, not vertical filled cylinders.
for fi in range(2,9):
 add(-52.5,0,F[fi]-.3,4.0,16.8,1.4)
 add(59.0,0,F[fi]-.3,3.0,16.8,1.4)
# West short-face wall: broad solid side cheeks, long narrow slot and small lights.
for z in [18,32,48,64,74]:
 cut(-68.4,-18,z,1.1,1.7,4.6)
cut(-68.4,-23,22,1.1,1.5,46)
for z in [14,58,72]:cut(-68.4,22,z,1.1,2.5,2.8)
# East short wall has conservatively simplified backed vertical windows.
for z in [20,36,52,68]:
 for y in [-21,21]:cut(68.4,y,z,1.1,2.5,5)
# Entrance canopy and a broad fused low apron.
add(-8,-30,10,31,7.5,1.5)
add(-8,-35,2.8,32,5,1.0)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for p in cuts:solid=solid-p
for p in details:solid=solid+p
print('components',[(q.volume(),q.bounding_box()) for q in solid.decompose()]);assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
