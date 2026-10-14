"""Original bounded Youren Memorial Library exterior prototype; mm output.
Four floors, rounded square body, seventeen front arches, four-pitch skylight.
No rear-elevation evidence: rear/side glazing deliberately not reconstructed.
"""
from pathlib import Path
import numpy as np, math,json,hashlib,trimesh
from manifold3d import Manifold,CrossSection
R=Path(__file__).resolve().parent;S=2.7;BASE=3.;parts=[];cuts=[];details=[]
def box(x1,x2,y1,y2,z1,z2):return Manifold.cube(((x2-x1)*S,(y2-y1)*S,(z2-z1)*S)).translate((x1*S,y1*S,BASE+z1*S))
def add(*a):parts.append(box(*a))
def detail(*a):details.append(box(*a))
def rounded(w,d,r,z,h):
 p=[]
 for cx,cy,a in [(w/2-r,-d/2+r,-90),(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180)]:
  for t in np.linspace(a,a+90,25):p.append([cx+r*math.cos(math.radians(t)),cy+r*math.sin(math.radians(t))])
 return CrossSection([np.array(p)*S]).extrude(h*S).translate((0,0,BASE+z*S))
def arch(cx,r,zb,zs,y1,y2):
 p=[(cx-r,zb),(cx+r,zb),(cx+r,zs)]+[(cx+r*math.cos(t),zs+r*math.sin(t)) for t in np.linspace(0,math.pi,65)[1:]]
 return CrossSection([np.array(p)*S]).extrude((y2-y1)*S).rotate((90,0,0)).translate((0,y2*S,BASE))
parts.append(Manifold.cube((150,150,BASE)).translate((-75,-78,0)))
parts.append(rounded(44,44,4.1,-.02,20.05))
# Main roof outer band, rounded corners. Front scalloped parapet remains visible.
parts.append(rounded(44.3,44.3,4.2,19.8,.65))
# Seventeen tall alternating dark-glass and shallow opaque arch bays.
for i,x in enumerate(np.linspace(-17.1,17.1,17)):
 outer=arch(x,1.21,.6,20.05,-22.38,-21.72)
 inner=arch(x,.87,1.0,20.05,-22.65,-21.45 if i%2==0 else -22.30)
 parts.append(outer);cuts.append(inner)
 if i%2==0:
  # Glass divisions rooted directly in the recess backing, no free strands.
  for z in [5.3,9.9,14.5,18.0]:
   if abs(x)>8 or z>5.55:detail(x-.88,x+.88,-21.66,-21.40,z,z+.35)
  detail(x-.16,x+.16,-21.62,-21.39,5.55 if abs(x)<8 else 1.0,19.3)
# Rounded corner walls reach the front arch tips; rear remains unornamented.
cornercap=rounded(44,44,4.1,19.9,1.45)
for xa,xb in [(-22.2,-18.25),(18.25,22.2)]:
 parts.append(cornercap ^ box(xa,xb,-22.2,-17.6,19.8,21.5))
# Four-pitch closed glass pyramid: upper floor void is interior, not a roof hole.
roofw=22.; roofbase=20.7; roofpeak=23.5
pyr=CrossSection.square((roofw*S,roofw*S),center=True).extrude((roofpeak-roofbase)*S,scale_top=(.035,.035)).translate((0,0,BASE+roofbase*S))
add(-11.25,11.25,-11.25,11.25,20.35,20.75);parts.append(pyr)
# Adjacent perpendicular roof features traced independently on 2018 imagery.
# NW long strip may include lower roof surface: deliberately low relief.
add(-10.5,10.5,15.0,20.0,20.3,20.95)
# NE shorter roof projection, height inferred rather than image-measured.
add(-19.55,-16.85,-4.0,9.4,20.3,21.4)
# Independent SW equipment box.
add(16.4,19.0,15.1,17.9,20.3,21.6)
# Front short-column canopy and recessed entry, not a high arcade.
add(-9,9,-25.4,-21.5,5.6,6.35)
for x in [-8.1,8.1]:add(x-.42,x+.42,-24.8,-23.9,.75,5.8)
cuts.append(box(-7.8,7.8,-22.7,-20.7,1.5,5.55))
for x in np.linspace(-6.5,6.5,7):detail(x-.15,x+.15,-20.9,-20.65,1.5,5.4)
detail(-7.8,7.8,-20.88,-20.6,3.3,3.65)
# Broad approach, only simplified local steps rather than full sloped landscape.
for i in range(6):add(-9.4,9.4,-27.8+i*.5,-21.8,-.01,.25*(i+1))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
m=solid.simplify(.00003).to_mesh64();mesh=trimesh.Trimesh(np.array(m.vert_properties,dtype=np.float32)[:,:3],np.array(m.tri_verts),process=False);mesh.export(R/'model.stl')
print(json.dumps({'dimensions_mm':mesh.extents.tolist(),'triangles':len(mesh.faces),'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()}))
