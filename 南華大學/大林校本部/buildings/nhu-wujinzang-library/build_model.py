"""南華無盡藏外觀比例近似，非測繪。
Coordinates before uniform 1.5 miniaturisation are OSM-derived nominal working units,
not certified metres. Main west facade is -Y; north is -X. Level heights come from
photo band proportions (ground hall taller), not assumed 3m storeys.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def detail(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile(points,y,depth):return CrossSection([points]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def gable(x,y,z,w,d,h,flat=1.2):parts.append(profile([(x-w/2,z),(x+w/2,z),(x+flat/2,z+h),(x-flat/2,z+h)],y,d))
def hip(x,y,z,w,d,h,top=(.7,.16)):
 parts.append(CrossSection.square((w,d),center=True).extrude(h,scale_top=top).translate((x,y,z)))
def poly(points,z,h):parts.append(CrossSection([points]).extrude(h).translate((0,0,z)))
# Common base; full building is L-shaped, not a vertically extruded OSM outline.
add(-17,-2,0,100,94,1.8)
# Five-storey main block. B1 is documented but not a separate fictitious exposed floor.
add(0,0,1.6,45,58,25.4)
# Northern two-storey wing with open third-floor roof platform, absent at 4F/5F.
add(-42.2,-19.25,1.6,39.6,19.5,10.5)
add(-42.2,-19.25,11.8,40.2,20.1,1.0)
# Low open parapet around the platform; finite 1.0 working-unit width.
for x in [-62,-22.4]:add(x,-19.25,12.5,1.0,20,1.1)
for y in [-29,-9.5]:add(-42.2,y,12.5,40.6,1.0,1.1)
# Rear/east projection: 1F/2F rounded end, upper portion squared and stepped back.
poly([(-13,27),(13,27),(13,38),(9,38),(9,40),(6,42),(0,43),(-6,42),(-9,40),(-9,38),(-13,38)],1.6,11.5)
add(0,33,12.8,26,12,9.4)
# Fifth-floor rear terrace, with end roof caps and a lower central service block.
add(0,33,22,26,12,1.0)
for x in [-12.5,12.5]:add(x,33,22.7,1.0,12,1.2)
add(0,38.5,22.7,26,1.0,1.2)
for x in [-10,10]:
 add(x,34,22.8,5.8,8.8,.8)
 hip(x,34,23.4,6,9,1.5,top=(.35,.2))
add(0,31,23,4.0,5,2.2)
# Four thicker corner blocks and eave caps.
for x in [-18.5,18.5]:
 for y in [-25,25]:
  add(x,y,1.6,8,8,26.1)
  add(x,y,27.3,8.8,8.8,1.1)
# Rear taller pale service crown, one end only (aerial), not a mirrored pair.
add(18.5,25,28.1,8.0,7.4,4.0)
add(18.5,25,31.8,8.8,8.2,.9)
# Narrow red pitched side roofs, dark-flat walkways left open between them and cover.
for x in [-19.5,19.5]:
 add(x,0,26.8,5.4,43,1.2)
 gable(x,0,27.8,5.3,43,1.8,flat=1.0)
# Major central pale metal cover, shallow cambered faceting, closed not open courtyard.
add(0,2,26.7,25,44,3.5)
cover_pts=[(-12.5,29.7),(12.5,29.7),(12.5,30.8),(7,31.5),(1,31.8),(-1,31.8),(-7,31.5),(-12.5,30.8)]
parts.append(profile(cover_pts,2,44))
# Nine transverse shallow structural ribs; finite backed relief, no free hairline wires.
for y in np.linspace(-19.5,23.5,9):
 pts=[(x,z+.28) for x,z in cover_pts]
 parts.append(profile(pts,float(y),.8))
# Front raised roof/clerestory: long centre opening and two flanking short openings.
add(0,-25.2,26.5,28,7.6,1.8)
hip(0,-25.2,28.1,23.5,8.2,2.4,top=(.92,.17))
for x in [-12.1,12.1]:add(x,-25.2,28.0,1.2,8.5,2.7)
# Deep front recesses: two flanking continuous balcony wells, 3 rows of 3 centre windows.
for x in [-11.5,11.5]:
 for z in [9.0,14.0,19.0]:
  cut(x,-29,z,4.8,4.8,3.4)
  detail(x,-27.3,z,4.8,2.2,.85)
for x in [-5.3,0,5.3]:
 for z in [9.0,14.0,19.0]:cut(x,-29,z,3.3,2.2,3.2)
# Top row is larger open clerestory, not another grid of square windows.
cut(0,-29,24.4,17.0,4.8,2.8)

for x in [-11.5,11.5]:cut(x,-29,24.4,3.8,4.8,2.8)
# Solid end-block facade: two upper window rows and tall lower slit treatment.
for side in [-1,1]:
 for xx in [16.3,20.3]:
  x=side*xx
  for z in [18,22.8]:cut(x,-29,z,1.7,1.8,1.8)
  cut(x,-29,5.0,.8,1.8,8.3)
# Official north-side oblique: nine bays x THREE tall visible window rows.
# The five-floor building record does not imply five window rows here.
for side in [-1,1]:
 for y in np.linspace(-18,18,9):
  for z in [10.5,15.7,20.9]:
   if side<0 and y<-8 and z<13:continue
   cut(side*22.5,float(y),z,2.0,2.8,4.2)
   # Window guard band recessed behind the outer wall, rooted into back wall.
   if z>13:detail(side*21.6,float(y),z+.85,1.2,2.8,.65)
# Visible west wall of the north low wing: broad upper window band grouping, sparse lower.
for x in [-57,-51,-45,-39,-33,-27]:
 cut(x,-29,8.0,4.1,1.8,2.1)
# No invented repetitive rear/east window elevation.
# Entry: broad glazed recess, two thick door-canopy piers, modest hipped red canopy.
cut(0,-29,2.7,11.5,2.4,4.5)
for x in [-4,-2,0,2,4]:detail(x,-28.1,2.8,.6,3.2,4.3)
for z in [4.6,6.5]:detail(0,-28.1,z,11.5,3.2,.7)
for x in [-7,7]:add(x,-33,1.6,2.2,6.0,5.8)
add(0,-32,6.9,16,8,1.0)
hip(0,-32,7.6,14,7.3,1.2,top=(.92,.18))
for x in [-7.2,7.2]:add(x,-32,7.5,1.0,7.7,1.5)
# Lower entrance side canopies span left/right of the doorway, as photographed.
for side in [-1,1]:
 add(side*11.5,-31,6.9,9.0,5.8,1.0)
 add(side*15,-32,2.6,1.7,4,4.7)
 add(side*15,-31,7.6,1.1,5.8,1.1)
# Orange/pale forward north roof box seen in the aerial, lower than rear crown.
add(-18.5,-24,28.1,7.4,6.0,1.9)
# Front platform, steps and short attached side corridors; no distant avenue model.
add(0,-36,1.6,60,18,1.2)
for i in range(4):add(0,-46.3+i*1.2,1.6,30,1.6,.3*(i+1))
for side in [-1,1]:
 x=side*27
 for y in [-29,-35,-41]:add(x,y,2.6,1.5,1.5,2.8)
 add(x,-35,5.0,2.2,14.0,1.0)
 # Two glass-pyramid pavilions are attached foreground structures, not separate buildings.
 for dx in [-2.5,2.5]:
  for dy in [-2.5,2.5]:add(x+dx,-41+dy,2.5,1.5,1.5,3.0)
 add(x,-41,5.2,7.0,7.0,1.0)
 hip(x,-41,6.0,7.0,7.0,1.6,top=(.18,.18))
solid=parts[0]
for p in parts[1:]:solid+=p
for c in cuts:solid-=c
for p in details:solid+=p
assert len(solid.decompose())==1
solid=solid.translate((17,2,0)).scale((1.5,1.5,1.5))
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
