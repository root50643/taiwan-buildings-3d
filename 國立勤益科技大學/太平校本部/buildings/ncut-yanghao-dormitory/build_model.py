"""NCUT Yanghao Dormitory C/D connected Z group, original photo-derived model.
Units mm. Official completed-project opposite aerials + official campus footprint.
Not a survey. Counts refer to observable major facade groups, not every room.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def poly(p,z,h):
 if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))<0:p=p[::-1]
 return CrossSection([p]).extrude(h).translate((0,0,z))
def rod(a,b,r=.65):
 a=np.array(a);v=np.array(b)-a;length=np.linalg.norm(v);axis=np.cross([0,0,1],v/length);ang=math.degrees(math.acos(v[2]/length))
 # Manifold Euler rotation for a vertical cylinder into the segment vector.
 theta=math.degrees(math.atan2(v[1],v[0]));phi=math.degrees(math.acos(v[2]/length))
 return Manifold.cylinder(length,r,r,circular_segments=12).rotate((0,phi,theta)).translate(a)
add(0,0,0,150,87,3)
# Z footprint: upper longer wing, offset lower shorter wing, joined common-room core.
# Opposite open courts remain open; this is not an H plan or a closed courtyard.
add(27,-23,2.8,82,22,64.2)
add(-37,23,2.8,62,22,64.2)
add(-4,0,2.8,26,68,64.2)
# Eight source-visible window rows. Four/six major room-bay groups on the short/long wing.
# Recessed narrow lights and separate deeper broad balcony bays retain the main hierarchy.
wingdata=[(-66,-17.1,23,4), (9.1,66,-23,6)]
for lo,hi,cy,n in wingdata:
 pitch=(hi-lo)/n
 for face in [-1,1]:
  y=cy+face*11
  for k in range(n):
   a=lo+k*pitch;b=a+pitch
   add(a+.10,y+face*.25,3,1.1,1.1,64.0)
   for floor in range(8):
    z=4.1+floor*7.5
    if cy==-23 and face==-1:
     # B view, long-wing OUTER face: broad white panels, ONE angular projecting
     # window plus ONE separated small slit per main bay. This face is NOT the A grid.
     bal=a+pitch*.40
     if floor>0:
      parts.append(poly([(bal-1.85,y-face*.40),(bal+1.85,y-face*.40),(bal+1.25,y+face*1.7),(bal-.8,y+face*1.1)],z,5.4))
     cut(bal,y+face*.35,z+.95,2.0,3.0,3.6)
     cut(a+pitch*.82,y,z+1.6,.70,2.7,2.8)
    else:
     # A short-wing outer + long-wing inner and B short-wing inner faces:
     # FOUR narrow lights between TWO wider recessed balcony/window strips.
     for bal in [a+1.02,b-1.02]:
      cut(bal,y+face*.05,z,1.15,3.4,5.5)
      if floor>0:details.append(poly([(bal-1.05,y-face*.35),(bal+1.05,y-face*.35),(bal+.9,y+face*1.30)],z,1.25))
     for j in range(4):
      x=a+2.65+j*(pitch-5.30)/3
      cut(x,y,z+.9,.50,2.7,4.35)
  add(hi-.2,y+face*.25,3,1.2,1.1,64)
 # Solid roof terrace slab, high outer frame with genuine open rectangular gaps.
 add((lo+hi)/2,cy,66.8,hi-lo+2.6,23.2,1.3)
 for face in [-1,1]:
  y=cy+face*11.05
  add((lo+hi)/2,y,74.0,hi-lo+2.6,1.4,1.65)
  for k in range(n+1):add(lo+k*pitch,y,67.8,1.6,1.55,6.5)
 # End frames and roof-edge low rails; roof remains flat/open, not another occupied floor.
 for x in [lo-.6,hi+.6]:
  add(x,cy,67.8,1.6,23.2,7.8)
 for face in [-1,1]:add((lo+hi)/2,cy+face*11.0,68.0,hi-lo,1.05,1.25)
# Central common-room core: wide walls, stacked corner balconies and offset two-storey glazing.
# The two opposite elevations are separately laid out, not copies of a uniform grid.
for face in [-1,1]:
 x=-4+face*13
 # balcony column, separated by thick white floor slabs and a tall corner pier.
 by=27*face
 for floor in range(8):
  z=4+floor*7.5
  cut(x,by,z+1.1,4.6,6.6,5.1)
  add(x+face*.7,by,z+.7,3.0,7.5,1.1)
  # backed balcony parapet, avoiding fragile freestanding rail rods.
  add(x+face*1.8,by,z+1.6,1.15,7.1,1.3)
 # Paired room windows beside the balconies.
 for floor in range(8):
  z=4.5+floor*7.5
  for y,w in [(by-face*7.5,3.2),(by-face*11.2,1.45)]:cut(x,y,z+1.0,2.8,w,3.5)
 # Larger double-height common-room glass, staggered and visibly different from room windows.
 for y,z,h in [(4*face,22,11.4),(4*face,43.5,11.4),(-7*face,14.5,11.0),(-7*face,36,11.0)]:
  cut(x,y,z,3.0,5.2,h)
  # Thick simplified glass crossbars connected to the solid recess backing.
  details.append(box(x-face*.85,y,z+h/2,2.0,5.4,1.0))
  details.append(box(x-face*.85,y,z,2.0,.95,h))
 for y,z in [(4*face,9),(4*face,59),(-7*face,57.5)]:cut(x,y,z,3.0,2.3,2.5)
 # Roof-height opening and coarse edge frame along the visible central core.
 add(x,0,66.8,1.65,67,1.3)
 add(x,0,73.95,1.85,67,1.70)
 for y in [-33,-20,-7,7,20,33]:add(x,y,67.95,1.55,1.7,6.25)
# Central roof is a separate lower service terrace, not same-height solid continuation.
add(-4,0,66.7,25.8,67,1.3)
# Outer end of the core meets the wing facade: stair lights, not a blank wall.
for side in [-1,1]:
 for z in [5.2+7.5*i for i in range(8)]:
  for x in [-12,2]:cut(x,side*34,z,2.5,3.0,3.9)
 add(-4,side*34,68.0,26,1.6,7.65)
# Short wing outer end: two continuous staircase glass ribbons in a broad white end wall.
# Opposite long-wing outer end is also seen as a glazed staircase; exact mullions simplified.
for x,cy,side in [(-68,23,-1),(68,-23,1)]:
 for y in [cy-5,cy+5]:
  cut(x,y,9,3.0,3.5,51)
  for z in np.arange(13,60,5.7):details.append(box(x-side*.80,y,float(z),.9,3.7,1.0))
 cut(x,cy,3.3,3.1,5.0,5.0)
 # Broad upper white parapet below the open end frame.
 add(x,cy,66.7,1.6,23.5,8.95)
# Angular red-ribbon entrance canopy. Printed in one material, stepped plan profile preserved.
# No unsupported paint-only surfaces; canopy and thickened triangular hangers are real geometry.
canopies=[[(9,-12),(44,-12),(44,-6),(30,-7),(20,-5),(9,0)], [(-17,12),(-43,12),(-43,6),(-31,5),(-24,7),(-17,0)]]
canopies += [[(8.5,-12),(15,-12),(14,4),(16,12),(13,26),(8.5,26)], [(-16.5,12),(-23,12),(-22,-4),(-24,-12),(-21,-26),(-16.5,-26)]]
for p in canopies:parts.append(poly(p,11.0,1.6))
for side in [-1,1]:
 cx=9 if side==1 else -17
 for y in [-5*side,9*side,23*side]:
  parts.append(rod((cx-side*.4,y,18),(cx+side*5,y,12),.68))
  cut(cx,y,3.3,3.0,5.8,6.2)
for x,ysign in [(15,1),(26,1),(38,1),(-22,-1),(-31,-1),(-39,-1)]:
 cy=-12 if ysign==1 else 12
 parts.append(rod((x,cy-.4*ysign,18),(x,cy+5*ysign,12),.68))
 # lower entrance door group, partly tree-covered in sources, reduced to attached recesses.
 cut(x,cy,3.3,4.0,3.0,6.2)
# Core ground entrance facing each open court.
for side in [-1,1]:cut(-4+side*13,-side*12,3.3,3.2,7.5,6.3)
solid=Manifold.batch_boolean(parts,0)-Manifold.batch_boolean(cuts,0)
solid=solid+Manifold.batch_boolean(details,0)
# Orient the plan to the official Z footprint; north/south naming is not surveyed.
solid=solid.scale((1,-1,1))
assert solid.status().name=='NoError',solid.status()
assert len(solid.decompose())==1,[(p.volume(),p.bounding_box()) for p in solid.decompose()]
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('dimensions_mm',mesh.extents,'volume_mm3',mesh.volume,'triangles',len(mesh.faces),'watertight',mesh.is_watertight)
