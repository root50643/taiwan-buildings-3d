"""朝陽波錠圖書館有界外觀原型。Units mm. Explicit estimates, not a survey."""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def slab(poly,z,h):return CrossSection([poly]).extrude(h).translate((0,0,z))
def profile(poly,y,d):return CrossSection([poly]).extrude(d).rotate((90,0,0)).translate((0,y+d/2,0))
def arch(x,y,z,w,h,d):
 r=w/2; spring=z+h-r
 pts=[(x-r,z),(x+r,z),(x+r,spring)]+[(x+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,33)[1:]]
 return profile(pts,y,d)
# Principal floor outline traced from official floors: long bar, curved south end,
# west elevator projection, east stair tower, and upper south-east setback.
add(0,0,0,166,82,3)
add(1,0,2.8,126,44,22)
# Semicircular south end only rises to fourth-floor roof, not sixth floor.
arc=[(-62,-18),(-62,18)]+[(-62+18*math.cos(t),18*math.sin(t)) for t in np.linspace(math.pi/2,3*math.pi/2,49)[1:]]
parts.append(slab(arc,2.8,29))
parts.append(slab([(-62,-8),(-45,-8),(-45,-22),(64,-22),(64,22),(-62,22)],24.5,22.8))
# Historical official oblique photo resolves higher south-west setback block:
# three visible grey window rows, versus two on the main front wall.
add(-53.5,7,46,17,30,8.0)
add(-53.5,7,53.5,18.5,31.5,1.4)
# Low entry projection, actually open below deep canopy.
for x in [-54,-19]:
 parts.append(CrossSection.square((5,6),center=True).extrude(17.5,scale_top=(.72,.8)).translate((x,-29,3)))
add(-36.5,-26,20,41,17,7)
# Behind the entry, recessed broad round-headed doorway; arch is shallow, backed.
cuts.append(arch(-36.5,-22,3.1,22,13,1.4))
details.append(arch(-36.5,-22.4,3.1,24,14,1.5)-arch(-36.5,-22.6,2.9,21.5,12.8,2))
# Main east stair tower: front-center cap flares outward. Height ~31m bounded28–35m.
add(4,-24,2.8,17,10,51)
parts.append(CrossSection.square((17,11),center=True).extrude(6,scale_top=(1.35,1.25)).translate((4,-24,52)))
add(4,-24,58,24,15,1.3)
# West elevator block follows all six floor diagrams. Different roof masses.
add(-9,26,2.8,32,10,53)
add(-9,26,55,33,11,1.3)
# Northern roof/service block (B1) differs from long western block (B3).
add(53,13,46,17,17,9)
add(53,13,54.5,18,18,1.3)
# Faceted glass roof: two closed sloping fields, a shallow folded valley.
# Each footprint stays backed by the main roof, never represented as open atrium.
for x,w in [(-24,28),(7,32)]:
 parts.append(profile([(x-w/2,47),(x+w/2,47),(x+w/2,51),(x+w/2-1.2,51),(x,48.3),(x-w/2+1.2,51),(x-w/2,51)],0,27))
# Strong horizontal overhangs: lower terrace and upper glass-floor cornices.
for z in [23,42.2,47]:
 add(8,-22.6,z,113,3.4,1.6)
 add(1,22,z,128,2,1.5)
 add(64,0,z,2.5,46,1.5)
# Front regular paired upper windows, with tower interrupting the rhythm.
for z in [29,36]:
 for x in [-57,-50,-42,-37.5,-33,-28.5,-24,-19.5,-15,-10.5,-6,18,24,30,36,42,48,54,60]:
  # southern cutaway has no wall at -57/-50 front, handled separately below
  if x>=-45:cut(x,-22,z,3.0 if x<0 else 3.8,1.1,5.1)
# Sixth-floor glazing is one shallow recessed strip, with flush backed mullions.
# It cannot cut the cornices: >0.8 mm final vertical land on both sides.
for a,b in [(-44,-6),(15,63)]:
 cut((a+b)/2,-22.1,44.7,b-a,.7,1.5)
 for x in np.arange(a+1.5,b,2.5):details.append(box(x,-21.85,44.7,1.0,.5,1.5))
