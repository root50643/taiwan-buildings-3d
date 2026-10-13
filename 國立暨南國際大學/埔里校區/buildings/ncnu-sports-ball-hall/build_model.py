"""NCNU Sports and Health Center ball hall exterior volume, millimetres.
Five diamond bays and an arched long-span roof follow official/architect photos.
Pool wing and connecting entrance are outside this item's scope.
Unseen rear is deliberately plain, rather than a mirrored diamond-window facade.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];reliefs=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def hull(p):return Manifold.hull_points(np.asarray(p,float))
def bar(p,q,r=.7):
 p=np.array(p);q=np.array(q);v=q-p;L=np.linalg.norm(v)
 return Manifold.cylinder(L,r,r,12).rotate((0,np.degrees(np.arccos(v[2]/L)),np.degrees(np.arctan2(v[1],v[0])))).translate(p)
def yz_profile(points,x,width):
 # CrossSection local coordinates are (y,z); extrude along local +Z then permute.
 return CrossSection([points]).extrude(width).rotate((90,0,90)).translate((x,0,0))
add(0,0,0,150,98,2.5)
# Width and depth are visually estimated; exterior is solid for printing.
add(0,1,2.4,126,72,52.1)
# Gentle segmental arch crosses the hall depth; roof is 1.8mm thick.
ys=np.linspace(-41,41,33);tops=[60.8+7.8*(1-(y/41)**2) for y in ys]
roofpts=list(zip(ys,tops))+list(zip(ys[::-1],np.array(tops[::-1])-1.8))
parts.append(yz_profile(roofpts[::-1],-68,136))
# Upper end-wall infill meets the arched roof rather than leaving detached roofing.
endpoly=[(-36,53.9),(36,53.9)]+[(float(y),60.8+7.8*(1-(y/41)**2)-1.6) for y in np.linspace(36,-36,25)]
parts.append(yz_profile(endpoly,-63,126))
# Five observed diamond-window bays on the main long facade (front = -Y).
for x in [-48,-24,0,24,48]:
 # recessed glazing and a raised diamond frame with robust 1.45mm margin
 def diamond(r,y,d):
  return hull([(x+dx,y+dy,z) for dx,z in [(-r,35),(0,35-r),(r,35),(0,35+r)] for dy in [-d/2,d/2]])
 parts.append(diamond(8.9,-35.5,2.0));cuts.append(diamond(7.1,-35.8,4.0))
 # Separate high clerestory glazing and broad louvre recess, as photographed.
 cuts.append(box(x,-35.2,48.1,20.6,2.8,5.0))
 cuts.append(box(x,-35.2,54.5,21.0,2.8,4.0))
 for j in [-7,-3.5,0,3.5,7]:reliefs.append(box(x+j,-35.2,54.2,1.2,3.0,4.8))
 # simplified louvre spacing retains thick continuous rails
 for z in [49.2,50.8,52.4]:reliefs.append(box(x,-35.2,z,21.0,3.0,.95))
# Deep vertical brick pilasters and rounded horizontal façade bands.
for x in [-60,-36,-12,12,36,60]:
 add(x,-36,2.4,2.8,4.3,43.7)
 add(x,-35.8,45.9,1.8,3.2,12.1)
 # Angled roof stays, visibly separated from wall and attached at both ends.
 # Main tapered sheet gusset seen under the eave plus separate outer tie rod.
 parts.append(hull([(x+dx,y,z) for dx in [-.95,.95] for y,z in [(-36.5,45.5),(-42.0,60.7),(-35.0,59.0)]]))
 parts.append(bar((x+3.2,-35.3,47),(x+5.2,-41,60.2),.75))
for z in [6,15,27,41.8]:add(0,-35.6,z,126,1.8,1.2)
# Two broad lower entrances exist at opposite ends; middle bays remain masonry.
for x in [-48,48]:
 cuts.append(box(x,-35.4,3.0,13.5,4.2,14.5))
 reliefs.append(box(x,-35.3,3,1.5,4.4,14.5))
 reliefs.append(box(x,-35.2,10.5,14.3,4.2,1.2))
# Side elevation: photographed blank red-brick piers rather than invented diamonds.
for y in [-30,-20,-10,0,10,20,30]:add(64.1,y,2.4,3.7,3.2,49)
for z in [15,27,41.8]:add(63.4,1,z,1.8,72,1.2)
# Unknown rear gets plain massing only. A shallow roof-edge trim is structural.
add(0,37,54,126,1.3,1.4)
solid=parts[0]
for n,p in enumerate(parts[1:]):
 assert p.status().name=="NoError",(n,p.status())
 solid=solid+p
 assert solid.status().name=="NoError",(n,solid.status())
for c in cuts:solid=solid-c
for p in reliefs:solid=solid+p
assert len(solid.decompose())==1,[(s.volume(),s.bounding_box()) for s in solid.decompose()]
m=solid.simplify(.00001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
