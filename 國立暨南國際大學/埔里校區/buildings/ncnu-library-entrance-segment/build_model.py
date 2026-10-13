"""Hand-built NCNU Library entrance/portico segment, mm; not a whole library.
Source: NCNU completed daylight/night entrance photographs and official closeup.
Rear is a deliberately plain cut face, not an asserted surveyed rear elevation.
No external mesh is imported. Every visible architectural feature is modeled here.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];reliefs=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def hull(points):return Manifold.hull_points(np.asarray(points,dtype=float))
def beam(p,q,r):
 p=np.array(p);q=np.array(q);v=q-p;L=np.linalg.norm(v)
 return Manifold.cylinder(L,r,r,12).rotate((0,np.degrees(np.arccos(v[2]/L)),np.degrees(np.arctan2(v[1],v[0])))).translate(p)
def recess_triangle(points,normal,shrink=.78,depth=1.3):
 pts=np.array(points,dtype=float);c=pts.mean(axis=0);pts=c+(pts-c)*shrink;n=np.array(normal);n=n/np.linalg.norm(n)
 cuts.append(hull(np.concatenate([pts+n*.15,pts-n*depth])))
# Flat plinth and wide stair reaching the raised portico landing.
add(0,0,0,150,82,2.5)
for i in range(8):add(0,-35+i*1.8,2.4,116,3.4,1.0+i*.8)
add(0,-7,2.4,140,41,7)
# Deliberately truncated background facade, not the whole building.
add(0,16,9,136,9,94)
# Central glazed door bay: deep reveal and a central door mullion.
cuts.append(box(0,11.3,10,39,4.8,70))
reliefs.append(box(0,11,9,1.6,7,70))
for z in [22,34,46,58,70,81]:reliefs.append(box(0,11,z,48,7,1.6))
# Two door leaves behind the tall bay, each with upper glass and lower rails.
for x in [-10,10]:
 pass # Door leaf relief is integral to the backing plane
 reliefs.append(box(x,11,9,1.6,7,18))
# Inner vertical structural pilasters around the entry.
for x in [-23,23]:add(x,9,9,3.6,6,86)
add(0,8.8,30.5,44,3,3.0) # sign band; no made-up miniature lettering
# Flanking vertical glazing strips and foreground open colonnades.
for side in [-1,1]:
 for x0 in [33,45,57]:
  x=side*x0
  cuts.append(box(x,11.3,15,7.8,4.6,66))
  for z in [30,46,63,80]:reliefs.append(box(x,11,z,12,7,1.6))
  for edge in [-1,1]:add(x+edge*4.9,-7,9,1.7,3.2,37)
  add(x,-2,44.5,11.6,17.5,2.3)
  # Small triangular rooflets are visible above the lower side colonnades.
  parts.append(hull([(x-5.8,-11,46),(x+5.8,-11,46),(x,-11,51),(x-5.8,6,46),(x+5.8,6,46),(x,6,51)]))
# Main two columns and the unmistakable flared, faceted capitals.
for x in [-27,27]:
 add(x,-14,9,7,7,58)
 # 7mm square column expands into a 52mm square inverted truncated pyramid.
 b=[(x+dx,-14+dy,66) for dx,dy in [(-3.5,-3.5),(3.5,-3.5),(3.5,3.5),(-3.5,3.5)]]
 t=[(x+dx,-14+dy,87) for dx,dy in [(-26,-23),(26,-23),(26,23),(-26,23)]]
 parts.append(hull(b+t))
 # Three distinct glazing recesses per capital face; 2.0mm deep with robust webs.
 for k in range(4):
  j=(k+1)%4;quad=np.array([b[k],b[j],t[j],t[k]],float)
  n=np.cross(quad[1]-quad[0],quad[3]-quad[0]);n=n/np.linalg.norm(n)
  ctr=quad.mean(axis=0);toward=np.array([x,-14,76])-ctr
  if np.dot(n,toward)>0:n=-n
  bottom=(quad[0]+quad[1])/2;top=(quad[2]+quad[3])/2;half=(quad[2]-quad[3])/2
  def point(u,v):return bottom+(top-bottom)*v+half*u
  panes=[[(.08,.91),(.87,.91),(.34,.43)],[(-.87,.91),(-.08,.91),(-.34,.43)],[(-.09,.1),(.09,.1),(.19,.34),(0,.52),(-.19,.34)]]
  for uv in panes:
   pts=np.array([point(u,v) for u,v in uv]);center=pts.mean(axis=0);pts=center+(pts-center)*.88
   # Horizontal-depth recess stays open at every XY slice; avoids hidden thin lip.
   cutn=n.copy();cutn[2]=0;cutn=cutn/np.linalg.norm(cutn)
   cuts.append(hull(np.concatenate([pts+cutn*1.0,pts-cutn*2.0])))
# Continuous two-stage canopy rim, tied to backing wall.
add(0,-10,86.5,112,59,2.4)
add(0,-10,88.6,115,61,2.3)
# A clipped upper facade strip identifies this as an entry segment.
for x in [-60,-45,-30,0,30,45,60]:
 cuts.append(box(x,11.2,93,10,4.7,7))
add(0,13,101,138,14,2.4)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in reliefs:solid=solid+p
assert len(solid.decompose())==1,[(s.volume(),s.bounding_box()) for s in solid.decompose()]
m=solid.simplify(.00001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
