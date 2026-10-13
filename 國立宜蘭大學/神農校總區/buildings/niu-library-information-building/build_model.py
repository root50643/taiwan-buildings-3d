"""NIU library / information building. Original approximate exterior in millimetres.
Main facade: left 4 louvred window rows vs right 3 + 8 tall slits; roof 4 openings
on right only. Do not substitute seven regular rows from a floor-count label.
Footprint follows official 2F / 6F plans: angled left flank and narrow rear wing.
"""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];late=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def prism(pts,z,h):return CrossSection([pts]).extrude(h).translate((0,0,z))
add(0,0,0,109,150,3)
foot=[(-48,-52),(48,-52),(48,67),(0,67),(0,8),(-20,8)]
parts.append(prism(foot,2.8,75.2))
# Large two-storey entrance undercroft, clearly visible on both facade and side.
cut(27,-46,3.0,40,16,21.0)
# Four facade piers delimit three openings; middle is occupied by ascending stairs.
for x in [7,15,35,47]:add(x,-51,2.9,3.0,3.1,21.5)
# Recessed glazed wall at back of portico, without pretending it is open through body.
for x in [12,24,39]:cut(x,-37,5,9,3.2,14)
# Broad entrance stair, with flared lower flight and a landing.
for k in range(20):
 w=24-5.0*min(k/9,1);add(25,-72+k*1.35,2.9,w,1.6,(k+1)*.60)
# Stout stepped parapets join stairs; no free thin metal handrails modelled.
for k in range(20):
 w=24-5.0*min(k/9,1)
 for s in [-1,1]:add(25+s*(w/2+.6),-72+k*1.35,2.9,2.0,1.85,(k+1)*.60+2.0)
# Lower left facade has four wide glazing doors and shallow entrance canopy.
for x in [-32,-24,-16,-8]:
 cut(x,-52,5,6.0,3.5,7.2);cut(x,-52,15,6.0,3.5,8.1)
add(-20,-54,12.5,40,6.0,1.8)
for k in range(4):add(-20,-58+k*1.4,2.9,44,1.6,.55*(k+1))
# Four left groups, separator slit, four right groups. Wings intentionally unequal.
for x in [-32,-24,-16,-8]:
 for z in [26,37,48,59]:cut(x,-52,z,6.4,3.6,8.2)
for x in [9,19,29,39]:
 for z in [37,48,59]:cut(x,-52,z,7.1,3.6,8.2)
for z in [29,40,51,62]:cut(0,-52,z,5.8,3.6,1.7)
# Frame blades and shelf are simplified into stout connected reliefs.
for x in [-32,-24,-16,-8,9,19,29,39]:
 for z in ([26,37,48,59] if x<0 else [37,48,59]):
  for dx in [-2.6,2.6]:late.append(box(x+dx,-52,z-.2,1.1,4.2,8.6))
  late.append(box(x,-52.3,z+5.7,7.7,4.1,1.2))
# Eight narrow vertical windows below the right's three grille rows.
for x in [5,11,15,21.2,25,32,36,43]:cut(x,-52,26,1.9,3.6,8.5)
# Uppermost roof band: only four windows on right; left is plain wall in source.
for x in [9,19,29,39]:cut(x,-52,70,5.5,3.6,5.4)
# Right long face has seven paired bays, not a generic full-window grid.
centres=[-38,-22,-6,10,26,42,58]
for i,y in enumerate(centres):
 for dy in [-3.3,3.3]:
  yy=y+dy
  cut(48,yy,70,3.6,4.4,5.4)
  for z in [37,48,59]:
   if i==3:continue # central continuous glass strip through three main rows
   cut(48,yy,z,3.6,4.7,8.2)
   late.append(box(48,yy,z+5.7,4.0,5.8,1.15))
  if i<3:cut(48,yy,26,3.6,2.0,8.5)
  elif i!=3:cut(48,yy,26,3.6,4.7,8.2)
  if i>1:
   for z in [5,15]:cut(48,yy,z,3.6,4.6,7.2)
# Recessed continuous central glass strip, not divided into artificial square holes.
cut(48,10,26,3.8,5.2,41.1)
for z in np.arange(27.5,66,5):late.append(box(48,10,z,4.0,5.4,1.1))
# Side portico extends two bays from the entrance and retains two large open voids.
cut(45,-29,3,8,30,11)
for y in [-44,-29,-14]:add(47,y,2.9,3.1,3.0,12)
add(46,-29,12.5,4,33,2)
# Rear end and the recessed return: positions approximated from current floor plans.
for x in [7,18,29,40]:
 for z in [6,17,28,39,50,61,70]:cut(x,67,z,6.5,3.6,5.4)
for y in [17,31,45,59]:
 for z in [6,17,28,39,50,61,70]:cut(0,y,z,3.6,8.5,5.4)
# Oblique flank follows the real trapezoid, not a boxed-out rectangular substitute.
a=np.array([-48.,-52.]);b=np.array([-20.,8.]);v=b-a;L=np.linalg.norm(v);angle=np.degrees(np.arctan2(v[1],v[0]))
for t in [.16,.36,.56,.76,.92]:
 c=a+t*v
 for z in [6,17,28,39,50,61,70]:
  cuts.append(box(0,0,z,7.5,3.6,5.4).rotate((0,0,angle)).translate((float(c[0]),float(c[1]),0)))
# Parapet / service core is deliberately modest: roof equipment not fully surveyed.
outer=prism(foot,77.6,2.0)
inner=CrossSection([foot]).offset(-1.7).extrude(3).translate((0,0,77.5))
parts.append(outer-inner)
add(24,48,77.7,15,21,4.4)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in late:solid=solid+p
print([(p.volume(),p.bounding_box()) for p in solid.decompose()]);assert len(solid.decompose())==1
m=solid.simplify(1e-5).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj');print(mesh.extents,len(mesh.faces),mesh.is_watertight)
