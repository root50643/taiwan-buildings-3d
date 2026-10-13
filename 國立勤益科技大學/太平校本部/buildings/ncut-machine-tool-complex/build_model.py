"""NCUT machine-tool teaching/factory complex, original photo-derived mesh, millimetres.
References: sources.json. No downloaded meshes. Dimensions are approximate, not survey data.
The teaching wings, lower factory wings and connected triangular court form ONE model.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def poly(points,z,h):
 area=sum(x1*y2-x2*y1 for (x1,y1),(x2,y2) in zip(points,points[1:]+points[:1]))
 if area<0:points=points[::-1]
 return CrossSection([points]).extrude(h).translate((0,0,z))
def profile(points,y,depth):return CrossSection([points]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def cylinder(x,y,z,rx,ry,h):return Manifold.cylinder(h,1,1,circular_segments=80).scale((rx,ry,1)).translate((x,y,z))
def wall_local(x,z,w,h,depth,angle,cx,cy,normal_offset=0):
 return box(x,normal_offset,z,w,depth,h).rotate((0,0,angle)).translate((cx,cy,0))
def curve_glass(x,y,z,w,h,depth=3):
 # Pear-like pointed glazed arch copied as an inset profile, not a fabricated opening.
 pts=[(x-w/2,z),(x+w/2,z)]
 pts.extend((x+(w/2)*(1-2*t),z+h*math.sin(math.pi*t)**.65) for t in np.linspace(0,1,41))
 return profile(pts,y,depth)
add(0,0,0,150,150,3)
# Plan traced as proportions from AHA's actual overhead photograph 003-1.jpeg.
# Teaching block is a shallow bent bar, with a lower central roof terrace.
outer=[(-64,-38),(-13,-56)]
outer += [(x,-58.5+2.5*(x/13)**2) for x in np.linspace(-13,13,13)[1:]]
outer += [(64,-38),(61,-18),(40,-27),(34,-22),(23,-28),(21,-22),(-21,-22),(-23,-28),(-34,-22),(-40,-27),(-61,-18)]
parts.append(poly(outer,2.8,42.2))
left=[(-64,-38),(-13,-56),(-8,-40),(-14,-39),(-14,-27),(-23,-28),(-34,-22),(-40,-27),(-61,-18)]
right=[(-x,y) for x,y in left[::-1]]
for p in [left,right]:parts.append(poly(p,44.8,9.2))
# Broad roof cap and solid parapets, 1.1 mm references, attached to the slabs.
for p in [left,right]:
 parts.append(poly(p,53.7,1.4))
 ring=CrossSection([p])-CrossSection([p]).offset(-1.3)
 parts.append(ring.extrude(3.8).translate((0,0,54.5)))
# Front west/east teaching elevations: five visible window rows; alternate wide/long narrow lights.
# Windows vary by row; no undifferentiated grid. Local x runs outer end to central vestibule.
patterns=[
 'NWWNWWNWWNWWNWWNW',
 'NWNWWNWWNWWNWWNWN',
 'WNWNWNWWNWWNNWNWW',
 'NWNWWNWNNWNWWNWNW',
 'WNWNNWNWWNWNWWNWW',
]
# Transform each wing facade from outer corner to inner top-plan corner.
for side in [-1,1]:
 a=np.array([side*64.,-38.]);b=np.array([side*13.,-56.]);v=b-a;L=float(np.linalg.norm(v));ang=math.degrees(math.atan2(v[1],v[0]));center=(a+b)/2
 # local +Y points inside for west, outside for east; offset handled explicitly.
 inward=1 if side==-1 else -1
 for row,pat in enumerate(patterns):
  for i,kind in enumerate(pat):
   x=-L/2+2.3+i*(L-4.6)/(len(pat)-1)
   w=1.3 if kind=='N' else 2.35
   h=6.2 if kind=='N' else 4.2
   z=5.7+row*9.0+(0 if kind=='N' else 1.0)
   cuts.append(wall_local(x,z,w,h,2.9,ang,*center,normal_offset=inward*.75))
 # Shallow top-floor shade lips, attached to the face, not floating sun blades.
 for z in [40.6,49.6]:
  details.append(wall_local(0,z,L+.3,1.0,2.3,ang,*center,normal_offset=-inward*.3))
 # Five open recesses in the high roof parapet, diminishing towards the central setback.
 for i,w in enumerate([7.0,6.3,5.6,4.9,4.2]):
  x=-L/2+5.0+i*8.4
  cuts.append(wall_local(x,55.4,w,1.65,3.5,ang,*center,normal_offset=inward*.35))
 # Side end: tall narrow light plus five recessed plant balconies behind a solid edge wall.
 # Construct openings in the corresponding west/east end plane.
 sa=np.array([side*64.,-38.]);sb=np.array([side*61.,-18.]);sv=sb-sa
 sang=math.degrees(math.atan2(sv[1],sv[0]));sc=(sa+sb)/2;sinward=side
 for j in range(5):
  z=5.5+9*j
  cuts.append(wall_local(4.3,z,8.2,6.4,5.2,sang,*sc,normal_offset=sinward*1.3))
  cuts.append(wall_local(-6.0,z+1.0,1.3,5.8,3.0,sang,*sc,normal_offset=sinward*.6))
# Inner/courtyard face: simpler small lights, stair-tower narrow slits, horizontal glazing groups.
for side in [-1,1]:
 for z in [6,15,24,33,42]:
  for x in [27,32,37,44,49,54]:
   y=(-22-(34-x)*6/11) if x<=34 else ((-27+(40-x)*5/6) if x<40 else (-18-(61-x)*9/21))
   cut(side*x,y,z,1.5 if x in [27,37] else 2.1,3,3.8)
 # Top landing blocks based on aerial photo: raised rear service towers, independent z heights.
 add(side*31,-26,53.8,12,9,8.0)
 cut(side*31,-20.7,55.4,4,2.4,5)
# Central rear lift/stair projection and roof housing, lower central terrace distinctly preserved.
add(0,-23.6,2.8,19,10,49.2)
add(0,-23.6,51.8,20,11,1.4)
for z in [7,16,25,34]:
 cut(0,-18.2,z,5.0,2.8,3.3)
 for x in [-7.0,7.0]:cut(x,-18.2,z,1.15,2.8,4.5)
for x in [-5.5,5.5]:cut(x,-18.2,46,1.1,2.8,3.0)
# North entrance: curved three-storey vestibule and arch glazing, fused to main block.
parts.append(cylinder(0,-56.2,2.8,13.0,10.5,30.5))
# A shallow sloping cap, modeled as a backed wedge cut, rather than a circular open ring.
roofcut=profile([(-15,33),(15,36),(15,42),(-15,42)],-56.2,25)
cuts.append(roofcut)
arch=curve_glass(0,-65.0,3.9,20.5,25,8)
cuts.append(arch)
# Glazed backing and mullions are physical relief; they remain joined to the rear structure.
details.append(curve_glass(0,-61.3,3.8,20.7,25.1,1.8))
for x in [-6.8,-3.4,0,3.4,6.8]:details.append(box(x,-62.2,4.0,1.0,1.1,25) ^ curve_glass(0,-62.2,4.2,19.2,23.8,2))
for z in [8,12,16,20,24]:details.append(box(0,-62.2,z,22,1.1,1.0) ^ curve_glass(0,-62.2,4.2,19.2,23.8,2))
# Solid elliptical canopy, linked to glazed backing: overhang requires support review.
parts.append(cylinder(0,-65.1,11.5,14.5,6,1.5))
# Back factory roofs and the lower connected wings form a triangular open court.
# Factory plans retain the kinked outside corners evident in the overhead source.
west=[(-64,-2),(-36,-12),(-14,58),(-48,62),(-48,47),(-52,48)]
east=[(-x,y) for x,y in west[::-1]]
for side,p in [(-1,west),(1,east)]:
 parts.append(poly(p,2.8,20.7))
 # Single shallow barrel profile across each long workshop, clipped to its asymmetric plan.
 # Full solid below roof means no artificial sealed cavity.
 axis_angle=-18 if side==-1 else 18
 # Roof surface changes from 23.5 outer eaves to 28.2 high inner barrel.
 # Two-axis wedge-like curved roof constructed by a sampled cross section and plan intersection.
 pts=[(-18,22.6),(18,22.6)]+[(x,23.2+4.4*math.cos((x/18)*math.pi/2)) for x in np.linspace(18,-18,49)]
 r=profile(pts,0,95).rotate((0,0,axis_angle)).translate((side*39,26,0))
 roofplan=CrossSection([p]).offset(1.0).extrude(35)
 parts.append(r ^ roofplan)
 # Side workshop windows: three narrow lower openings and high hood-like shades.
 for y in [6,24,43]:
  x=side*(64-(y+2)*.24)
  cut(x,y,5.3,3.1,2.0,6)
  add(x,y,12.0,3.5,2.7,1.2)
 # Large vehicle opening on south end, shallow inset with thick pilasters.
 cut(side*34,57.3,3.7,12,7,14)
 # Single-storey covered link towards the teaching block, with actual open underpass below.
 link=box(0,0,11.5,6.2,15,6.0).rotate((0,0,side*18)).translate((side*39,-14,0))
 parts.append(link)
 for x in [-1.8,1.8]:cuts.append(box(x,0,13,1.8,18,3).rotate((0,0,side*18)).translate((side*39,-14,0)))
 # Low inward wings: two floors, explicitly lower than both teaching wings and rear tower.
 inner=[(side*36,-12),(side*22,-8),(side*8,39),(side*19,43)]
 if side==-1:inner=inner[::-1]
 parts.append(poly(inner,2.8,22.2))
 for y in [1,12,23]:
  x=side*(22-(y+8)*14/47)
  cut(x,y,7,3.5,3.0,4)
  cut(x,y,17,3.5,3.0,4)
# Two-storey rear cross-link closes the court. Central courtyard remains open to the sky.
parts.append(poly([(-20,34),(-7,30),(7,30),(20,34),(22,43),(10,47),(-10,47),(-22,43)],2.8,22.2))
# Distinct round south entrance tower rises above the two-storey workshops.
parts.append(cylinder(0,51.0,2.8,10.5,10.5,33.2))
parts.append(cylinder(0,51,35.7,10.8,10.8,1.4))
cuts.append(curve_glass(0,59.7,3.9,17.5,26,7))
details.append(curve_glass(0,56.7,3.9,17.7,26,1.8))
for x in [-6,-3,0,3,6]:details.append(box(x,57.6,4,1,1.1,27) ^ curve_glass(0,57.6,4.2,16.2,24.8,2))
for z in [8,12,16,20,24]:details.append(box(0,57.6,z,19,1.1,1) ^ curve_glass(0,57.6,4.2,16.2,24.8,2))
parts.append(cylinder(0,59.7,10.8,12,5.0,1.5))
# South adjacent wall: four tall lower windows, never substitute a regular teaching grid.
for side in [-1,1]:
 for x in [16]:
  cut(side*x,45,5,1.8,4,4.0);cut(side*x,45,16,1.8,4,4.0)
# Roof service blocks are simplified; small railings/air-conditioning/pipework omitted.
solid=Manifold.batch_boolean(parts,0)
solid=solid-Manifold.batch_boolean(cuts,0)
solid=solid+Manifold.batch_boolean(details,0)
assert solid.status().name=='NoError',solid.status()
assert len(solid.decompose())==1,[(m.volume(),m.bounding_box()) for m in solid.decompose()]
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print('dimensions_mm',mesh.extents,'volume_mm3',mesh.volume,'triangles',len(mesh.faces),'watertight',mesh.is_watertight)
