"""NIU 經德大樓. Self-authored photo/evacuation-plan based exterior approximation.
Preserves the central lightwell, corner ventilation voids, curved landings and
terraced upper two levels. Dimensions are visual estimates, in millimetres.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];late=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def prism(poly,z,h):
 area=sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))
 if area<0:poly=list(reversed(poly))
 return CrossSection([poly]).extrude(h).translate((0,0,z))
def quarter(cx,cy,z,r,h):
 pts=[(cx,cy)]+[(cx+r*math.cos(t),cy+r*math.sin(t)) for t in np.linspace(-math.pi/2,0,25)]
 return prism(pts,z,h)
add(0,0,0,138,150,3)
# Lower five floors: square-ring block with open court.
ring=box(0,0,2.8,112,128,49.2)-box(0,0,2.7,53,65,50)
# The two east wind openings are deliberately through-open, never blind texture.
ring=ring-box(43,-48,12.2,34,34,40.5)-box(43,48,12.2,34,34,40.5)
parts.append(ring)
# Six and seven floors: asymmetric setbacks, plus the full-height rear wing.
add(-10,-50,51.8,92,28,9.2)
add(-22,-50,60.8,68,28,9.2)
add(-42,0,51.8,28,128,18.2)
add(42,17,51.8,28,94,18.2)
add(0,50,51.8,112,28,18.2)
# Patio edges are broad enough to be fused at scale. 1.5 mm parapets.
add(42,-48,50.2,28,32,1.8)
add(28,-63,51.8,55,1.6,2.0)
add(54,-46,51.8,1.6,36,2.0)
add(11,-63,60.8,18,1.6,2)
add(19,-50,60.8,1.6,27,2)
# Individual roof caps below follow only existing upper-floor mass.
cut(28,-62.8,61,55,2.4,12)
cut(12,-62.8,70,19,2.4,3)
# Front classroom fenestration has two panes separated by a robust backed sill.
for floor in range(7):
 z=5.0+floor*9.3
 xs=[-48,-38,-28,-18,-8,2,12,22,32,42,51]
 for x in xs:
  if floor==5 and x>30:continue
  if floor==6 and x>10:continue
  if floor in [1,2,3,4] and x>25:continue
  cut(x,-63.4,z,7.2,3.0,5.9)
  late.append(box(x,-62.5,z+2.3,7.3,1.8,1.0))
# West elevation continuous rows with deep concrete reveals.
for floor in range(7):
 z=5.0+floor*9.3
 for y in [-55,-44,-33,-22,-11,0,11,22,33,44,55]:
  cut(-55.4,y,z,3.0,7.3,5.9)
  if floor>0 or abs(y)>9:late.append(box(-54.7,y,z+2.3,1.8,7.4,1.0))
# Rear and east wing: asymmetric stair strip, six large window groups.
for floor in range(7):
 z=5.0+floor*9.3
 for x in [-47,-35,-23,-11,1,13,25,37,49]:cut(x,63.5,z,8,2.8,5.9)
 for y in [-20,-8,4,16,28,40,52]:
  cut(55.5,y,z,2.8,8.4,5.9)
# Hollow-brick screens on the east facade are backed relief grids at miniature
# scale; the old and 2021 architect views distinguish them from classroom windows.
for floor in range(5):
 z=5.0+floor*9.3
 for y in [-20,-8]:
  for off in [-2.1,0,2.1]:late.append(box(54.9,y+off,z,1.6,1.0,5.9))
  for zz in [z+1.45,z+2.9,z+4.35]:late.append(box(54.9,y,zz,1.6,8.4,.9))
# Open galleries around inner court; true recess with thick floor/rail bands.
for floor in range(7):
 z=5.5+floor*9.3
 for x in [-19,-6,7,20]:
  cut(x,35.1,z+1.6,10.3,5.8,5.7)
  if floor<5 or (floor==5 and x<29) or (floor==6 and x<10):cut(x,-35.1,z+1.6,10.3,5.8,5.7)
 for y in [-25,-12,1,14,27]:
  cut(-27,y,z+1.6,4.8,10.3,5.7)
  if abs(y)<20:cut(27,y,z+1.6,4.8,10.3,5.7)
# Curved exterior landings in wind slots. 1.5mm solid rails and 1.8mm slabs.
for sign in [-1,1]:
 for level in range(1,5):
  z=3+9.3*level
  q=quarter(26,-31,z,28.5,1.8)
  rim=quarter(26,-31,z+1.7,28.5,2.3)-quarter(26,-31,z+1.6,26.8,2.6)
  if sign>0:q=q.mirror((0,1,0));rim=rim.mirror((0,1,0))
  late.extend([q,rim])
 # Thin original stair core becomes a 3.0mm full-height attached structural pier.
 add(28,sign*33,3,3.0,3.0,49.5)
# A sinuous internal landing on the eastern court edge, inferred from plan and
# architect photo: three broad lobes fused into the inner gallery at each floor.
for level in range(1,7):
 if level==2:continue # modern canopy supplants open gallery here
 z=3+9.3*level
 outline=[(29,-18),(23,-18),(20,-16),(18,-12),(18,-8),(20,-4),(21,0),(20,4),(18,8),(18,12),(20,16),(23,18),(29,18)]
 landing=prism(outline,z,1.7)
 # Open wavy edge backed by full slab: extruded strip on the court side.
 edge=outline[1:-1]; inside=[(x+1.6,y) for x,y in reversed(edge)]
 railing=prism(edge+inside,z+1.6,2.0)
 late.extend([landing,railing])
# Rooftop stair tower, a strongly stepped silhouette in both historical and 2021 photos.
add(34,31,68.5,15,18,15.5)
add(34,31,79.5,16.5,19.5,2.0)
cut(34,21.8,73,10,2.2,4.3)
for x,y,w,d in [(-42,15,26,96),(41,18,26,92),(0,50,108,26),(-22,-50,65,26)]:
 # Roof lips represented as solid-backed 1.5mm edges, no unconnected roof rings.
 add(x,y,69.7,w,d,1.1)
# Central atrium has a low modern canopy since the 2021 architect visit.
# Retain the large open upper court; roof represented as plate at third-floor level.
add(0,0,23.5,53.4,65.4,1.7)
# Ground entrance on western side, portal into courtyard with low landing.
cut(-43,0,3,30,18,9)
for k in range(4):add(-62+k*1.4,0,3,1.6,21,.45*(k+1))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in late:solid=solid+p
print('components',[(p.volume(),p.bounding_box()) for p in solid.decompose()]);assert len(solid.decompose())==1
m=solid.simplify(1e-5).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj');print('dimensions_mm',mesh.extents,'watertight',mesh.is_watertight,'faces',len(mesh.faces))
