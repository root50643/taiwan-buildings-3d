"""Original approximate exterior of NTUT Everlight Building, from public photos.
mm. Front = long balcony elevation on Zhongxiao East Road. Roof depth/returns
are photo estimates; no surveyed interior, mesh, texture or CAD is imported.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
# Base and three-storey podium. The tower is a single building, not three models.
add(0,0,0,150,94,3)
add(0,0,2.8,126,74,31.0)
# Ground-floor glazing recesses with backed, deliberately thickened mullions.
for y in [-37,37]:
 for x in np.arange(-56,60,8):cut(float(x),y,4.4,6.7,3.2,8.1)
for x in [-63,63]:
 for y in np.arange(-29,34,9):cut(x,float(y),4.4,3.2,7.6,8.1)
# Broad horizontal exterior sunshades of the conference/podium levels.
for z in [14.0,17.5,21.0,24.5,28.0,31.5]:
 add(0,-37.6,z,126,3.5,1.25)
 add(63.3,0,z,2.8,74,1.25)
for y in [-37,37]:
 for x in np.arange(-56,60,10):cut(float(x),y,15.2,7.4,2.6,14.4)
# Tall western service/stair core and the main wing. A deep frontage separation
# survives between them, crossed only by three bridges, as in the photos.
add(-53.0,0,33.5,20,67,110.5)
add(10,2.8,33.5,78,58.4,101.8)
add(55.0,0,33.5,16,67,110.5)
# Connecting rear structural band; preserves the gap at the front, not a box front.
add(-30,23,33.5,28,20,101.8)
# Ten occupied tower levels, with one partial setback below the top balcony.
levels=[34.0+i*10.25 for i in range(10)]
for i,z in enumerate(levels):
 # Open-front galleries are real deep recesses with floor plates and parapets.
 # The penultimate floor plate stops near the left, making a double-height void.
 if i==8:
  add(-15,-28.1,z,22,16.2,1.8)
  add(-15,-35.4,z+1.6,22,1.6,2.0)
 else:
  add(11,-28.1,z,75,16.2,1.8)
  add(11,-35.4,z+1.6,75,1.6,2.0)
 # Back wall windows: grouped into three bays rather than an undifferentiated grid.
 if i<8:
  for x in [-15,9,33]:
   cut(x,-26.0,z+3.0,19.0,3.4,6.2)
   for xx in [x-5.5,x,x+5.5]:details.append(box(xx,-25.0,z+3,1.1,2.2,6.2))
   details.append(box(x,-25.0,z+5.5,19,2.2,1.0))
 # Rear gallery, visible in official aerial photo; depth is an estimate.
 add(5,32.4,z,65,8.4,1.8)
 add(5,35.8,z+1.5,65,1.5,1.9)
 for x in [-17,4,25]:cut(x,32.0,z+3,17,3.3,5.8)
 # Right return balconies along the short side.
 for yy in [-16,7,25]:
  cut(63.0,yy,z+2.6,3.0,17.3,6.5)
 add(63.4,0,z,2.5,67,1.7)
# Front top setback creates the clear two-storey loggia, with two thick piers.
cut(21.0,-21.0,levels[8]+2.0,53,20,17.0)
for x in [7.0,31.0]:details.append(box(x,-26.4,levels[8]+1.5,2.8,5.2,19.2))
# Full top slab and projecting horizontal crown.
add(11,-28.0,levels[9]+10.05,77,18.0,2.1)
# Three bridges across the deep gap to the slim left core.
for z in [levels[0],levels[4],levels[8]]:
 add(-33,-25,z,25,12.8,2.1)
 add(-33,-30.5,z+1.8,25,1.6,2.8)
# Folded, solid-backed grilles. Full-height ribs follow the same folded outline
# as the broad panels rather than floating in a separate flat plane.
zs=[33.4,44.0,48.0,55.0,85.0,89.0,96.0,144.0]
offsets=[0,0,2.6,0,0,2.6,0,0]
def offset_at(z):return float(np.interp(z,zs,offsets))
def rib(x,w,front,thick):
 pts=[(front-o,z) for z,o in zip(zs,offsets)]
 pts += [(front-o+thick,z) for z,o in list(zip(zs,offsets))[::-1]]
 area=sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))
 if area<0:pts.reverse()
 return CrossSection([pts]).extrude(w).rotate((90,0,90)).translate((x-w/2,0,0))
for x,w in [(-55.0,15.6),(56.0,13.6)]:
 parts.append(rib(x,w,-34.0,4.2))
 for xx in np.arange(x-w/2+1.0,x+w/2-.5,2.7):parts.append(rib(float(xx),1.1,-35.0,1.7))
 for z in np.arange(36.0,142.0,5.1):add(x,-34.6-offset_at(float(z)),float(z),w+.3,1.6,1.1)
# Broad north-east folded screen from the official reverse aerial view.
parts.append(rib(-50.0,25.4,-34.2,4.4).rotate((0,0,180)))
for xx in np.arange(38.3,62.0,3.0):parts.append(rib(-float(xx),1.1,-35.2,1.7).rotate((0,0,180)))
for z in np.arange(36.0,142.0,5.1):add(50.0,34.8+offset_at(float(z)),float(z),25.7,1.6,1.1)
for z in levels:cut(38.7,35.0,z+3.0,3.2,7.0,6.1)
# Slim west front core: three tall inset openings remain open-looking despite fins.
for z in [39.0,80.0,121.0]:cut(-55,-34.0,z,5.6,9.1,13.5)
# Brown western end wall: one broad window column and three narrow columns.
# Sparse upper slot follows photographed crown. Lettering is not imitated.
for z in levels:
 for yy,w in [(-14,8.0),(8,3.3),(16,3.3),(25,3.3)]:
  cut(-63,yy,z+3.3,3.1,w,6.4)
cut(-63,14.5,138.0,3.2,21.0,3.0)
# North end of the tall core: three broad horizontal dark slots in the aerial.
for z in [122.0,131.0,140.0]:cut(-53,33.5,z,14.5,3.3,2.6)
# Upper side balconies reduce the brown core mass near the north-west corner.
for z in [levels[6],levels[7],levels[8]]:
 cut(-60,27,z+2.2,8.0,13.0,7.0)
 add(-62.5,27,z,3,16,1.9)
# Rear white end volume and stepped skin, as seen from above.
add(50,25,33.5,26,17,110.5)
for z in levels:
 for x in [41.2,48.1,55.0,61.3]:cut(x,33.5,z+3,4.8,3.0,6.4)
for x in [39,46,53,60]:add(x,34.1,33.5,1.2,2.1,110.5)
# Actual roof is recessed between parapets: do not cap the whole outline flat.
# Retain broad terrace and a small observed service core, not guessed equipment.
add(8.0,3.0,135.0,81,60.0,2.1)
for xx in [-32.5,48.5]:add(xx,3,136.6,2.0,60.0,2.8)
add(8,32.0,136.6,82,2.0,2.8)
add(-47,13,143.3,18,29,3.4)
# Open roof edge frame; thick posts anchored into terrace/slab, not wire railings.
for x in [-24,-6,12,30,48]:add(x,-29.5,136.7,2.0,2.0,7.3)
add(12,-29.5,142.4,74,2.0,1.8)
# Entrance canopy tied back into podium.
add(21,-40,11.0,54,9.0,1.7)
for x in [-5,20,46]:add(x,-43.2,3.0,2.2,2.2,8.3)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1,[(p.volume(),p.bounding_box()) for p in solid.decompose()]
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.apply_scale(150.0/mesh.extents.max())
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight,'faces',len(mesh.faces))
