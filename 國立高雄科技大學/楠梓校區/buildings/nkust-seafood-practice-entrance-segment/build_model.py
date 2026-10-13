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
# Photo-supported south long facade, western perforated entrance screen and east stair tower.
# Official evacuation plan labels 1/2/3/R: roof is not a fourth office floor.
# The northern parallel laboratory wing, full inner corridor and unseen rear are excluded.
# Front is -Y, west is -X. Rear is a plain local truncation.
add(0,0,0,150,84,3)
add(10,1,2.8,87,37,64.2)
# Five principal openings on each of THREE real window tiers, with robust main piers.
# Perspective foreshortening is not interpreted as five different physical bay widths.
centres=[-24,-7,10,27,44]
for x in centres:
 # Low-level window is partly screened by the roller-shutter field above.
 cut(x,-17.7,9.5,12.6,2.7,14.0)
 details.append(box(x,-17.1,18.5,12.6,1.8,5.0))
 for xx in [x-4.2,x,x+4.2]:details.append(box(xx,-17.0,9.5,1.1,2.0,9.1))
 # Middle floor: large glass lights below a transom, not two separate floors.
 cut(x,-17.7,30,12.6,3.1,14.5)
 details.append(box(x,-17.8,39.9,12.7,2.2,1.4))
 for xx in [x-4.2,x,x+4.2]:details.append(box(xx,-17.0,30,1.1,2.0,9.9))
 # The top floor has deep projecting rectangular frames and a clear horizontal transom.
 cut(x,-17.7,51,13.0,5.3,13.5)
 details.append(box(x,-18.7,60.2,13.1,3.0,1.4))
 for xx in [x-4.1,x+.4,x+4.5]:details.append(box(xx,-16.0,51,1.1,2.5,9.3))
# Upper primary white frame: six piers and the thick roof fascia.
for x in [-32.2,-15.5,1.5,18.5,35.5,52.2]:add(x,-19.1,48.1,2.4,5.6,19.7)
add(10,-18.4,65.5,88,6,3.0)
# Broad continuous horizontal canopy between the lower two levels.
add(10,-20.3,25.8,88,8,2.0)
# Narrow, full-height louver/service strip separates the entry void from the long window field.
add(-36,-18.8,3,5.2,6.0,66.8)
for z in [5+i*2.5 for i in range(26)]:cut(-36,-22.0,z,3.4,1.5,1.15)
# Open western entrance bay, vertically continuous apart from two partial landing ledges.
# Its rear service wall is grounded and the broad void is kept genuinely open.
add(-47,17,2.8,26,5,65.5)
for z in [25.5,46.1]:
 parts.append(CrossSection([[(-60.32,-21),(-33.2,-21),(-33.2,19),(-51.52,19)]]).extrude(2.1).translate((0,0,z)))
 add(-48,-20.7,z+1.4,23,1.7,3.0)
 for x in [-58,-51,-44,-37.5]:add(x,-20.7,z+4.1,1.3,1.7,2.4)
 add(-48,-20.7,z+5.7,23,1.5,1.3)
# Full entrance roof bridges the screen and service strip.
add(-48,-1,66.3,27.5,41,2.8)
# West oblique perforated concrete screen. It is a real open screen rather than embossed diamonds.
# Local horizontal direction follows global Y; x=-57+.22*y follows the slanted plan edge.
def screen_transform(m):
 return m.rotate((0,0,90)).transform(np.array([[1,.22,0,-57],[0,1,0,0],[0,0,1,0]],dtype=float))
screen=profile([(-27,2.8),(20,2.8),(20,69),(-27,69)],0,3.0)
# Two explicitly arranged asymmetric diamond clusters; lettering and tile grooves omitted.
# Large openings preserve their size difference from the small diamond lights.
for u,z,r in [(-11,48,5.8),(-8,18,5.8),(-19,52,1.7),(-16,57,1.7),(-10,59,1.7),(-5,57,1.7),(-2,52,1.7),(-17,47,1.7),(-20,43,1.7),(-14,40,1.7),(-7,37,1.7),(-18,21,1.7),(-15,27,1.7),(-10,31,1.7),(-4,26,1.7),(0,22,1.7),(-2,13,1.7),(-9,8,1.7),(-16,9,1.7),(-20,14,1.7)]:
 screen=screen-profile([(u-r,z),(u,z-r),(u+r,z),(u,z+r)],0,5)
# A large entry door is left at the rearward end of the screen, observed in the entry photo.
screen=screen-profile([(2,3),(16,3),(16,24),(2,24)],0,5)
parts.append(screen_transform(screen))
# Small entrance canopy and jamb connect to the screen at its doorway.
parts.append(screen_transform(profile([(0,23),(18,23),(18,25),(0,25)],-2.8,8.5)))
# West rear stair/machine core has its own higher setback and circular light.
add(-42,10,67.4,18,16,14.7)
add(-42,10,81.2,20,18,2.0)
# Visible west-facing circular light is a shallow recess; inner room not reconstructed.
q=cyl(0,0,0,3.0,3.2,64).rotate((0,90,0)).translate((-52.2,10,74.7));cuts.append(q)
# Higher east stair tower, with seven unequal glazing/landing tiers. These are NOT seven office floors.
add(61,-8,2.8,14,22,80.2)
for z,h in [(3.6,10.1),(15.1,11.1),(27.6,11.6),(40.6,5.3),(47.3,11.6),(60.3,5.3),(67.0,11.6)]:
 cut(61,-19.2,z,12.0,2.8,h)
 cut(68.2,-9,z,2.8,18.1,h)
 for x in [57.6,64.4]:details.append(box(x,-18.7,z,1.1,1.7,h))
 details.append(box(67.5,-9,z,1.7,1.1,h))
 add(61,-8,z+h-.1,16,24,1.4)
# Tower's tall rear plate and upper ventilation field remain visible above main roof.
add(68,10,2.8,2.6,20,83.2)
for z in [80.0,81.5,83.0]:cut(61,-19.2,z,11.0,2.3,.85)
# Circle on the outer east plate as in the source. It is embossed by recess, not a through cavity.
q=cyl(0,0,0,4.2,2.3,80).rotate((0,90,0)).translate((67.6,10,77.1));cuts.append(q)
# Small circular vents puncture the outer solid stair plate; positions approximated.
for y,z in [(8,16),(13,18),(7,37),(12,40),(7,61),(12,64)]:
 cuts.append(cyl(0,0,0,.85,2.5,40).rotate((0,90,0)).translate((67.6,y,z)))
# Rooted roof parapet rail along the exposed long side. Simplified and thickened for miniature scale.
for x in [-58,-46,-33,-20,-7,6,19,32,45,54]:add(x,-18.0,68.0,1.35,1.8,4.7)
for z in [69.0,71.4]:add(-2,-18,z,116,1.8,1.3)
# West screen top rail follows the plan obliqueness and is tied to the screen.
for z in [69.8,72.0]:parts.append(screen_transform(profile([(-27,z),(20,z),(20,z+1.3),(-27,z+1.3)],0,1.7)))
for u in [-26,-14,-2,10,19]:parts.append(screen_transform(profile([(u-.65,68.3),(u+.65,68.3),(u+.65,73.0),(u-.65,73.0)],0,1.7)))
# Main roof is open flat mass within this partial south/entry section; plant and northern wing omitted.

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
