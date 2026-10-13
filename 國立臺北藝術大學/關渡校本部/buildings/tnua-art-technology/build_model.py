"""Original photo/plan-derived exterior miniature, millimetres. No third-party mesh.
Datum: +X southeast short end; -X northwest end; -Y southwest long side.
Published 2021/2022 photos and architect-supplied plans; not an as-built survey.
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
def xy(poly,z,h):return CrossSection([poly]).extrude(h).translate((0,0,z))
def profile_x(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
# Low bounding plinth. Terrain is deliberately schematic, without neighboring pool.
add(0,0,0,150,104,3)
# Downhill basement: one low wing with continuous front glazing and roof terrace.
add(31,-1,2.8,67,68,9.2)
add(-37,1,2.8,67,48,9.2)
add(0,0,11.4,137,73,1.8)
# Long recesses are actual bands, not a generic array of square windows.
cut(31,-35,5,60,3,4.2)
for x in [-.5,7,14.5,22,29.5,37,52,59.5]:details.append(box(x,-34.5,4.9,1.1,3,4.4))
cut(64,2,5.2,4,33,4)
for y in [-12,-5,2,9,16]:details.append(box(64,y,5.1,4,1.1,4.2))
# Four massive cores keep the exhibition volume raised: two at each end.
for x in [-47,27]:
 for y in [-14,15]:add(x,y,12,9.5,8.5,14.2)
# Slab beneath the two suspended volumes follows the L-plan and open walkway.
foot=[(-65,-22),(22,-22),(22,-43),(65,-43),(65,22),(-65,22)]
parts.append(xy(foot,24.6,2.0))
# Main black box (northwest); outer skin is solid for printing.
add(-19.5,0,26.2,91,43,31)
# Gray box projects southeast, 5 mm taller and extends toward southwest.
add(43.5,-10.5,29,43,65,31)
# Main southwest low horizontal ribbon, one high square opening.
cut(-27,-21.5,27,53,3.5,2.5)
cut(-51,-21.5,43.5,4.7,3.5,5.2)
for x in np.linspace(-51.5,-2.5,14):details.append(box(x,-20.8,26.9,.85,1.5,2.7))
# Main northeast low ribbon; one narrow high vertical glazing slot.
cut(-27,21.5,27,53,3.5,2.5)
cut(-51,21.5,42,2.7,3.5,7.5)
# Northwest end: a single wide low glass band behind the monumental blank box.
cut(-65,0,26.8,4,32,7.2)
for y in [-12.8,-7.7,-2.6,2.6,7.7,12.8]:details.append(box(-64.8,y,26.6,4.2,1.05,7.6))
# Southeast elevation: the two offsets and dark deep corner opening visible in photos.
cut(64,1,28.8,8,23,10)
cut(64,-33.2,43.3,4.2,18.5,2.5)
for y in np.linspace(-40.7,-25.7,7):details.append(box(63,y,43.2,4.1,.95,2.7))
# The ribbon turns the southwest corner only partway; no invented stacked windows.
cut(54,-43,43.3,22,3.4,2.5)
for x in [45.5,49.7,54,58.3,62.5]:details.append(box(x,-41.6,43.2,.95,3,2.7))
# Subtle horizontal overlaps in the metal skin, at unequal heights.
cut(65,-3,49,1.8,49,.6)
cut(47,-43,48.6,35,1.6,.6)
# Northeast translucent screen: three recessed bands seen through the expansion mesh.
for z in [36,46,55]:cut(49,22,z,23,1.5,2.3)
# Supported vertical panel divisions, shallow and backed, not freely hanging fins.
for y in [-38,-26,-14,-2,10]:cut(65.1,y,31,.4,.3,28.4)
for x in [29,41,53]:cut(x,-43.1,31,.3,.4,28.4)
# Roof: low parapets, main and gray roofs retain independent levels.
for x,y,w,d,z in [(-19.5,0,91,43,56.6),(43.5,-10.5,43,65,59.4)]:
 rim=box(x,y,z,w,d,1.7)-box(x,y,z+.01,w-2.8,d-2.8,2)
 parts.append(rim)
# Two roof access housings from roof plan/sections, coarse plant mass only.
add(-46,2,57.1,8,15,5)
add(26,5,60,14,18,4)
add(39,8,60,7,9,2)
# Open southeast balcony and southwest walkway rail; 1.2 mm rails fuse to slab.
# Railing is a solid low strip at this scale (actual infill mesh not reproduced).
add(43.5,-42.7,26.3,43,1.4,2.7)
add(64.2,-11,26.3,1.4,64,2.7)
# Outdoor stair behind gray screen descends to corner platform; tread count simplified.
for i in range(13):add(36.0,-35.5+i*1.7,13,9,1.95,(i+1)*.9)
# Central broad stair connects lower terrace to raised plaza, per entrance photo.
for i in range(10):add(-9,-29+i*1.55,3,12,1.8,(i+1)*.95)
# Open ground passage remains between four principal supports.
# Soffit crossing beams visible in the undercroft; no extra vertical supports.
for x in [-56,-35,-14,7,28,49]:add(x,0,23.4,1.6,44,1.4)
for y in [-13,0,13]:add(-19.5,y,23.4,91,1.6,1.4)
# Glazed lower stair/elevator shaft on the downhill side.
add(44,-27,2.8,6,7,23)
cut(44,-34.5,4,3.4,10,18)
for z in [10,17]:details.append(box(44,-30,z,3.5,2.7,1))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1,[(p.volume(),p.bounding_box()) for p in solid.decompose()]
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('dimensions_mm',mesh.extents,'watertight',mesh.is_watertight,'volume',mesh.volume)
