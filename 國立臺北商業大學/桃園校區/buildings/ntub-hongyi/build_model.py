'''國立臺北商業大學弘毅樓，全形量體／有證立面近似，非測繪。'''
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def det(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
def hip(x,y,z,w,d,h):
 # low hipped roof as seen in official photos; slope estimated.
 low=np.array([[x-w/2,y-d/2,z],[x+w/2,y-d/2,z],[x+w/2,y+d/2,z],[x-w/2,y+d/2,z]])
 high=np.array([[x-w/2+2,y-d/2+2,z+h],[x+w/2-2,y-d/2+2,z+h],[x+w/2-2,y+d/2-2,z+h],[x-w/2+2,y+d/2-2,z+h]])
 parts.append(Manifold.hull_points(np.vstack([low,high])))
add(0,0,0,150,150,3)
# Open end faces -Y. Local coordinates are not surveyed geographic north.
# Two seven-level outer bars; inward five-level classroom shoulder plus terrace.
for s in [-1,1]:
 add(s*55,0,2.8,27,124,87.2)
 add(s*36,-1,2.8,16,104,63.7)
 add(s*36,-1,65.6,20,106,1.8)
 # rooftop terrace canopy supported by backed posts, courtyard remains open.
 add(s*32,-1,77.1,15,104,1.7)
 for y in [-47,-28,-9,10,29,47]:add(s*30,y,66,1.5,1.7,12.5)
 hip(s*55,0,89.5,30,127,1.8)
# Six-floor rear classroom bridge closes only back of court.
add(0,50,2.8,112,25,75.7)
add(0,50,78,114,28,1.8)
# Lower spine roof has an open-sided shelter shown across the courtyard.
add(0,49,82.7,90,10,1.7)
for x in [-43,-29,-15,0,15,29,43]:add(x,49,78.4,1.5,1.7,5.2)
# Rear stair/service towers: roof and slot band visible, exact rear faces unknown.
for s in [-1,1]:
 add(s*40,45,65,18,24,29)
 hip(s*40,45,93.3,21,27,2)
 cut(s*40,32.7,85.8,14,2.5,5.4)
 for dx in [-4.8,-1.6,1.6,4.8]:det(s*40+dx,33.3,85.5,.85,1.4,6)
# Front blue-glass stair towers: continuous glazing, backed coarse mullions.
for s in [-1,1]:
 add(s*36,-47,2.8,18,28,94.2)
 add(s*36,-48,95.5,21,32,2.1)
 cut(s*36,-61,4,13,3,90)
 for z in np.arange(7,94,4.2):det(s*36,-60.1,float(z),13.4,1.4,.8)
 det(s*36,-60.1,4,.8,1.4,90)
 # Inner pale side has six stacked deep balcony recesses, not glazed wall grid.
 for z in [4,17,30,43,56,69]:
  cut(s*27,-43,z,6,16,9.7)
  add(s*24.8,-43,z-1,7,18,1.6)
  det(s*22,-43,z+.1,1.2,18,1.8)
 add(s*24.5,-43,80,8,20,1.8)
 # Outer end: four large window bands over two-storey podium plus terrace.
 for z in [39,51.5,64,76.5]:
  cut(s*58.5,-62,z,17,2.8,8)
  for dx in [-6.375,-4.25,-2.125,0,2.125,4.25,6.375]:det(s*58.5+dx,-61.1,z,.8,1.4,8)
  for dz in [2.6,5.2]:det(s*58.5,-61.1,z+dz,17.2,1.4,.8)
 for z in [30.5,43,55.5,68,80.5]:cut(s*47,-62,z,3.2,2.8,7.5)
 add(s*57,-63,2.8,25,14,25)
 cut(s*57,-70,5,20,3,20)
 for dx in [-6.5,0,6.5]:det(s*57+dx,-69.1,5,1,1.4,20)
 det(s*57,-69.1,15,20,1.4,1)
 # open terrace above podium has three roof supports, coarse railing.
 add(s*57,-63,27.1,26,15,1.8)
 for dx in [-10,0,10]:add(s*57+dx,-68,28,1.5,1.7,8)
 add(s*57,-64,35.1,27,16,1.7)
 add(s*57,-69,28,26,1.3,1.8)
 # Courtyard classroom facade: 2 long window groups, 5 occupied rows.
 for y in [-20,18]:
  for z in [5,18,30.5,43,55.5]:
   cut(s*28,y,z,2.8,33,7.5)
   for dy in [-12,-6,0,6,12]:det(s*28.1,y+dy,z,1.4,.85,7.5)
   for dz in [2.5,5]:det(s*28.1,y,z+dz,1.4,33.2,.8)
   add(s*27.2,y,z+7.3,3.5,34,1.1)
# Rear inner courtyard: exactly 7 principal groups (5 center, 2 pale returns).
xs=[-31,-21,-10.5,0,10.5,21,31]
for z in [5,18,30.5,43,55.5,68]:
 for x in xs:
  if z in [5,18] and x in [-10.5,0,10.5]:continue
  cut(x,37.5,z,6.9,2.8,7.7)
  det(x,36.8,z,.9,1.5,7.8);det(x,36.8,z+2.4,7,1.5,.85)
# Central double-height recessed entry, with solid upper sign panel.
cut(0,37.5,3,28,9,23)
add(0,34.5,16,27,2,10)
for x in [-10.5,10.5]:cut(x,33.5,18,6.5,2.5,6.5)
for x in [-12,0,12]:det(x,33.2,3,1.2,2,13.5)
add(0,32.5,14.2,29,5,1.5)
# Exterior documented only on ONE wing (env0); distant flank/back intentionally plain.
# Outside has two broad bands at intermediate levels, corner single windows,
# and a separate top row. Counts below are photo-supported main groups only.
for z in [30.5,43,55.5,68]:
 for y in [-16,23]:
  cut(68.5,y,z,2.8,33,8)
  for dy in [-12,-6,0,6,12]:det(67.7,y+dy,z,1.4,.85,8)
  for dz in [2.6,5.2]:det(67.7,y,z+dz,1.4,33,.8)
 for y in [-51,53]:cut(68.5,y,z,2.8,6,7.7)
# Upper storey separate group spacing is checked against env0 (12 windows).
for y in np.linspace(-53,53,12):cut(68.5,float(y),80.2,2.8,6,7.2)
# Rooftop photovoltaic source proves panels exist adjacent a signed rear tower,
# but does not establish which wing or complete extent. Unlocalized equipment is
# deliberately NOT synthesized here; this is an undated photographic mass, NOT a dated pre-PV reconstruction.
solid=parts[0]
for p in parts[1:]:solid+=p
for c in cuts:solid-=c
for p in details:solid+=p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
