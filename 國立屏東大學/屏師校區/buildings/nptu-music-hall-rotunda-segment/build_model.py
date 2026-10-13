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
# Circular entrance volume only; the adjoining teaching wings are outside scope.
add(0,0,0,150,125,3)
parts.append(cyl(0,-3,2.8,44,65))
# Photograph shows tall glazing between white ribs, and a broad central sign wall.
# Narrow-depth sector cuts preserve the cylindrical mass and round silhouette.
for a in [-168,-151,-134,-117,-63,-46,-29,-12,5]:
 # Leave 1.2 mm bands in the original solid instead of adding coincident rings.
 for z,h in [(7,13),(21.2,12.8),(35.2,12.8),(49.2,12.8)]:
  cuts.append(sector(41.7,47,a-6.5,a+6.5,z,h).translate((0,-3,0)))
# Tall external white ribs and flared capitals are visibly separated from glazing.
for a in [-178,-160,-143,-126,-109,-71,-54,-37,-20,-3,14]:
 t=math.radians(a);x=44.4*math.cos(t);y=-3+44.4*math.sin(t)
 rib=box(0,0,4.8,2.2,3.5,59).rotate((0,0,a-90)).translate((x,y,0));details.append(rib)
 cap=box(0,0,62.8,3.4,5.3,3.8).rotate((0,0,a-90)).translate((x,y,0));details.append(cap)
parts.append(cyl(0,-3,65.8,47.2,3.2))
# Curved low front plinth attaches to base; no loose landscape pieces.
parts.append(cyl(0,-3,2.8,48.5,2.4))
# Short joining stub and the visible pink vertical service tower.
add(-33,29,2.8,18,26,75)
add(-13,37,2.8,36,19,63)
for z in [12,28,44,60]:cut(-42,29,z,2.3,10,10)
# Unseen northern/back side intentionally plain; all omitted wing limits documented.

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
