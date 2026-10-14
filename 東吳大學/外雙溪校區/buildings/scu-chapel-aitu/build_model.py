"""Original bounded connected Soochow chapel and Aitu exterior, output mm.
Photo-grounded roof segmentation and three-floor wing; unknown details simplified.
"""
from pathlib import Path
import numpy as np,trimesh,hashlib,json
from manifold3d import Manifold,CrossSection
R=Path(__file__).resolve().parent;S=2.5;BASE=3.;parts=[];cuts=[];details=[]
def box(x1,x2,y1,y2,z1,z2):return Manifold.cube(((x2-x1)*S,(y2-y1)*S,(z2-z1)*S)).translate((x1*S,y1*S,BASE+z1*S))
def add(*a):parts.append(box(*a))
def cut(*a):cuts.append(box(*a))
def detail(*a):details.append(box(*a))
def xz_prism(p,y1,y2):return CrossSection([np.array(p)*S]).extrude((y2-y1)*S).rotate((90,0,0)).translate((0,y2*S,BASE))
parts.append(Manifold.cube((150,150,BASE)).translate((-75,-75,0)))
# Chapel: north front flat gray high foyer, south long shallow gable.
add(-22,-6,-22,19.8,-.01,11.7)
add(-22.5,-5.5,-22.7,-7.4,11.65,12.35)
parts.append(xz_prism([(-22.5,11.65),(-5.5,11.65),(-5.5,12),(-13.75,13.4),(-14.25,13.4),(-22.5,12)],-7.6,20.4))
# Lower rear-west annex and narrow eastern platform are not full-height gable.
add(-6.2,-1.5,10,19.8,-.01,4.6)
add(-22.8,-21.8,0,17,-.01,1.1)
# Aitu three-storey wing, flat thin eave, connected at the chapel/tower junction.
add(-6,19.5,-21,-4.8,-.01,11.4)
add(-6.5,20,-21.7,-4.3,11.35,11.9)
# Joint tower: rectangular stepped solid crown and cross, not a pierced logo.
add(-7.6,-3.0,-24.0,-18.0,-.01,16.7)
add(-7.6,-5.7,-23.6,-18,16.65,17.45)
add(-5.9,-3.0,-21.7,-18,16.65,18.15)
add(-6.1,-5.5,-21.1,-20.5,17.3,21.0)
add(-7.15,-4.45,-21.1,-20.5,19.6,20.2)
# Three pairs of tower slit windows, rooted rebates, no through perforation.
for z in [2.4,7.1,12.1]:
 for x in [-6.1,-4.8]:cut(x-.22,x+.22,-24.2,-23.5,z,z+2.3)
 for y in [-22.5,-21.2]:cut(-3.5,-2.8,y-.22,y+.22,z,z+2.3)
# Chapel tall glazing plane above a lower true recessed entrance.
cut(-21.1,-8.1,-22.3,-21.1,4.4,11.05)
for x in np.linspace(-20.8,-8.4,12):detail(x-.16,x+.16,-21.5,-21.05,4.4,11.05)
for z in np.linspace(4.65,10.8,7):detail(-21.1,-8.1,-21.5,-21.05,z-.15,z+.15)
cut(-20.8,-8.2,-22.3,-20.9,1.0,3.8)
for x in np.linspace(-20.4,-8.6,7):detail(x-.18,x+.18,-21.25,-20.85,1,3.8)
detail(-20.8,-8.2,-21.25,-20.85,2.9,3.25)
# Aitu continuous paired upright window bands over three floors. Four modules before the entrance, one at the outer end
# bounded from the partly cropped official image; no AC boxes used as dividers.
for x in [-1.0,2.5,6.0,9.5,18.0]:
 cut(x-1.15,x+1.15,-21.25,-20.82,1.25,11.05)
 for dx in [-.50,.50]:cut(x+dx-.34,x+dx+.34,-21.25,-20.45,1.7,10.75)
 for z in [2.75,6.15,9.55]:
  detail(x-.86,x+.86,-20.68,-20.4,z,z+.25)
# Continuous substantial floor spandrels across the facade, rooted into body.
for z in [4.35,7.7]:detail(-2.8,19.45,-21.08,-20.4,z,z+.55)
# Wide entrance bay has a broad upper window and solid middle name-panel,
# rather than another copy of the slender paired window rhythm.
cut(11.3,16.8,-21.3,-20.45,8.3,10.75)
for x in [12.55,14.05,15.55]:detail(x-.16,x+.16,-20.7,-20.4,8.3,10.75)
detail(11.3,16.8,-20.7,-20.4,9.5,9.8)
# Entrance in outer half of Aitu, approached from raised front landing.
cut(11.0,17.2,-21.3,-20.1,.9,4.5)
for x in [11.3,13.3,15.3,17.0]:detail(x-.18,x+.18,-20.4,-20.05,1.0,4.4)
add(10.6,17.6,-23.2,-20.7,4.5,4.95)
# Three horizontal short-window rows on rear, documented in 2013 corner photo;
# interval/count elsewhere inferred, never mirrored colored upright front bays.
for x in [-2,2.5,7,11.5,16]:
 for z in [2.0,5.6,9.2]:
  cut(x-1.25,x+1.25,-5.3,-4.6,z,z+1.0)
  detail(x-.16,x+.16,-5.35,-5.0,z,z+1.0)
# Quiet chapel side high window run, count simplified pending source review.
for y in [-5,0,5,10,15]:cut(-22.2,-21.5,y-.9,y+.9,8.2,10.3)
# Broad approach stairs and rear hillside passage: no full landscaped hill.
for i in range(6):
 add(-21.3,-8.0,-26.3+i*.55,-21.8,-.01,.17*(i+1))
 add(10.5,17.7,-26.0+i*.5,-20.8,-.01,.16*(i+1))
# Low abstract retaining mass leaves 3.8m passage behind the wing. 2013 stone
# texture omitted, since retaining-wall work is documented in 2018.
add(-1,22.5,-.8,0.0,-.01,2.4)
for i in range(10):add(20.3,24.5,-9.5+i*.7,-2.0,-.01,.25*(i+1))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
m=solid.simplify(.00003).to_mesh64();mesh=trimesh.Trimesh(np.array(m.vert_properties,dtype=np.float32)[:,:3],np.array(m.tri_verts),process=False);mesh.export(R/'model.stl')
print(json.dumps({'dimensions_mm':mesh.extents.tolist(),'triangles':len(mesh.faces),'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()}))