# Lower red-brick facade has short ground windows, tall middle windows,
# then shorter upper windows. Uneven narrow/standard grouping retained.
for z,h in [(4.0,2.7),(10,6.8),(18.7,3.3)]:
 for x,w in [(17,2.2),(22.2,3.7),(27.4,3.7),(32.6,3.7),(37.8,3.7),(43,3.7),(48.2,3.7),(53.4,3.7),(58.6,3.7)]:
  cut(x,-22,z,w,1.1,h)
  if h>5:details.append(box(x,-21.7,z+4.6,w,.8,1.0))
for z in [17.2]:add(39,-22.5,z,49,1.5,1.2)
# Entry porch on right red-wall facade.
add(36,-24,8.4,18,5,1.6)
for x in [28.5,43.5]:add(x,-24,2.8,2.2,2.2,5.7)
# Third-floor band is below its uninterrupted upper rim, partly hidden by entry.
add(8,-22.6,28.0,113,3.4,1.3)
for a,b in [(-17,-6),(15,63)]:
 cut((a+b)/2,-22.1,25.45,b-a,.7,1.7)
 for x in np.arange(a+1.5,b,2.5):details.append(box(x,-21.85,25.45,1.0,.5,1.7))
# Central tower: four tall grey-floor glazed panels and two lower brick panels.
# Narrow central glazing continues vertically, split by backed floor spandrels.
cut(4,-29,23.2,5.1,1.1,26.1)
for z in [29.3,36.4,43.5]:details.append(box(4,-28.7,z,5.1,.6,1.0))
# Central glazing mullion is backed throughout; no slender independent rod.
details.append(box(4,-28.7,23.2,1.05,.6,26.1))
for z,h in [(6.1,6.5),(15.4,4.9),(24,4.8),(31.1,4.8),(38.2,4.8),(45.3,4.0)]:
 for x in [-2.1,10.1]:cut(x,-29,z,2.0,1.1,h)
for z,h in [(6.1,6.5),(15.4,4.9)]:cut(4,-29,z,2.3,1.1,h)
# Vent is a shallow backed relief in the straight tower face BELOW the flaring cap.
# v1 cut wrongly entered the flaring cap and left a sub-0.8mm front skin.
cut(4,-29,50.2,5,1.1,1.0)
# Entry sign parapet has three narrow slots at either end.
for x in [-51,-48,-45,-28,-25,-22]:cut(x,-34.5,22,1.4,1.1,3.3)
# Main rectangular lights have upper transoms, not an extra row of floors.
for z in [29,36]:
 for x in [-42,-37.5,-33,-28.5,-24,-19.5,-15,-10.5,-6,18,24,30,36,42,48,54,60]:
  details.append(box(x,-21.7,z+3.6,3.0 if x<0 else 3.8,.8,.95))
  details.append(box(x,-21.7,z,1.0,.8,5.1))
# Door glazing set on the recessed arch back, shallow backed relief.
for x in [-43,-39.5,-33.5,-30]:details.append(box(x,-21.45,3.2,1.0,.5,5.8))
for z in [5.4,8.6]:details.append(box(-36.5,-21.45,z,17,.5,1.0))
# Central door jambs taller than the side fanlight panels.
for x in [-39,-34]:details.append(box(x,-21.45,3.2,1.0,.5,8.5))
details.append(box(-36.5,-21.45,10.7,6,.5,1.0))
# South high-side windows above rounded base, as shown in frontal/side source.
for z in [29,36,43]:
 for x in [-58,-51]:cut(x,-8,z,4.4,1.3,5.1)
# Rear window layout unverified: retain floor-derived stepped mass, no invented array.
# Official 1F plan: north-end external exit stair, absent on 2F+.
# Low platform and broad fused treads only; exact exterior landing elevation unknown.
add(71,15,2.8,14,14,4.5)
for i in range(7):add(72,-18+i*4.5,2.8,12,5,.6*(i+1))
# Broad fused entrance steps.
for i in range(4):add(-36.5,-39+i*2,2.8,29,2.8,.6*(i+1))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
solid=solid.scale((150/166,150/166,1.12*150/166))
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print(mesh.extents,mesh.is_watertight)
