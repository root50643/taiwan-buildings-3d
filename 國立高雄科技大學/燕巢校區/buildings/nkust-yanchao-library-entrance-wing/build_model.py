"""Original photo-derived NKUST exterior miniature. Units: mm.
Visual estimates from cited public photographs, not a measured survey.
No third-party 3D geometry; see sources.json for scope and unknown elevations.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def cyl(x,y,z,r,h,n=120):return Manifold.cylinder(h,r,r,circular_segments=n).translate((x,y,z))
def sector(r1,r2,a,b,z,h):
 ts=np.linspace(math.radians(a),math.radians(b),max(3,int(abs(b-a)/2)+1))
 pts=[(r2*math.cos(t),r2*math.sin(t)) for t in ts]+[(r1*math.cos(t),r1*math.sin(t)) for t in ts[::-1]]
 return CrossSection([pts]).extrude(h).translate((0,0,z))
def profile(poly,y,depth):
 if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))<0:poly=poly[::-1]
 return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def recess_poly(poly,y,depth):cuts.append(profile(poly,y,depth))
# Only the long principal entrance wing and its junction glass tower.
# The east turning library wing is excluded rather than reconstructed from a single oblique.
# Front=-Y; rear cap plain. Layout depth is approximate from the official 2020 evacuation plan.
add(0,0,0,150,86,3)
# Five-storey frontal body: ground arcade, ribbon floor, 3 tall framed rows above.
add(-5,5,2.8,128,36,78.2)
# Five main photographed supports, four full framed glazing bays; left core is solid.
# Undercut front arcade preserves the real deep void, no sealed inner shell.
cut(-4,-13,3.0,127,14,17.5)
# Entrance double-height opening at the final two spans.
cut(34,-13,3.0,49,14,28.2)
for x in [-64,-38,-12,14,40,64]:details.append(cyl(x,-17.0,2.8,2.15,31.7,48))
# Brick/ribbon floor on the left: long glazing bands with variable width jambs.
for a,b in [(-61,-40.5),(-35.5,-14.5),(-9.5,11.5)]:cut((a+b)/2,-13.2,22,b-a,2.7,7)
# Exposed entrance lintel and lower horizontal frame.
add(-3,-17,31.4,129,8.6,2.4)
# Four protruding high frames with 3 vertical-glazing rows.
# Photograph gives four bays after the broad solid western stair core.
for index,(x,w) in enumerate([(-39,22),(-13,22),(13,22),(39,22)]):
 add(x,-14.8,33.0,w+2.8,6.8,47.8)
 # Main horizontal glazing openings separated by robust but visually narrow rails.
 for z,h in [(35.2,13.2),(50.0,13.2),(64.8,13.7)]:
  cut(x,-18.5,z,w,4.5,h)
  # Unequal wide and narrow light groups derived from the photographic screen rhythm.
  # Opaque vertical fins alternate with broad glass panels, not regular square windows.
  positions=[(-9.6,1.2),(-5.2,2.0),(1.4,1.65),(7.2,1.7)]
  for dx,fw in positions:details.append(box(x+dx,-17.7,z,fw,3.2,h))
 # Projected side strip and its 3 separate small vertical windows.
 for z in [36,51,66]:cut(x-w/2-1.1,-18.0,z,1.4,2.5,8.8)
# Western stair/name wall intentionally broad and almost blank.
add(-60,-14.5,33,14,7.4,47.8)
for z in [36.0,50.8,65.6]:
 cut(-51.2,-16.1,z,3.0,3.0,9)
 cut(-69.1,-6,z,2.5,8,7)
# Junction tower is taller, slender and glazed continuously to ground.
add(61,3,2.8,15.5,35,82.2)
cut(61,-15.0,5.4,12.6,2.5,76.8)
for z in [17,29.7,42.4,55.1,67.8]:details.append(box(61,-14.4,z,12.6,1.6,1.2))
for x in [57.3,64.7]:details.append(box(x,-14.4,5.4,1.1,1.6,76.8))
# Glazed right return visible beside the turning library wing.
for z in [6.0,18.7,31.4,44.1,56.8,69.5]:cut(68.8,1,z,2.3,27,11.2)
# The white entrance canopy has TWO supporting columns and a deeper recessed doorway.
add(30,-24,17.1,35,22,2.5)
for x in [15,45]:details.append(cyl(x,-32.0,2.8,1.9,15.8,48))
cut(30,-6.2,4.2,22,2.0,12)
# Exposed roof retains its setbacks and the photographed four low louvered screens.
add(-5,5,80.2,128.8,36.8,1.6)
for x in [-39,-13,13,39]:
 # Open-ended shallow louver hood; no speculative plant represented.
 for xx in [x-9.2,x+9.2]:add(xx,9,81.2,1.7,15,5.2)
 add(x,15.8,81.2,20,1.7,5.2)
 add(x,9,85,21,16.5,1.5)
 # Four broad slats are integrated to the lower roof and upper hood.
 for xx in [x-6.5,x-2.2,x+2.2,x+6.5]:add(xx,1.8,81.2,1.25,2.0,5.0)
# Roof tower rim is kept a robust solid cap; fences/antennas not reconstructed.
add(61,3,84.4,16.4,35.8,1.6)
for i in range(3):add(30,-39+i*1.8,2.8,40,2,.5*(i+1))
# Rear service elevation and attached east wing are beyond this documented segment.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print('PARTS', [(round(s.volume(),4),s.bounding_box()) for s in solid.decompose()])
assert len(solid.decompose())==1, 'Detached part: fix source geometry'
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.is_winding_consistent
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'triangles',len(mesh.faces))
