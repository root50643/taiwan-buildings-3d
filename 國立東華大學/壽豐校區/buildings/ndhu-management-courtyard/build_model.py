"""國立東華大學管理學院，2017–2021公開實拍外觀參考模型。
All coordinates are miniature mm, +Y north, -Y south/front, +X east.
Handmade CSG from official floor plans and public photographs. No external mesh.
North exterior facade is insufficiently photographed and deliberately simplified.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
P={'base_w':150.,'base_d':150.,'base_h':2.5,'south_y':-55.,'north_y':54.,'west_x':-55.,'east_x':55.,'floor_h':8.1,'wing_top':37.9,'roof_rise':4.2,'min_pier':1.8}
parts=[];cuts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cyl(x,y,z,r,h):return Manifold.cylinder(h,r,r,64).translate((x,y,z))
def poly(points,z,h):return CrossSection([points]).extrude(h).translate((0,0,z))
def gable(x,y,z,w,d,h,angle=0,skylights=False):
 # Solid gable with 1.4mm flattened ridge avoids fragile knife edge.
 section=CrossSection([[(-d/2,0),(d/2,0),(d/2,1.1),(.7,h),(-.7,h),(-d/2,1.1)]])
 roof=section.extrude(w).rotate((90,0,90)).translate((-w/2,0,z)).rotate((0,0,angle)).translate((x,y,0))
 parts.append(roof)
 if skylights:
  # Distinct open skylight pockets along court-facing slope. Keep floor of roof intact.
  for xx in np.arange(-w/2+6,w/2-4,5.8):
   c=box(xx,-d*.10,z+1.7,4,5.3,h+1).rotate((0,0,angle)).translate((x,y,0));cuts.append(c)
# Flat integrated base; body is about 133x129mm.
add(0,0,0,P['base_w'],P['base_d'],P['base_h'])
# North wing: four storeys and several courtward office projections, not a filled court.
add(0,54,2.4,120,18,35.5)
gable(0,54,37.7,112,20,4.2,skylights=True)
# North courtyard corridor relief, vertically separated by thick floor slabs.
for z in [4.2,12.3,20.4,28.5]:
 for x in [-42,-14,14,42]:cuts.append(box(x,44.9,z,21,3.5,5.8))
for x in [-43,-12,20,44]:
 add(x,42.7,11.5,12,5.5,18)
 for z in [13.2,21.3]:
  for dx in [-3.7,1.8]:cuts.append(box(x+dx,39.9,z,3.6,1.5,5.1))
# Northern corner service towers: one taller than the other, as in 2021 aerial.
for x,h in [(-61,40),(61,47)]:
 add(x,54,2.4,12,19,(40.8 if x>0 else h)-2.4)
 add(x,54,h,14,20,1.4)
 # Upper ventilator on northeastern tower with printable wall-backed reveal.
 if x>0:
  add(x,54,40.8,11,13,6.2)
  for yy in [47.4,60.6]:cuts.append(box(x,yy,44.3,7,1.5,2.1))
  for xx in [55.4,66.6]:cuts.append(box(xx,54,44.3,1.5,8,2.1))
 # A vertical stair glazing recess, no fabricated north window array.
 cuts.append(box(x+(6 if x>0 else -6),54,7,1.7,5,25))
# East wing: continuous long face with deep, grouped window bays.
add(55,-1,2.4,18,92,35.5)
gable(55,-1,37.7,82,20,4.2,90)
for z in [5.1,13.2,21.3,29.4]:
 for y in np.arange(-38,40,7.8):
  cuts.append(box(64,y,z,2.0,5.6,6.1))
  cuts.append(box(46,y,z,2.2,5.6,6.1))
# Ground-floor interior colonnade. Behind it the wing stays solid.
for y in np.arange(-37,39,13):cuts.append(box(46.5,y,2.5,6.4,10.2,6.0))
# West wing deliberately broken by open bridge connections at both ends.
add(-55,0,2.4,20,57,35.5)
gable(-55,0,37.7,59,22,4.2,90,True)
for z in [5.1,13.2,21.3,29.4]:
 for y in np.arange(-24,27,7.8):
  cuts.append(box(-65,y,z,1.9,5.6,6.1))
  if z>12 or abs(y)>21:cuts.append(box(-45,y,z,2.3,5.6,6.1))
# Four-storey open bridges, with robust columns and low integrated parapets.
for y in [-38,38]:
 for x in [-59,-51]:add(x,y,2.4,2.1,20,34.5)
 for z in [10.2,18.3,26.4,34.5]:
  add(-55,y,z,12,21,1.7)
  add(-61,y,z+1.5,1.5,21,1.5)
  add(-49,y,z+1.5,1.5,21,1.5)
# Southern facade: three separate gable blocks with lower glazed connections.
for x,w,d,h in [(-35,32,20,34.1),(0,18,24,34.1),(35,32,20,34.1)]:
 add(x,-55,2.4,w,d,h-2.4);gable(x,-55,h-.2,w+1.8,d+1.8,4.2)
 for z in [5.1,13.2,21.3]:
  for xx in np.arange(x-w/2+4,x+w/2-2,6.1):
   cuts.append(box(xx,-55-d/2,z,4.3,1.8,6.1))
   cuts.append(box(xx,-55+d/2,z,4.3,1.8,6.1))
 # Attic/light band represented as a continuous inset, plus robust vertical separators.
 for yy in [-55-d/2,-55+d/2]:
  cuts.append(box(x,yy,30, w-4,1.7,2.1))
for x,w in [(-16,8),(16,8),(-55,10),(55,10)]:
 add(x,-55,2.4,w,12,27.8)
 for z in [5.1,13.2,21.3]:
  cuts.append(box(x,-61,z,w-1.6,1.7,6.1));cuts.append(box(x,-49,z,w-1.6,1.7,6.1))
# Southern central entry: recessed clear-through ground passage.
cuts.append(box(0,-55,2.5,11,30,6.8))
# Two round corner staircase towers. Flattened glazing sectors + horizontal balcony bands.
for x in [-61,61]:
 parts.append(cyl(x,-54,2.4,8,39.8));parts.append(cyl(x,-54,41,8.8,1.5))
 # Four levels of broad recessed glazing bays on the exposed southern half.
 for z in [5.0,13.1,21.2,29.3]:
  for ang in [-110,-70]:
   # tangent cuts are shallow, do not leave isolated thin mullions
   rad=np.deg2rad(ang);xx=x+7.5*np.cos(rad);yy=-54+7.5*np.sin(rad)
   cuts.append(box(0,0,z,3.6,2.1,6.0).rotate((0,0,ang+90)).translate((xx,yy,0)))
  parts.append(cyl(x,-54,z-1.3,8.5,1.2))
# Inward semicircular lecture-room volumes and terraces from official plan.
# A full cylinder is clipped at the attachment line before union, eliminating unknown back halves.
for x,side in [(-45,1),(45,-1)]:
 disc=cyl(x,0,2.4,19,9.5)^box(x+side*10,0,2.3,20.4,40,12)
 parts.append(disc)
 deck=cyl(x,0,11.6,20,1.8)^box(x+side*10,0,11.5,20.4,42,2.2);parts.append(deck)
 rim=(cyl(x,0,13.1,20,1.6)-cyl(x,0,13,18.6,2))^box(x+side*10,0,13,20.4,42,2)
 parts.append(rim)
 # wide doorway at each semicircular frontage
 cuts.append(box(x+side*18.6,0,2.5,3.6,7,6.2))
# Northern circular exterior stair landing extends into the courtyard; supported stair treads.
parts.append(cyl(0,40,2.4,11,1.2))
for i in range(8):add(0,31+i*1.3,2.4,8,1.5,(i+1)*1.1)
add(0,41,10.5,11,5,1.6)
# East exterior canopy, stepped in plan to match the long approach seen in aerials.
for x,y,w,d in [(70,20,6,50),(66,-2,14,6)]:
 add(x,y,9.2,w,d,1.4)
for y in [-4,14,36]:add(71,y,2.4,2,2,7.2)
# Courtyard remains open; a low path hints at the circular garden without delicate landscaping.
# No trees, tiny balustrade wires, rooftop antennae, or measured masonry texture are invented.
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
assert len(solid.decompose())==1, [(x.volume(),x.bounding_box()) for x in solid.decompose()]
m=solid.simplify(0.001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight,len(mesh.faces))
