"""Self-authored facade SECTION of NTOU Matsu alumni residence, millimetres.
Only the photographed front 2+3-bay elevation, entrance, canopy and roof brow are
included. Flat cut rear is an explicit section boundary, not a claimed rear facade.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def column(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
def frontprofile(poly,y,d):
 return CrossSection([poly]).extrude(d).rotate((90,0,0)).translate((0,y+d/2,0))
add(0,0,0,150,48,2.8)
# Three-storey cut frontage, asymmetric two-bay and three-bay wings.
add(-45,4,2.7,48,24,59.0)
add(33,4,2.7,72,24,59.0)
add(-12,7,2.7,18.5,18,53.0)
# Deep backed window reveals; front balconies have open sides above parapets.
left=[-57,-33];right=[9,33,57]
for x in left+right:
 for z in [24.3,44.0]:cut(x,-8,z,18.3,5.0,13.4)
 # ground window glazing, all backed rather than through to invented rooms.
 cut(x,-8,7.0,18.3,3.8,11.5)
# Central recessed doorway and upper two offset glazed strips.
cut(-12,-2,4.8,13.8,3.6,15.0)
cut(-12,-2,26.2,14.2,3.6,3.8)
cut(-12,-2,42.5,14.2,3.6,10.5)
# Distinctive centre window group: backed horizontal transom and paired verticals.
for x in [-16.7,-12,-7.3]:details.append(box(x,-1.2,42.3,1.15,2.4,10.9))
details.append(box(-12,-1.2,47.8,14.6,2.4,1.15))
for x in [-16.7,-12,-7.3]:details.append(box(x,-1.2,26.0,1.15,2.4,4.2))
# Two left projecting box balconies; three right flush/parapet framed bays.
for x in left:
 for z in [22.0,41.7]:
  add(x,-12,z,20.8,10.5,1.5)
  add(x,-16.5,z,20.8,1.8,6.2)
  for sx in [-1,1]:add(x+sx*9.6,-12,z,1.65,10.5,6.2)
  cut(x,-17.4,z+1.2,17.2,1.0,3.7)
for x in right:
 for z in [22.0,41.7]:
  add(x,-10.7,z,22.8,6.9,1.5)
  add(x,-13.3,z,22.8,1.8,6.2)
  cut(x,-14.2,z+1.2,19.2,1.0,3.7)
# Thick structural uprights, with left intermediate slender shading fins.
for x in [-69,-21,-3,21,45,69]:add(x,-10,21.2,2.8,7.7,40.6)
for x in [-57,-45,-33]:add(x,-10,44.0,1.25,7.5,17.7)
# Roof overhang brows; rear stops at the explicitly cropped section boundary.
add(-45,1,61.0,54,30,1.8);add(33,1,61.0,78,30,1.8)
add(-12,6,55.3,18.5,20,1.6)
# Single-storey open canopy across facade with round columns and open bays.
for x in [-70,-46,-22,0,24,48,70]:column(x,-19.4,2.7,1.45,19.8)
add(0,-19.2,21.1,146,3.4,2.0)
for x in [-70,-46,-22,0,24,48,70]:add(x,-12.0,20.8,1.8,15.9,1.7)
# Low parapet walls and central entry opening, seen behind the ceremonial ribbon.
add(-45,-19.0,2.7,46,2.1,5.0);add(34,-19.0,2.7,67,2.1,5.0)
# Small traditional tile canopy over the central entrance, separate from main roof.
# Solid sloping plate, bonded to the entrance wall and front canopy beam.
roofpoly=[(-23,21.8),(-1,21.8),(-1,24.2),(-4,26.2),(-20,26.2),(-23,24.2)]
parts.append(frontprofile(roofpoly,-12.6,14.8))
# Robust raised tile stones kept backed to canopy; regular tiny texture omitted.
for x in [-19.5,-16,-12.5,-9,-5.5]:
 add(x,-14.7,25.4,2.0,3.5,1.2)
# Shallow three-step approach.
for i in range(3):add(-12,-21.8+i*1.8,2.7,17,2.1,.6*(i+1))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert solid.status().name=='NoError' and len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('Dimensions mm',mesh.extents,'watertight',mesh.is_watertight)
