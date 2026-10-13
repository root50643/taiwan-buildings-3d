"""NTSU photo-derived exterior section, self-built geometry in millimetres.
Unknown back and omitted building extents are plain section cuts, not surveyed facades.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
P=[];C=[];D=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):P.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):C.append(box(x,y,z,w,d,h))
def cyl(x,y,z,r,h):P.append(Manifold.cylinder(h,r,r,circular_segments=32).translate((x,y,z)))
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def arc_strip(ro,ri,cy,z,h,span=42):
 a=np.linspace(-math.radians(span),math.radians(span),65)
 poly=[(ro*math.sin(t),cy-ro*math.cos(t)) for t in a]+[(ri*math.sin(t),cy-ri*math.cos(t)) for t in a[::-1]]
 return CrossSection([poly]).extrude(h).translate((0,0,z))

# Central gabled entry pavilion plus one visible window on each side; not full tennis halls.
add(0,0,0,150,96,3)
# Short flanking wall sections, all rear cuts plain.
add(-44,18,2.8,49,23,43)
add(44,18,2.8,49,23,43)
add(0,20,2.8,42,20,43)
# Deep entrance directly behind the freestanding front portal.
cut(0,9,7,25,10,29)
for x in [-36,36]:
 cut(x,6.5,9,15,4,24)
 D.append(box(x,8.1,29,15,1.4,1.5))
 D.append(box(x,8.1,9,1.6,1.4,24))
# Tall paired entrance piers and rear pair physically support the open gabled canopy.
for x in [-19,19]:
 for y in [-9,15]:add(x,y,2.8,7,7,65)
# Lower horizontal sign band, rendered unlettered; walkway underneath remains open.
add(0,-9,38,45,8,9)
# Top horizontal roof support and central truss; all bars >=2.4mm.
add(0,-9,65,46,4,3)
add(0,15,65,46,4,3)
for y in [-9,15]:
 add(0,y,66.5,2.8,3.0,20.5)
# Eaves have 2.2mm flat-bottom fascia to avoid sub-nozzle pointed lower tips.
# True gabled roof shell with an open triangular front, not a filled triangular box.
roof=profile([(-28,66),(-.9,90.2),(.9,90.2),(28,66),(28,63.8),(25.8,63.8),(0,86.9),(-25.8,63.8),(-28,63.8)][::-1],3,37)
P.append(roof)
# Fully backed decorative pier score lines are recessed, not thin detached horizontal wire.
for x in [-19,19]:
 for z in [18,31,52,61]:cut(x,-12.5,z,7.5,1.4,.9)
# Raised threshold platform and approach accessibility ramp.
add(0,-1,2.8,35,26,4.5)
# Slope runs toward the entry, rising from z3.2 at y-41 to z7.3 at y-2.
# use an explicit XYZ mesh via manifold hull for deterministic ramp orientation
P.append(Manifold.hull_points([[-12,-42,2.8],[12,-42,2.8],[-12,-42,3.4],[12,-42,3.4],[-12,-2,2.8],[12,-2,2.8],[-12,-2,7.3],[12,-2,7.3]]))
# Railing wire is too fine at this scale: broad attached side curbs encode ramp limits.
for x in [-13.4,13.4]:
 P.append(Manifold.hull_points([[x-1,-42,2.8],[x+1,-42,2.8],[x-1,-42,5],[x+1,-42,5],[x-1,-2,2.8],[x+1,-2,2.8],[x-1,-2,9],[x+1,-2,9]]))

assert all(p.status()==Manifold().status() for p in P+C+D)
solid=P[0]
for p in P[1:]:solid=solid+p
for c in C:solid=solid-c
for d in D:solid=solid+d
assert len(solid.decompose())==1,[(p.volume(),p.bounding_box()) for p in solid.decompose()]
m=solid.simplify(.0001).to_mesh64();v=np.array(m.vert_properties,dtype=np.float32)[:,:3];v[abs(v)<.000005]=0.0
mesh=trimesh.Trimesh(v,np.array(m.tri_verts),process=True)
# Float32 source-mesh construction can collapse redundant zero-area triangles.
# Remove only zero-area construction triangles BEFORE STL export, then fail closed.
mesh.update_faces(mesh.nondegenerate_faces(height=1e-7))
assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
mesh.export(OUT/'model.stl');print(mesh.extents,len(mesh.faces),mesh.is_watertight)
