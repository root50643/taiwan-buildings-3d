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
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def gable(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x,z+h)],y,d))
def paired_front(x,y,z,w=4.8,h=4.6):
 for dx in [-w/4,w/4]:cut(x+dx,y,z,w/2-.65,2.4,h)
def band_front(x,y,z,w,h,n):
 for i in range(n):cut(x-w/2+(i+.5)*w/n,y,z,w/n-1.0,2.4,h)
# One small building photographed from porch/gable and opposite gable/rear angles.
# The gallery's centre / kennel / classroom labels describe this same documented body.
add(0,0,0,150,118,3)
add(0,0,2.8,110,52,28.2)
# Red-brick plinth is an integrated shallow belt.
add(0,0,2.8,111,53,7)
# Main pitched roof, ridge along X. The roof is deliberately solid inside.
yz=[(-29,30.3),(29,30.3),(0,49)]
parts.append(CrossSection([yz]).extrude(115).rotate((90,0,90)).translate((-57.5,0,0)))
# Wide eaves and a robust ridge cap.
add(0,0,48.4,116,1.8,1.4)
# Long front veranda: lean-to canopy with visible 4-post rhythm.
parts.append(CrossSection([[(-46,25.3),(-25,30.3),(-25,32),(-46,27)]]).extrude(115).rotate((90,0,90)).translate((-57.5,0,0)))
add(0,-36,2.8,115,23,1.8)
for x in [-52,-18,18,52]:add(x,-44,4.3,2.8,2.8,22.2)
# Front door and photographed tall window groups, set back under the veranda.
cut(-16,-26,4.6,9.2,2.8,18)
for x in [-39,10,37]:
 for dx in [-2.25,2.25]:cut(x+dx,-26,11.3,3.3,2.6,11.2)
# The right gable has a central door plus two low horizontal windows.
cut(55,0,4.5,2.8,9.2,18.5)
for y in [-17,17]:cut(55,y,17,2.8,8.2,5.5)
# Rear lean-to strip seen behind the fenced service area.
add(0,31,2.8,110,12,22.5)
parts.append(CrossSection([[(25,25),(39,22.0),(39,23.6),(25,26.8)]]).extrude(114).rotate((90,0,90)).translate((-57,0,0)))
# The opposite end wall is not securely identified by these photos; leave it plain.
# Rear has small high windows visible above the service fence; no copied tall front fenestration.
for x in [-33,2,34]:cut(x,37,15.2,7.4,2.7,4.8)
# Clapboard courses are shallow engravings, preserving the distinctive long horizontal siding.
for z in [10.8,13.5,16.2,18.9,21.6,24.3,27.0,29.7]:
 cut(0,-26,z,109,0.55,.35)
 for side in [-1,1]:cut(side*55,0,z,.55,51,.35)
for z in [10.8,13.5,16.2,18.9,21.6]:cut(0,37,z,109,.55,.35)
# Roof-edge protection has actual thickness; no wire fence or thin downpipe meshes.
add(0,-46,25.2,115,1.3,1.4)
for i in range(3):add(-16,-52+i*1.6,2.8,19,1.9,.5*(i+1))

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
