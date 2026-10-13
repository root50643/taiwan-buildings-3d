'''國立臺北商業大學北商學舍；U形量體及實拍可見立面近似，毫米。'''
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def hip(x,y,z,w,d,h):
 # Low pitched orange hipped roof visible in official photographs; slope estimated.
 parts.append(CrossSection.square((w,d),center=True).extrude(h,scale_top=((.07,.88) if d>w*2 else (.25,.25))).translate((x,y,z)))
add(0,0,0,150,150,3)
# One U-shaped building: two seven-storey longitudinal wings and lower five-storey link.
# North opening faces -Y. Courtyard remains open through roof, not filled with a block.
for x in [-52,52]:add(x,0,2.8,28,128,87)
add(0,51,2.8,132,26,60)
# Connected low plinth below the wings, not an entire courtyard podium.
for x in [-52,52]:add(x,0,2.8,29.5,129.5,3)
add(0,51,2.8,133,27,3)
# Rooftops follow observed low hipped profiles; no PV attributed to this dormitory.
for x in [-52,52]:
 add(x,0,89,32,132,1.6);hip(x,0,90.5,32,132,3.5)
add(0,51,62,134,29,1.6)
# Cross-link hip, rotated so ridge follows long cross wing.
parts.append(CrossSection.square((134,29),center=True).extrude(3.0,scale_top=(.91,.07)).translate((0,51,63.5)))
# Southern staircase housings rise above seven-storey wings; parapet vents are backed.
for x in [-52,52]:
 add(x,54,87,25,22,12)
 add(x,54,98,28,25,1.4);hip(x,54,99.2,28,25,3.4)
 for dx in [-7,0,7]:cut(x+dx,65,91,2.5,3,5)
# Inner stair cores occur near the open ends on the space-use diagram and rise
# behind the main roof in the official east-side photo. Their offsets are estimated.
for x in [-38,38]:
 add(x,-32,2.8,10,20,94)
 add(x,-32,96.2,15,24,1.4);hip(x,-32,97.5,15,24,3.3)
 side=x+(5 if x<0 else -5)
 cut(side,-32,8,2.8,11,78)
 for z in range(12,86,7):details.append(box(side+(1 if x>0 else -1),-32,z,1.5,11.3,.8))
# EAST facade: six wide structural bays each with two window groups.
# Never replace the two different two-storey loggias by a fully regular grid.
ys=[41,22,3,-16,-35,-54]
for f in range(7):
 z=7+f*11.7
 for j,y in enumerate(ys):
  if (j==2 and f in [2,3]) or (j==5 and f in [4,5]):continue
  if f==0:
   cut(66,y,z,3.2,16.5,8)
   for q in [-4,0,4]:details.append(box(65.1,y+q,z,1.8,.8,8))
  else:
   for dy in [-4.3,4.3]:
    cut(66,y+dy,z,3.0,7.5,6.3)
    # Subtle mullion divisions flush with outside wall; no thick fake piers.
    details.append(box(65.2,y+dy,z,1.6,.8,6.5))
   add(66.2,y,z+6.6,1.8,17.3,.95)
# Large deep loggias seen from the playing fields. Keep recesses, one central lower,
# one north-end upper. Back corridor thickness is unmeasured and retained at 3 mm.
for y,z in [(3,30.4),(-54,53.8)]:
 cut(55,y,z,25,16.7,22.6)
 # heavy balustrade, backed to floor and the side walls
 details.append(box(65.8,y,z,1.6,17.4,2.9))
 # relief perforations instead of unsafe submillimetre railings
 for yy in [-6,-3,0,3,6]:cuts.append(box(66,y+yy,z+1.2,2.5,1.25,.9))
# SOUTH stair end of east wing: tall glass strip and small stacked balconies.
for f in range(7):
 z=6.8+f*11.7
 cut(66,57,z,2.8,7.2,8.2)
 # North-facing end pieces are detailed separately below.
# Inner east-facing courtyard elevation: visible horizontal corridor openings.
# Six bays and six repeated upper floors are photograph-estimated, not room-count mapping.
for f in range(1,7):
 z=7+f*11.7
 for y in ys:
  cut(38,y,z,4,16.3,6.4)
  add(37.4,y,z-.8,1.7,17.2,1.8)
# North tip facades: asymmetry recorded in the official handbook.
# Western tip has a broad blank band on right and a stacked balcony lane at left.
for f in range(7):
 z=6.8+f*11.7
 cut(-48,-64,z,8,3,7.7)
 add(-42,-65.5,z-1,8,5,1.4)
 add(-42,-67.1,z-.8,8,1.4,2.3)
# East tip: glass strip at inner edge, large double-height recess high on outer side.
for f in range(7):
 z=6.8+f*11.7
 cut(44,-64,z,9,3,7.7)
cut(57,-60.5,53.8,13,10,22.6)
add(57,-64.2,53.4,13.5,1.8,3)
# Lower west tip blank panels intentionally left plain as seen in handbook.
# Inner west courtyard visible in handbook: seven-storey banded corridor elevation.
for f in range(1,7):
 z=7+f*11.7
 for y in ys:
  cut(-38,y,z,4,16.3,6.4)
  add(-37.4,y,z-.8,1.7,17.2,1.8)
# Cross-link courtyard face: lower five storeys, not seven.
for f in range(5):
 z=7+f*11.7
 for x in [-30,-18,-6,6,18,30]:cut(x,38,z,9.0,3.0,6.5)
# Low covered walkway visible along inner west and back. It does not bridge across
# or fill the central courtyard. Unseen east ground-floor canopy is not invented.
add(-34,0,14,10,116,1.7)
for y in [-54,-35,-16,3,22,38]:add(-30,y,2.8,2.0,2.0,11.5)
add(0,34,14,77,9,1.7)
for x in [-30,-15,0,15,30]:add(x,30.5,2.8,2.0,2.0,11.5)
# West OUTER long elevation and south outer link are unknown; left undecorated.
# This explicit blankness is preferable to mirroring asymmetric eastern loggias.
# Roof service boxes visible at eastern north end, position and size approximate.
add(53,-42,91,8,8,7)
solid=parts[0]
for p in parts[1:]:solid+=p
for c in cuts:solid-=c
for p in details:solid+=p
assert len(solid.decompose())==1
# Coordinate convention: geographic east is -X, north is -Y.
solid=solid.scale((-1,1,1))
m=solid.simplify(.00001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
