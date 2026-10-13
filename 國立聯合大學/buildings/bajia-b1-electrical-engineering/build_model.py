"""B1 electrical engineering building, NUU Bajia: photo-informed miniature.
Units: mm. No measured floor plan; see manifest and README for assumptions.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, OpType
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def windows_x(x,ys,zs,w=5,h=5):
 for y in ys:
  for z in zs:cut(x,y,z,1.4,w,h)
def windows_y(xs,y,zs,w=5,h=5):
 for x in xs:
  for z in zs:cut(x,y,z,w,1.4,h)
# Flat continuous print base. Front = -Y; the tall six-storey wing is at -X.
add(0,0,0,122,150,2.4)
# Main U-shaped six-storey body with an open roof courtyard.
add(-38,3,2.3,28,126,80)
add(0,53,2.3,104,26,79)
add(40,17,2.3,24,92,77)
# Lower front-side sign wall: very broad flat panel is a defining B1 feature.
add(-38,-53,2.3,28,25,64)
add(-38,-66,2.3,29,2,64.4)
# Two deep tall entrance-side stair masses with an inset glazed strip.
add(40,-47,2.3,24,36,68)
add(32,-61,2.3,8,13,71)
add(48,-50,2.3,8,30,70)
cut(41,-65,8,5,1.5,56)
for z in [12,24,36,48,60]:details.append(box(41,-64.65,z,5.2,1.5,.9))
# Front recess is deeper than the corner walls. A closed backing supports
# printable shallow corridor recesses; the courtyard beyond stays open to sky.
add(0,-48,2.3,52,9,65)
for z in [20,33,46]:
 cut(0,-52.5,z,47,3.2,10)
 # Three structural piers and balcony-edge bands.
 for x in [-19,0,19]:details.append(box(x,-52,z,1.7,3.8,10.2))
 details.append(box(0,-52,z,49,3.8,1.1))
# Continuous luminous upper bridge / screen, plus short lower entrance canopy.
add(0,-51.2,56,52,3.5,12)
for x in np.arange(-23,24,5.75):cut(x,-53.0,56.7,.65,.9,10.7)
# The photographed screen has conspicuous crossing braces in its lower half.
# 0.8 mm wide relief is anchored 0.3 mm into the solid panel, projecting 0.6 mm.
for x in np.arange(-22.75,23,6.5):
 for slope in [-1,1]:
  pts=[]
  for xx,zz in [(x-3,59.7-slope*3.0),(x+3,59.7+slope*3.0)]:
   for dx in [-.4,.4]:
    for yy in [-53.55,-52.6]:pts.append([xx+dx,yy,zz])
  details.append(Manifold.hull_points(pts))
add(0,-57,17.5,51,13,2)
# Fill canopy undersurface where it meets the stair platform to avoid a
# large free span; local overhangs still require slicer inspection.
add(0,-56,2.3,48,11,15.2)
for i in range(6):add(0,-64-i*1.3,2.3,45,1.5,12-i*1.8)
# Six repeated upper-side bay fins, only on observed tall side elevation.
for y in [-43,-26,-9,8,25,42]:
 add(-53,y,39,3.0,1.5,44)
 for z in [39,53,67]:
  add(-52.3,y+7.2,z,2.4,15,1.4)
 windows_x(-52, [y+6.5], [43,57,71],6,7)
# Side lower floors have grouped rectangular window openings.
windows_x(-52,[-44,-29,-14,1,16,31,46],[8,20,32],8,5)
# Rearward tall slit tower on the visible flank.
add(-54,53,2.3,5,9,88)
cut(-56.5,53,8,1.6,6,77)
for z in range(14,86,14):details.append(box(-56.1,53,z,1.5,6.4,1.1))
add(-40,54,83,29,11,7)
# Side elevation roof cap and shallow beam line.
add(-38,1,82,29.8,130,1.3)
add(0,53,80.5,105.8,27.8,1.3)
add(40,17,78.5,25.8,93.8,1.3)
# Roof solar arrays are simplified to anchored solid shallow pads with grid grooves.
for x,y,w,d,z in [(-38,-24,25,48,83.2),(-38,29,25,44,83.2),(0,53,47,23,81.7),(40,26,21,65,79.7)]:
 add(x,y,z,w,d,.85)
 for xx in np.arange(x-w/2+4,x+w/2,4):cut(xx,y,z+.5,.65,d-.8,.5)
 for yy in np.arange(y-d/2+7,y+d/2,7):cut(x,yy,z+.5,w-.8,.65,.5)
windows_y([-38],-60,[71],7,7)
# Courtyard wall openings, observed in aerial photo 21; window counts approximate.
windows_x(-24,[-26,-10,6,22,38],[10,24,38,52,66],7,7)
windows_x(28,[-12,5,22,39],[10,24,38,52,66],7,7)
windows_y([-17,-5,7,19],40,[10,24,38,52,66],7,7)
# Rear/outer right facade unseen in close views: conservative plain wall with
# sparse repeated recesses, explicitly approximate, no invented appendages.
windows_x(52,[-17,0,17,34,51],[9,23,37,51,65],6,6)
windows_y([-43,-28,-13,2,17,32,45],66,[9,23,37,51,65],6,6)
# Front tower small balconies supported directly against their wall.
for z in [18,32,46]:
 add(43,-65.8,z,14,3.2,1.4)
 windows_y([44],-65,[z+2],4,7)
# Sign wall has one low slit visible in the source; lettering intentionally omitted.
cut(-28,-67,18,3,1.2,15)
shape=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
shape=shape+Manifold.batch_boolean(details,OpType.Add)
m=shape.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('Exported',len(mesh.faces),'triangles',mesh.extents,'mm; watertight',mesh.is_watertight)
