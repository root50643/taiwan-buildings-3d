"""雲旭樓主樓段；自建毫米外觀模型，不是古蹟群全區或測繪成果。
官方2024年1/3F平面與2023修復後實拍：三層主楼、五開間折版屋頂、
正面外廊、兩端樓梯。斜接連廊/工場/電梯另列未建模，背窗細節估計。
"""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile(poly,y,d):return CrossSection([poly]).extrude(d).rotate((90,0,0)).translate((0,y+d/2,0))
add(0,0,0,150,72,3)
# The five 450 cm structural bays and two end stair bays in the published plan.
add(0,4.5,2.8,105,35,47.6)
# Open ground-floor center passage, not a painted dark recess.
cut(0,4.5,2.9,18,36,14.4)
# Three broad cantilevered front corridors, stairs and deep balcony voids.
for z in [3.0,18.8,34.6]:add(0,-3.0,z,136,49,1.6)
add(0,-2.0,50.4,136,52,1.6) # continuous backing under all five roof fold valleys
for x in [-66,-52.5,-31.5,-10.5,10.5,31.5,52.5,66]:
 add(x,-25.4,3.1,2.2,2.5,48.3)
 # Exposed transverse concrete beams under each corridor slab.
 for z in [17.0,32.8,48.6]:add(x,-18.7,z,2.1,15.7,2.4)
# Structural rear/end columns frame the stair openings.
for x in [-66,-52.5,52.5,66]:
 add(x,19.8,3,2.2,2.2,48)
for x in [-67,67]:
 for z in [18.8,34.6]:add(x,-2.5,z+1.1,1.6,45,4.8)
# First-floor facade partial raised panels flank a center doorway.
for x in [-42,-21,21,42]:add(x,-26,3,15.8,1.6,3.6)
# Second-floor steel guardrails thickened to 1.2 mm; upper floor solid parapet.
add(0,-26.0,20.3,134,1.8,1.4)
add(0,-26.0,25.6,134,1.8,1.4)
for x in np.arange(-64,65,5.2):add(float(x),-26.0,21.2,1.2,1.6,5.2)
add(0,-26.0,36.0,134,1.8,5.4)
add(0,-26.3,40.5,136,2.1,1.5)
# Original name panel is represented by blank relief; no invented lettering.
add(0,-27.0,37.0,23,1.0,3.4)
# Major facade windows are individually recessed with sturdy backed mullions.
for y in [-13,22.0]:
 s=1 if y<0 else -1
 for floor,z in enumerate([7.2,23.2,39.0]):
  for x in [-42,-21,0,21,42]:
   if floor==0 and x==0:continue
   cut(x,y,z,17.7,2.5,9.6)
   for dx in [-5.8,0,5.8]:details.append(box(x+dx,y+s*.7,z,1.2,1.5,9.6))
   for zz in [z+3.0,z+6.2]:details.append(box(x,y+s*.7,zz,17.7,1.5,1.0))
   add(x,y,z-.9,19,1.8,1.0)
# Back columns/headers follow actual bay rhythm rather than a generic grid.
for x in [-52.5,-31.5,-10.5,10.5,31.5,52.5]:add(x,22.0,3,2.2,1.5,47.6)
for z in [17.5,33.3]:add(0,22.0,z,106.5,1.7,1.5)
# Two end open dog-leg staircases, grounded and tied to floor landings.
for x in [-59.4,59.4]:
 for z in [4.5,20.3,36.1]:
  # Stair flight rises toward the rear; opposing return flight to next floor.
  for i in range(10):
   add(x-3.0,-9.0+i*2.4,z,5.8,2.6,(i+1)*.7)
   add(x+3.0,12.6-i*2.4,z+7.0,5.8,2.6,(i+1)*.7)
  add(x,13.2,z+6.4,13.1,5.0,1.2)
 # Rear window-free end pier simplified from public plan.
 add(x,21.0,3.0,14.1,3.0,48.7)
# Folded-plate roof: five ridges spanning the five central bays. Lower slab
# remains continuous, so sharp peaks are attached to an ample solid substrate.
for x in [-42,-21,0,21,42]:
 parts.append(profile([(x-10.5,51.6),(x+10.5,51.6),(x,55.4)],4.5,37.5))
 # Stout rim follows the visible rear triangle, no detached thin edge.
 parts.append(profile([(x-10.6,51.4),(x+10.6,51.4),(x,55.6)],23.0,1.5))
# End stair canopy tops read as flat end wings. Adjacent new elevator excluded.
for x in [-60.4,60.4]:add(x,-2.3,51.4,15.2,49.5,1.4)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print([(s.volume(),s.bounding_box()) for s in solid.decompose()]);assert len(solid.decompose())==1,'Disconnected geometry'
m=solid.simplify(1e-5).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
