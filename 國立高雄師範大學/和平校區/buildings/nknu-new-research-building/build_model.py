"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. No survey or interior data used.
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
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def gable(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x,z+h)],y,d))
def arch(x,y,z,w,h,depth):
 r=w/2; spring=z+h-r
 pts=[(x-r,z),(x+r,z),(x+r,spring)]
 pts += [(x+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,25)[1:]]
 return profile(pts,y,depth)
def arch_cut(x,y,z,w,h,depth):cuts.append(arch(x,y,z,w,h,depth))
def arch_trim(x,y,z,w,h):
 # Backed relief ring, fused into the wall, not a separate floating shell.
 details.append(arch(x,y,z,w+1.7,h+.85,1.7)-arch(x,y-.1,z-.2,w,h+.2,2.3))
def hip(x,y,z,w,d,h):parts.append(CrossSection.square((w,d),center=True).extrude(h,scale_top=(.72,.03)).translate((x,y,z)))
def column(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
def step(x,y,w,n=3):
 for i in range(n):add(x,y+i*1.4,2.8,w,1.7,.7*(i+1))
# NKNU new Research Building. Completed 2020; not the demolished old research building.
# U/H-shaped footprint with full-height open inner court, tied by front/back circulation.
add(0,0,0,150,147,3)
# Long left wing, shorter stepped right wing, and recessed middle front cross-wing.
add(-40,0,2.8,43,112,92.4)
add(43,13,2.8,38,86,92.4)
add(10,-38,2.8,61,26,92.4)
add(5,42,2.8,53,20,92.4)
# Right front stair/vertical signage tower with glazing wrapped around the front corner.
add(43,-43,2.8,23,33,104.2)
# Open top court: no roof or slab spanning this void. Ground surface is the 3mm base.
# Building components leave court x=-18.5..24, y=-25..32 clear.
# Rear stair projects into rear notch, footprint from official upper-storey floorplans.
add(3,52,2.8,27,14,92.4)
# Left front: projecting balcony stack beside narrow recessed window zone.
# Broad balcony recesses are carved, with thick integrated front parapets.
for z in [5,18,31,44,57,70,83]:
 cut(-50,-56,z,18,7,9.2)
 details.append(box(-50,-58.2,z-.7,20.3,6,1.4))
 details.append(box(-50,-60.6,z,20.3,1.2,3.1))
 for x in [-59.55,-40.45]:details.append(box(x,-58.2,z,1.2,5.9,3.1))
 # Immediately adjacent three deep window wells, a visible asymmetry in the actual facade.
 for x in [-35.6,-30.3,-25]:cut(x,-56.3,z,3.6,5.2,9.2)
 # Backing windows in the balcony recess, recessed further rather than painted.
 for x in [-55,-49,-43]:cut(x,-52.3,z+.7,3.7,2.9,7.1)
# Central entrance bay is set well back behind a double-height projecting portico.
cut(7,-50,3,36,14,25.8)
# Keep a real dark backing doorway after the portico opening, not a sealed flush front.
for x in [-5,7,19]:cut(x,-43,4,8.8,3,13)
# Five upper central balconies form a deep repeated sheltered stack above the entrance.
for z in [31,44,57,70,83]:
 cut(5,-51,z,33,9,9.2)
 details.append(box(5,-54.1,z-.7,35.5,10,1.5))
 details.append(box(5,-58.45,z,35.5,1.3,3.1))
 for x in [-12.1,22.1]:details.append(box(x,-54.1,z,1.3,9.8,3.1))
 for x in [-6,5,16]:cut(x,-46.5,z+.6,7.8,2.8,7.7)
# Narrow windows between central balconies and solid signage pier.
for z in [31,44,57,70,83]:cut(27.7,-51.2,z+.4,4,3.2,8)
# Double-height main entrance porch; 2 substantial pillars and roof plate.
add(7,-57,28.0,54,18,2.2)
for x in [-15.5,20.5]:add(x,-63.8,2.8,3.5,3.5,25.6)
for x in [-8,8]:add(x,-57,26.6,2.0,17.5,1.7)
for i in range(5):add(7,-66+i*1.1,2.8,48,1.5,.55*(i+1))
# Corner glazing tower: alternating horizontal spandrels, recessed two-sided glazed bands.
for z in [4,17,30,43,56,69,82]:
 cut(46,-59.6,z,14.5,3.2,10.8)
 cut(54.3,-50,z,3.2,18,10.8)
 for x in [40.5,46,51.5]:details.append(box(x,-59.5,z,1.0,1.8,10.8))
 for y in [-56,-50,-44]:details.append(box(54.2,y,z,1.8,1.0,10.8))
 add(46,-60,z+10.7,16.1,2.5,1.25)
 add(54.5,-50,z+10.7,2.5,20,1.25)
# Upper head is wider than glass corner and wraps a real roof enclosure.
add(43,-43,94.8,25,35,12.2)
for x in [30.9,55.1]:add(x,-43,106.8,1.3,35,3.0)
for y in [-59.85,-26.15]:add(43,y,106.8,25,1.3,3.0)
add(43,-40,106.8,10,12,4.1)
# Right-hand visible flank: spaced little balcony stacks and staggered small windows.
for z in [5,18,31,44,57,70,83]:
 for y in [0,35]:
  cut(62.1,y,z,7,18,9.2)
  details.append(box(64,y,z-.7,6.0,20.5,1.4))
  details.append(box(66.3,y,z,1.25,20.5,3.1))
  for yy in [y-9.65,y+9.65]:details.append(box(64,yy,z,5.8,1.25,3.1))
 for y in [-20,17,50]:cut(62.1,y,z+2.5,3,4.2,5.8)
 # Small windows on the blank tower flank match actual vertical irregular rhythm approximately.
 cut(54.6,-33,z+4,3,3.6,4)
# Back and opposite outside elevations: functional window rhythm from floorplan, not surveyed.
for z in [5,18,31,44,57,70,83]:
 for y in [-45,-28,-11,6,23,42]:cut(-61.7,y,z,3.4,10,8)
 for x in [-50,-34,34,48]:cut(x,56,z,10,3.2,8)
# Four sides of the open courtyard get broad paired recesses rather than interior room modeling.
for z in [5,18,31,44,57,70,83]:
 for y in [-17,0,19]:cut(-18.6,y,z,2.7,10,7.8);cut(24,y,z,2.7,10,7.8)
 for x in [-7,11]:cut(x,-25,z,11,2.8,7.8);cut(x,32,z,11,2.8,7.8)
# Roof has protective rims following each roof block; outer and court-facing rim are backed.
for x,y,w,d in [(-40,0,43,112),(43,13,38,86),(10,-38,61,26),(5,42,53,20),(3,52,27,14)]:
 for xx in [x-w/2+.65,x+w/2-.65]:add(xx,y,94.9,1.3,d,2)
 for yy in [y-d/2+.65,y+d/2-.65]:add(x,yy,94.9,w,1.3,2)
# A broad rooftop stair/service head visible toward the rear, separate from the corner head.
add(3,47,94.9,16,17,4.5)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
