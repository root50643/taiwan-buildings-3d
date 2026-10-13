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
# Observed entrance band only, front=-Y. Unseen auditorium roof/rear omitted.
add(0,0,0,150,105,3)
# Upper hall facade over a genuine sheltered entrance void.
add(0,11,2.8,132,35,50.2)
add(0,-16,22,132,24,31)
# Deep upper window ribbon with rhythmic outward-folding sunshade blades.
cut(0,-26,28,116,13,19)
for x in np.linspace(-55,55,17):
 # Thickness 2 mm; angular depth changes through the blade height.
 yz=[(-20,27.8),(-28.2,27.8),(-33.5,37.5),(-28.2,47.2),(-20,47.2)]
 # CrossSection XY -> YZ, extruded in X; solid attaches to inset backing.
 blade=CrossSection([yz]).extrude(2.0).rotate((90,0,90)).translate((x+1,0,0))
 # Explicit coordinate mesh is less ambiguous than transformed profiles.
 verts=[]
 for xx in [x-1,x+1]:verts += [[xx,y,z] for y,z in yz]
 faces=[];n=len(yz)
 for i in range(1,n-1):faces += [[0,i+1,i],[n,n+i,n+i+1]]
 for i in range(n):j=(i+1)%n;faces += [[i,j,n+j],[i,n+j,n+i]]
 import manifold3d as md
 details.append(Manifold(md.Mesh64(np.array(verts,dtype=float),np.array(faces,dtype=np.uint64)[:,::-1])))
# Glazing strips behind each sunshade, recessed into the backing.
for x in np.linspace(-51.5,51.5,16):cut(x,-19.1,29,3.7,2.1,16.4)
# Sheltered entrance stair and tall structural piers.
add(0,-7,2.8,130,16,5.6)
for x in [-55,-18.5,18.5,55]:add(x,-23,8.0,2.8,2.8,14.4)
# Rear doors of the open entrance porch.
for x in [-42,-21,0,21,42]:cut(x,-6.7,9,14,2.0,10.8)
for i in range(8):add(0,-48+i*3.0,2.8,109,3.3,.7*(i+1))
# Documented solid left flank with a shallow ground-level grille.
cut(-66,4,6,2.2,14,9)
# Back is a declared study cutoff, not an invented full building elevation.

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
