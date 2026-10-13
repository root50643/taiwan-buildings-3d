"""Original NCUT Luming Grandstand exterior study. Units mm; longest edge 150 mm.
After-construction views and campus plan, not a measured survey. See sources.json.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, OpType
OUT=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def yz_profile(points,x,width):return CrossSection([points]).extrude(width).rotate((90,0,90)).translate((x-width/2,0,0))
def half_disc(x,y,z,r,h):
 pts=[(x-r,y),(x+r,y)]+[(x+r*math.cos(t),y+r*math.sin(t)) for t in np.linspace(0,math.pi,49)[1:]]
 return CrossSection([pts]).extrude(h).translate((0,0,z))
add(0,0,0,150,53,3)
# Exposed lower block plus the rear structural wall. No sealed interior cavity is introduced.
add(0,0,2.8,138,18,11.8)
add(0,7.1,14.3,138,3.8,11.5)
# Covered spectator terrace and front cantilever walkway.
add(0,-10.3,13.3,140,7.4,1.7)
# Four seating zones and a broad central dais. Six bench rises are source-visible.
for lo,hi in [(-68,-31),(-23,-12),(12,23),(31,68)]:
 for i in range(6):add((lo+hi)/2,-5.5+i*1.7,14.4,hi-lo,2.0,1.0+i*1.05)
# Central dais remains open, not a filled box or a continuation of the seating rows.
add(0,-1.5,14.4,23,15,1.1)
# Broad wall piers beside stair access openings and slimmer central posts.
for x in [-69,-29,29,69]:add(x,0,14.3,2.3,18,12.2)
for x in [-23.6,-11.3,11.3,23.6]:add(x,-1.1,14.3,1.3,14,12.2)
# End stair bays linking the levels, seen in the side edges of the official aerial views.
for side in [-1,1]:
 for i in range(9):add(side*70.7,-8+i*1.8,2.8,3.0,2.0,1.15+i*1.16)
# Slightly pitched roof: 15 actual panel bays, bounded by 16 longitudinal ribs.
# Six broad bays on each side, two narrow bays flanking the larger central panel.
roof=[(-13,25.6),(11.5,26.9),(11.5,28.3),(-13,27.0)]
parts.append(yz_profile(roof,0,142))
rib_x=[-70.4,-61.2,-52.0,-42.8,-33.6,-24.4,-15.2,-10.4,10.4,15.2,24.4,33.6,42.8,52.0,61.2,70.4]
for x in rib_x:parts.append(yz_profile([(-13,26.7),(11.5,28.0),(11.5,31.3),(-13,27.9)],x,1.25))
# Thickened continuous front railing; individual hairline bars omitted at this scale.
add(0,-14.1,14.9,141,1.15,1.3)
# Original lower facade has long grouped glazing, separated by wide door/stair gaps.
for lo,hi in [(-68,-32),(-22.0,-6),(6,22.0),(32,68)]:
 width=hi-lo;cut((lo+hi)/2,-9.0,7.0,width,2.8,4.0)
 for x in np.arange(lo+4,hi,5):add(x,-9,6.9,1.1,2.9,4.2)
# Deep ground-level circulation openings in centre and beside the two access towers.
for x,w in [(0,12),(-27,6),(27,6)]:cut(x,-3.5,2.9,w,26,5.1)
# Track-side low retaining walls with the same four interruptions.
for lo,hi in [(-69,-30),(-21,-6),(6,21),(30,69)]:add((lo+hi)/2,-17,2.8,hi-lo,2.0,4.8)
# Rear elevation: twelve repeated semicircular balcony bays, two visible levels.
# Trees obscure portions of the lower row; their repeated positions are inferred from the upper row.
centers=[-64.9,-55.7,-46.5,-37.3,-28.1,-18.9,18.9,28.1,37.3,46.5,55.7,64.9]
for x in centers:
 for z in [6.8,17.2]:
  parts.append(half_disc(x,8.65,z,4.0,1.25))
  outer=half_disc(x,8.65,z+1.1,4,2.5)
  inner=half_disc(x,8.65,z+1.0,2.65,3.0)
  parts.append(outer-inner)
  cut(x,9.0,z+3.95,5.0,2.7,4.8)
 # Broad pilaster edges, visually different from the railings.
for x in [-69.5,-60.3,-51.1,-41.9,-32.7,-23.5,-14.3,14.3,23.5,32.7,41.9,51.1,60.3,69.5]:add(x,9.3,2.8,1.3,2.3,24.3)
# Rear middle arrival porch: tall central glazing and a low deep entrance below.
add(0,9.5,10.5,24,4,1.6)
for x in [-11.2,11.2]:add(x,9.5,3,1.5,4,23.8)
cut(0,9.0,16.0,18,3.0,7)
for x in [-6,-2,2,6]:add(x,9.1,15.9,1.1,3.1,7.2)
add(0,12.8,11.1,23,5,1.5)
for i in range(4):add(0,18.6-i*1.3,2.8,17,1.8,.7+i*.8)
# Glazed openings on the short ends, source partially visible; no invented service annex.
for side in [-1,1]:
 for y in [-4,3]:cut(side*69,y,7,3.0,3.8,4.3)
# Photo-derived width/height proportion; preserve the 3 mm base independently.
# Long span and low stand: 0.72 vertical proportion relative to the drafting dimensions.
# This is a documented approximate scale, not a measured full-size height.
base=parts[0]
above=Manifold.batch_boolean(parts[1:],OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
above=above.translate((0,0,-3)).scale((1,1,.72)).translate((0,0,3))
solid=base+above
assert solid.status().name=='NoError',solid.status()
assert len(solid.decompose())==1,[(x.volume(),x.bounding_box()) for x in solid.decompose()]
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('dimensions_mm',mesh.extents,'volume_mm3',mesh.volume,'triangles',len(mesh.faces),'watertight',mesh.is_watertight)
