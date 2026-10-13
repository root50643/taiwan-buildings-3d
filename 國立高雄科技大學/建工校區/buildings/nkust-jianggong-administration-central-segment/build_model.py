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
# Photographed central curved portico segment only, not the complete administration bar.
# Official 2024 evacuation plan has seven floors; the central projecting facade has
# FIVE glazed bands (floors 3–7), above the double-height portico. Side stubs have seven.
# Main front is -Y; the rear is a deliberate segment cut, not an invented facade.
from math import sin,cos,pi

def half_round(radius,z,height):
 return cyl(0,0,z,radius,height,160)^box(0,-radius/2,z-.1,2*radius+2,radius+0.02,height+.2)
def arc_window(radius,z,h):
 # Recess the continuous glass band, leaving a solid glass proxy rooted to the body.
 ring=cyl(0,0,z,radius+2,h,160)-cyl(0,0,z-.1,radius-1.6,h+.2,160)
 return ring^box(0,-radius/2,z-.1,2*radius+5,radius+.1,h+.2)
def radial_bar(radius,ang,z,h,width=.98):
 # Robust rooted mullion, tangential width is an approximation of the dense real glazing.
 q=box(0,0,z,width,2.0,h).rotate((0,0,ang*180/pi+90))
 return q.translate((radius*cos(ang),radius*sin(ang),0))
add(0,0,0,150,94,3)
# Adjacent facade stubs are truncated after two primary bays per side.
for x in [-53,53]:
 add(x,13,2.8,34,28,112.2)
 # Seven window rows on the attached office wings, unlike the central five-row curve.
 for z,h in [(5,10),(19,10),(35,10.5),(51,10.5),(67,10.5),(83,10.5),(103,10.5)]:
  for a,b in [(x-14.1,x-1.4),(x+1.4,x+14.1)]:
   cut((a+b)/2,-1.2,z,b-a,3.0,h)
   for xx in [a+(b-a)/3,a+2*(b-a)/3]:details.append(box(xx,-.4,z,1.05,1.8,h))
 # Primary columns read as structural bays; mullions are separate elements.
 for xx in [x-16,x,x+16]:add(xx,-2,2.8,2.5,3.0,112)
 add(x,12,114,35,29.5,2.5)
# Central suspended solid, with a flat rear cut and deep double-height entrance below.
parts.append(half_round(36,31,68))
add(0,13,31,72,27,68)
# Four lower round glazing bands, with deep horizontal solid spandrels between.
for z in [35,51,67,83]:
 cuts.append(arc_window(36,z,10.7))
 # Thin real window frames are deliberately thickened, not represented as open holes.
 for a in [pi+pi*i/30 for i in range(31)]:details.append(radial_bar(35.5,a,z,10.7))
 # Window transom follows the continuous cylindrical band.
 details.append((cyl(0,0,z+7.4,36.1,1.05,160)-cyl(0,0,z+7.3,34.6,1.25,160))^box(0,-20,z+7.3,80,40,1.25))
# Top floor widens and projects: horizontal radius AND height change are explicit.
parts.append(half_round(40,99,22.2));add(0,13,99,80,27,22.2)
cuts.append(arc_window(40,103,10.7))
for a in [pi+pi*i/34 for i in range(35)]:details.append(radial_bar(39.5,a,103,10.7))
details.append((cyl(0,0,110.4,40.1,1.05,160)-cyl(0,0,110.3,38.6,1.25,160))^box(0,-21,110.3,84,42,1.25))
# Five main front posts observed in the official front and shuttle photographs.
for a in [pi,pi*1.25,pi*1.5,pi*1.75,pi*2]:
 details.append(cyl(33.0*cos(a),33.0*sin(a),3,2.3,28.4,64))
# The rear portico is open to the cut, with two rooted side piers; no fictional back windows.
for x in [-34,34]:add(x,15,2.8,4,24,29.0)
# Shallow fan steps express the entrance threshold without inventing the full plaza.
for r,z,h in [(39.6,3,0.65),(37.6,3.6,.65),(35.6,4.2,.65)]:
 parts.append(half_round(r,z,h))
 # trim is intentionally a solid plinth; actual handrails and entrance text omitted.
# Small radial supports under the projecting top level are visible in the front photo.
for a in [pi*1.08,pi*1.29,pi*1.5,pi*1.71,pi*1.92]:
 details.append(radial_bar(36.4,a,96.5,3.1,1.4))
# Roof is a plain cap within this local segment; full atrium skylight and wings excluded.

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
