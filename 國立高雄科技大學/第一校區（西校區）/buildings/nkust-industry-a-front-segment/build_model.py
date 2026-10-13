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
# Main photographed facade only. Front=-Y; rear is a plain truncation.
# Official A-wing evacuation plan confirms the long bar / right entrance relationship.
add(0,0,0,150,70,3)
add(0,2,2.8,134,44,72.2)
# Three deeply recessed left galleries. Their right end steps eastward with height.
for x,w,z in [(-35,60,25),(-32.5,65,42),(-30,70,59)]:
 cut(x,-18,z,w,18,12.8)
 # Rooted solid lower parapet and robust transparent-rail approximation.
 add(x,-24.3,z-.7,w+2,2.2,3.8)
 for px in [x-w*.43,x-w*.22,x,x+w*.22,x+w*.43]:add(px,-24.3,z+2.9,1.25,2.2,2.6)
 add(x,-24.3,z+5.0,w+2,1.5,1.3)
 # Door/window group is set back behind each deep gallery.
 for px in [x-w*.32,x,x+w*.31]:cut(px,-8.8,z+2.0,7.4,2.2,8.1)
# These floor ledges and rails are added after the recess cuts, physically joined to the rear slab.
for x,w,z in [(-35,60,25),(-32.5,65,42),(-30,70,59)]:
 details.append(box(x,-16.5,z-1.5,w+2,18.0,1.8))
 details.append(box(x,-24.3,z-.3,w+2,2.2,3.4))
 for px in [x-w*.43,x-w*.22,x,x+w*.22,x+w*.43]:details.append(box(px,-24.3,z+2.9,1.25,2.2,2.6))
 details.append(box(x,-24.3,z+5.0,w+2,1.5,1.3))
# Distinctive sloped red frame around the lowest balcony (a real thick ring).
details.append(profile([(-68,23),(-63.5,40.5),(1.2,40.5),(-4.0,23)],-23.9,3.2)-profile([(-63.6,27),(-60.9,37.6),(-3.1,37.6),(-6.3,27)],-23.9,4.1))
# The long diagonal dividing blade continues down to the ground.
parts.append(profile([(-24,2.8),(-18,2.8),(4.5,41),(-1.5,41)],-22.2,3.4))
# Lower left glazed hall: two glass tiers, unequal edge lights.
for a,b in [(-62,-55),(-53.6,-45),(-43.6,-35),(-33.6,-25)]:
 for z,h in [(4.3,11.0),(16.7,5.5)]:cut((a+b)/2,-20.2,z,b-a,2.5,h)
# Right ground/second-storey glazed wedge is a continuous panel field.
recess_poly([(-12,4.2),(65,4.2),(65,40.5),(8.5,40.5)],-20.1,2.8)
# Glazing mullions are rooted to the recess back and remain stout at 150 mm.
for x in [-4,7,18,29,40,51,62]:
 z0=4.2;z1=min(40.7,4.2+(x+12)*36.3/20.5)
 if z1>z0:details.append(box(x,-19.2,z0,1.25,1.4,z1-z0))
for z in [15.7,28.1]:details.append(box(28,-19.2,z,76,1.4,1.25))
# Opaque central spine: its tall narrow lights do not extend across the glass wedge.
for x,z,h in [(-14.8,7,12),(-11.3,9,13),(-7.8,13,11),(-4.3,28,10),(-.8,30,8),(2.7,32,6)]:cut(x,-20.2,z,1.55,2.4,h)
# Upper right vertical-light groups; larger masonry breaks between each group.
# Two clear upper rows only, not four rows of generic square windows.
for z in [45.2,62.2]:
 for group in [[6.0,9.0,12.0],[18.5,21.5,24.5],[31,34,37],[43.5,46.5,49.5],[58,61]]:
  for x in group:cut(x,-20.2,z,1.65,2.5,9.2)
# Top canopy sits above a recessed terrace, with the right solid corner core.
cut(0,-8,72.8,127,29,5.0)
add(0,1,78,138,48,2.3)
for x in [-61,-30,1,32,63]:add(x,9,72,2.0,6,7.2)
add(61,6,72.0,9,28,7)
# Right glazed return and separate solid upper gable, confirmed by architect oblique view.
for y in [-13,-4,5]:
 for z,h in [(4.2,11),(16.7,11),(29.2,11)]:cut(67.1,y,z,2.4,7.7,h)
cut(67.1,-8,45.2,2.4,2.3,9.2)
# Entry canopy is attached to facade; cables and wire rails are omitted.
add(32,-25,27.4,72,12,1.7)
for i in range(3):add(39,-30+i*1.8,2.8,35,2,.55*(i+1))
# Left end lower service door observed in the completed photograph.
cut(-67.1,-4,4.2,2.5,6,10.5)
# No invented fenestration is applied on the unobserved rear cap.

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
