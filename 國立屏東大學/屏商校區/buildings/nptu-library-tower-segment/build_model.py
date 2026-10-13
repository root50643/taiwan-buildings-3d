"""Original photo-derived NPTU exterior miniature. Units: mm.
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
# Front=-Y. Main tower and observed low entrance/side podium only.
# 12-storey tower: the deep multi-storey open recess is essential.
add(0,0,0,150,124,3)
add(0,5,2.8,94,62,132)
cut(0,-25,35.5,31,56,63.5)
# Eight clearly exposed square-window rows above the low podium.
# Source front: 2 full 12-bay rows, then 6 rows of 4+4 bays beside the deep recess.
for z in [39.5,50,60.5,71,81.5,92,102.5,113]:
 for x in np.linspace(-42.9,42.9,12):
  if z<99 and abs(x)<15.6:continue
  cut(x,-26.2,z,5.2,2.8,6.3)
# Five horizontal glazing ribbons and the lower screened band inside the recess.
for z in [44,54.5,65,75.5,86]:
 cut(0,2.2,z,28,2.4,5.4)
 for x in [-15.7,15.7]:cut(x,-11.5,z,2.2,26,5.4)
cut(0,2.2,36.8,28,2.4,5.4)
# The left elevation is documented by an oblique official photograph.
for z in [8,18.5,29,39.5,50,60.5,71,81.5,92,102.5,113]:
 for y in [-18,-8,2,12,22,30]:cut(-47,y,z,2.7,6.0,6.3)
# Blue-glazed top storey: use broad grouped recesses and robust mullions.
for x in np.linspace(-38.5,38.5,6):cut(x,-26,123.3,13.4,3.0,8.1)
for y in [-17,-1,15,29]:cut(-47,y,123.3,3.0,13.6,8.1)
add(0,5,134.2,95.6,63.6,1.7)
# Source front low podium hides the lower tower storeys: do not invent exposed rows.
add(7,-30.5,2.8,112,19,31.2)
add(7,-30.5,33.4,113.4,20.5,1.7)
# Low podium glazing is simplified where vegetation conceals detailed mullions.
for x in [-37,-22,-7,8,23,38,53]:cut(x,-40.2,7,10.3,2.6,17)
# Documented smaller entrance canopy projects ahead of the podium at the left.
add(-35,-46,2.8,22,17,10.6)
add(-35,-47,13,24,21,2.2)
cut(-35,-53.5,3.3,15,10,9.8)
for x in [-44,-26]:add(x,-55,2.8,2.4,2.4,10.7)
for i in range(4):add(-35,-60+i*2,2.8,24,2.3,.65*(i+1))
# Unobserved rear/right elevations are plain. No mirrored facade invented.

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
