"""Huai En Hall: historical circa-2021 exterior massing, before 2024 solar.
Original parametric geometry, with 1983 drawing infill and 2023 roof dimensions.
All source coordinates below are metre-like architectural estimates. Final STL is mm.
Front/south is -Y. Do not silently reinterpret this as a 2026/current survey.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
SCALE=1.30  # millimetres per source metre, approximately 1:769.23
BASE_Z=1.8
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def sideprofile(poly,x,width):
 # input is (Y,Z), extrusion along X.
 return CrossSection([poly]).extrude(width).rotate((90,0,90)).translate((x-width/2,0,0))
def arch(x,y,z,w,h,depth):
 r=w/2; spring=z+h-r
 pts=[(x-r,z),(x+r,z),(x+r,spring)]
 pts += [(x+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,25)[1:]]
 return profile(pts,y,depth)
# H2 roof outer rectangle 106.52 x 12.09 m; H1 axis chain 105.50 m.
# H1 4.0m between floors; 3.5m upper storey to eave. No false precise survey.
# Solid room bar behind a genuinely open south arcade.
add(0,1.57,0,105.7,8.95,7.55)
# Lower and upper arcade floors: ~0.9 mm robust simplified slabs at final size.
add(0,-4.46,0,106.0,3.55,.70)
add(0,-4.46,3.55,106.0,3.55,.72)
# The long outer wall is opened into 12 left / 9 right arches on BOTH levels.
add(0,-5.70,0,106.0,.90,7.65)
left_centers=np.linspace(-52.75+44/24,-8.75-44/24,12)
right_centers=np.linspace(19.75+33/18,52.75-33/18,9)
for x in list(left_centers)+list(right_centers):
 cuts.append(arch(float(x),-5.73,.62,2.68,2.84,1.20))
 cuts.append(arch(float(x),-5.73,4.92,2.68,2.28,1.20))
# Two broad rectangular bays flank the projecting entrance; do not count as arches.
for x in [-5.25,16.25]:
 cut(x,-5.73,.62,5.35,1.20,2.84)
 cut(x,-5.73,5.15,5.35,1.20,1.95)
# Walkway end closures and cross ties remain robust; arcade void depth is real.
for x in [-52.45,52.45]:add(x,-4.44,0,1.1,3.70,7.65)
# H1 main roof is very low-pitched double slope, not a single flat plate.
# A 0.9m flattened crest is a declared printable simplification, not a measured ridge.
parts.append(sideprofile([(-2.9,7.42),(6.045,7.42),(6.045,7.92),(1.98,8.20),(1.08,8.20),(-2.9,7.92)],0,106.52))
# Lowered south corridor roof and raised outer fascia reproduce the end section.
add(0,-4.45,7.10,106.52,3.20,.70)
add(0,-5.73,7.00,106.52,.90,.93)
# Rear eave: attached fascia; avoids a delicate detached roof rim.
add(0,5.92,7.25,106.52,.85,.67)
# Rear 2021-photo-based broader window groups, with old drawing used only for rhythm.
# Front x coordinates; north elevation will read reversed left/right in a rear view.
rear_groups=[(-46.75,7.1),(-35.75,7.1),(-24.75,7.1),(-13.75,7.1),(25.25,7.1),(36.25,7.1),(47.25,7.1)]
for x,w in rear_groups:
 # 2021 visible second-storey band is simplified into two broad recessed panes.
 for dx in [-1.87,1.87]:cut(x+dx,6.03,4.82,3.30,.80,2.18)
 # 1F obscured in 2021: H1 four-window grouping reduced to two backed relief bays.
 for dx in [-1.87,1.87]:cut(x+dx,6.03,1.15,3.30,.72,1.92)
# Three broad clerestory groups over the central passage, visible in H1/H4.
for x,w in [(-.10,4.1),(5.5,4.8),(11.1,4.1)]:cut(x,6.03,4.92,w,.80,2.08)
# Major back pilasters/vertical divisions, not small window mullions.
for x in [-51.1,-42.4,-40.9,-31.4,-29.9,-20.4,-18.9,-9.4,-2.1,2.4,8.6,13.1,19.75,29.5,31.0,40.5,42.0,51.7]:
 add(x,6.00,0,.80,.55,7.42)
# H1 offset entrance 7..10 axes, center +5.50m from geometric midpoint.
PORTICO_X=5.5
add(PORTICO_X,-5.66,0,14.5,6.32,7.92)
# Large central and two narrow side portals retain depth rather than flat dark marks.
cuts.append(arch(PORTICO_X,-6.9,.20,3.10,3.16,8.0))
for x in [.30,10.70]:cuts.append(arch(x,-6.8,.55,1.82,2.86,5.6))
# Central through-passage links the south door to the north arch in H1.
cuts.append(arch(PORTICO_X,1.30,.20,3.10,3.16,13.8))
# Narrow backed vertical upper windows in the central block: approximate H1 infill.
# No fine 1983 frame bars are claimed to describe 2021.
for x in [-.8,2.1,8.9,11.8]:cut(x,-8.87,5.12,.90,.92,1.92)
cut(PORTICO_X,-8.87,5.06,2.25,.92,2.0)
# One-storey forward porch and attached balcony/parapet; photograph confirms arch type.
add(PORTICO_X,-9.27,0,5.50,3.12,3.96)
cuts.append(arch(PORTICO_X,-9.30,.20,3.1,3.16,4.0))
# Robust balcony parapet is plain, not invented balustrade rods.
add(PORTICO_X,-10.40,3.90,5.5,.85,.83)
for x in [PORTICO_X-2.32,PORTICO_X+2.32]:add(x,-9.22,3.90,.85,3.15,.83)
# Front portico coping.
add(PORTICO_X,-6.80,7.36,14.7,4.48,.71)
# End staircases from H1 only: mirrored across X, risers rise toward south landing.
# Tread/riser detail is purposefully coarsened; each outer rail is >=1.1 mm wide.
for sign in [-1,1]:
 x=sign*53.80
 for i in range(10):
  # Broad solid steps rise north(+Y) to south(-Y).
  y=3.18-i*.66
  add(x,y,0,1.95,.75,.40*(i+1))
 add(x,-3.60,0,2.0,1.50,4.0)
 # Outer solid diagonal balustrade; the open space above the stair remains air.
 rail_x=sign*54.44
 parts.append(sideprofile([(3.58,0),(3.58,.98),(-3.26,5.12),(-4.34,5.12),(-4.34,0)],rail_x,.86))
 # Short landing guard, with no unsupported fine rail rods.
 add(x,-4.17,4.0,1.98,.86,1.12)
 # Backed upper doorway above the rail and small stair-wall window, H1 infill only.
 # Shallow relief preserves >=0.8mm material in every exposed end-wall connection.
 cut(sign*53.18,-3.45,5.13,.70,1.75,1.65)
 cut(sign*55.00,1.05,.86,.60,.92,.74)
# Fused entrance steps kept broad enough to resolve at the chosen miniature scale.
for i in range(3):add(PORTICO_X,-11.12+i*.45,0,5.75,.60,.15*(i+1))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
solid=solid.scale((SCALE,SCALE,SCALE)).translate((0,0,BASE_Z-.02))
solid=solid+box(0,-2.5,0,150,29,BASE_Z)
assert len(solid.decompose())==1, 'Disconnected solids are forbidden'
m=solid.simplify(.000001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.volume>0
mesh.export(OUT/'model.stl')
print('actual_STL_mm',mesh.extents.tolist(),'triangles',len(mesh.faces),'volume',mesh.volume)
