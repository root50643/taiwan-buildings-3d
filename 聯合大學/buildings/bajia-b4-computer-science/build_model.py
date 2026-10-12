"""B4 資訊工程館. Photo-informed, approximate FDM miniature in millimetres."""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, OpType
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def mull(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
# Bed-facing plinth. Main elevation faces negative Y.
add(0,0,0,150,70,2.4)
add(0,1,2.3,134,48,66)
# Shallow terrace and entrance steps.
add(0,-27,2.3,139,9,1.1)
add(-8,-31,2.3,24,4,.7)
add(-8,-33,2.3,24,2,.35)
# Front wall panels: original green/white material areas become subtle relief.
add(39,-23.5,3.1,18,1.8,65)
add(27,-23.45,17.4,40,1.7,13.1)
add(27,-23.45,41.9,40,1.7,14.4)
# Five-storey left frame, and narrow stair glazing tower.
add(-59,-24,2.3,15,4,66)
cut(-59,-26,5,10.6,1.8,59)
for xx in [-62,-58]:mull(xx,-25.55,5,.9,1.4,59)
for z in [15.5,28,40.5,53]:mull(-59,-25.55,z,11,1.4,1)
add(-47,-24,2.3,17,3,59)
# Front window bays and corridors, five levels. Depths kept small for printing.
for xx in [-45,-24,-2,20]:
 for z in [7,19.5,32,44.5,57]:
  cut(xx,-24.2,z,12,5.6,7.1)
  for dx in [-3.5,0,3.5]:mull(xx+dx,-23.1,z,.85,4,7.1)
  mull(xx,-23.1,z+4.8,12,4,.85)
# Tall alternating white ceramic pilasters across middle floors.
for xx in [-35,-21,-7,7,21]:mull(xx,-23.8,19,6.2,6.4,39.4)
# Recessed full-height entrance at centre: two-storey vestibule.
cut(-6,-24.3,3.4,16,5.2,17)
for xx in [-11,-6,-1]:mull(xx,-24.1,3.4,.95,5.4,17)
for z in [9.5,15]:mull(-6,-24.1,z,16,5.4,.95)
# Right open stair gallery beside the prominent glazed corner.
for z in [7,19.5,32,44.5,57]:cut(51,-23.6,z,8,2.6,8.6)
add(62,-23.6,17.5,12,1.5,50.8)
cut(62,-24.4,18.4,10.1,1.4,48.3)
for xx in [58.7,62,65.3]:mull(xx,-23.95,18.4,.85,1.4,48.3)
for z in [29.8,42.2,54.6,60.1]:mull(62,-23.95,z,10.4,1.4,.9)
# Diagonal stair-flight spandrels seen in the left tower close-up.
for z in [15.5,28,40.5,53]:
 pts=[[x,y,zz] for y in [-27.2,-24.3] for x,zz in [(-64,z-5),(-54,z+1),(-54,z+4.6),(-64,z-1.4)]]
 details.append(Manifold.hull_points(pts))
# Broad near-blank short side seen in the oblique source. Thin sign panel only;
# Chinese lettering is intentionally omitted at this scale.
add(67.35,-12,3,1.3,8,64)
cut(68,-12,8,1.4,3,10)
# Yellow upper-floor band and small projecting eave translated into relief.
add(-7,-23.3,64.1,79,1.3,4.5)
add(-7,-24,68,80,2.9,1.1)
# Roof edge, low plant blocks visible above rear roofline. No fabricated roof kit.
add(0,1,68,135,49,1.1)
add(-53,8,68.8,17,21,4.4)
add(19,15,68.8,26,15,4)
# Rear elevation: schematic because reference is distant/obscured.
for xx in [-52,-38,-24,-10,4,18,32,46,60]:
 for z in [8,20.5,33,45.5,58]:
  cut(xx,25,z,6.4,1.4,6.3)
  mull(xx,24.7,z,.9,1.1,6.3)
for z in [17,29.5,42,54.5]:add(0,25.2,z,130,.8,.9)
# Left end side glazing. Simplified from the narrow stair tower photo.
for yy in [-16,-6,4]:
 for z in [8,20.5,33,45.5,58]:cut(-67,yy,z,1.5,6,7)
shape=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
shape=shape+Manifold.batch_boolean(details,OpType.Add)
m=shape.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('Exported',len(mesh.faces),'triangles',mesh.extents,'mm; watertight',mesh.is_watertight)
