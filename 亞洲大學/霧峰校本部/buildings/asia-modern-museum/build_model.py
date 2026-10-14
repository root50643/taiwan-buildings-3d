"""Original source-evidenced exterior approximation, not a measured survey.
Metres are bounded image estimates; STL uses mm. Rebuild with requirements.txt.
"""
from pathlib import Path
import json, math, hashlib
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
OUT=Path(__file__).resolve().parent
S=2.15; BASE=3.0; CENTER_Y=29.0
# Highest roof and central rim: manually traced NLSC PHOTO2, in front-edge basis.
ROOF=[(-28.303,0),(.190,48.248),(28.303,0)]
RIM=[(-9.656,6.917),(.354,24.062),(10.547,6.495)]
# Lower outline follows the brochure/model triangular topology plus aerial scale.
# Only two aerial edges are observable: observed L1=(-29.639,8.185) is an OPEN
# edge endpoint, never a measured corner. The left corner below is independently
# inferred within ~1m uncertainty; a full triangle is a source-combined approximation.
MID=[(-29.8,8.0),(1.57,61.00),(32.17,7.81)]
GROUND=[(-32,5.0),(-1.5,57.82),(29,5.0)]
Z1=4.9; Z2=11.0; H=17.0
PIERS=[Polygon([(-25.7,.75),(-19,.75),(-11.2,14.25),(-17.9,14.25)]),Polygon([(19,.75),(25.7,.75),(17.9,14.25),(11.2,14.25)])]
parts=[];cuts=[];relief=[]
def extr(poly,z1,z2):
 assert poly.is_valid and not poly.is_empty
 poly=orient(poly,sign=1.0)
 contours=[list(poly.exterior.coords)[:-1]]+[list(r.coords)[:-1] for r in poly.interiors]
 # Exterior CCW and holes CW are explicitly preserved, without polygon repair.
 cs=CrossSection([[(x*S,(y-CENTER_Y)*S) for x,y in c] for c in contours])
 return cs.extrude((z2-z1)*S).translate((0,0,BASE+z1*S))
def add(poly,z1,z2):parts.append(extr(poly,z1,z2))
def rectangle(x1,x2,y1,y2):return Polygon([(x1,y1),(x2,y1),(x2,y2),(x1,y2)])
def box(x1,x2,y1,y2,z1,z2):add(rectangle(x1,x2,y1,y2),z1,z2)
def ribbon(a,b,w):
 a=np.array(a);b=np.array(b);d=b-a;n=np.array([-d[1],d[0]])/np.linalg.norm(d)*w/2
 return Polygon([a+n,b+n,b-n,a-n])
def beam(a,b,width,depth):
 # A rectangular inclined beam in a facade plane; cylinders are avoided.
 a=np.array(a);b=np.array(b);d=b-a;L=np.linalg.norm(d);d/=L
 n=np.cross(d,[0,0,1]); n/=np.linalg.norm(n);u=np.cross(n,d)
 m=Manifold.cube((width*S,depth*S,L*S),True)
 basis=np.column_stack((u,n,d));T=np.column_stack((basis,(a+b)/2))
 T[:2,3]*=S;T[1,3]-=CENTER_Y*S;T[2,3]=BASE+T[2,3]*S
 return m.transform(T)
parts.append(Manifold.cube((150,148,BASE)).translate((-75,-74,0)))
roof=Polygon(ROOF);mid=Polygon(MID);ground=Polygon(GROUND)
# Lower north cantilever support: shelley-09, unlike the two-storey R1/R3 walls.
# Its association with aerial L2 and the local 1F setback are image inferences.
rear_pier=ribbon((-2.0,51.8),(1.6,58.0),1.4)
ground_body=ground.buffer(-1.05,join_style=2).intersection(rectangle(-100,100,-100,47.8))
hole=Polygon(RIM).buffer(-.55,join_style=2)
# Ground is closed beneath the 2F/3F lightwell, not a false 3-storey through-hole.
add(ground_body,-.03,Z1)
add(rear_pier,-.03,Z1+.04)
add(ground,Z1-.45,Z1+.05)
# The 2F cantilever has its own lower fascia, overlapping the 1F roof.
add(mid,Z1-.48,Z1+.03)
# 2F/3F bodies are inset from their separately offset eaves.
mid_body=mid.buffer(-1.05,join_style=2).intersection(rectangle(-100,100,14.25,100))
add(mid_body,Z1-.02,Z2)
add(mid,Z2-.48,Z2+.03)
# 3F lower fascia follows the forward gallery, not only the receding 2F roof.
add(roof.difference(hole),Z2-.48,Z2+.03)
add(roof.buffer(-.95,join_style=2).difference(hole),Z2-.02,H-.42)
add(roof.difference(hole),H-.47,H)
# Front elevated gallery's deep opening and heavy concrete end supports.
for pier in PIERS:add(pier,-.02,Z2+.04)
# The courtyard is a 3F recess, not a triangle drilled through 2F glazing.
# Its base is bounded by the 2F roof slab; lower interior stairs are not invented.
# Interior stairs are omitted: their plan symbols do not justify inventing an
# exposed entrance stair or a surveyed courtyard staircase in this exterior model.
# Thick low triangular lightwell sill; this is a roof rim, not a closed roof.
add(Polygon(RIM).difference(hole),H-.48,H+.15)
# Facade glass is represented by shallow panel relief, no pretend transparent STL.
# Seven main vertical bands in upper gallery derived from 6 visible transoms.
def facade(poly,zlo,zhi,rows,bay=3.4,vs=True):
 coords=list(poly.exterior.coords)[:-1]
 for a,b in zip(coords,coords[1:]+coords[:1]):
  a=np.array(a);b=np.array(b);vec=b-a;L=np.linalg.norm(vec);t=vec/L
  # polygon buffered-in mass; recess each glass pane shallowly along outer edge.
  c=poly.representative_point();normal=np.array([-t[1],t[0]])
  if np.dot(np.array([c.x,c.y])-(a+b)/2,normal)<0:normal=-normal
  n=max(1,round(L/bay)); dz=(zhi-zlo)/rows
  for j in range(n):
   u=a+t*(j*L/n+.18);v=a+t*((j+1)*L/n-.18)
   pane=Polygon([u-normal*.04,v-normal*.04,v+normal*.10,u+normal*.10])
   if zhi<=Z2: 
    active_piers=PIERS+[rear_pier] if zhi<=Z1 else PIERS
    if any(pane.intersects(pier.buffer(.20,join_style=2)) for pier in active_piers):continue
   if pane.is_empty:continue
   panes=list(pane.geoms) if hasattr(pane,'geoms') else [pane]
   for pp in panes:
    for k in range(rows):cuts.append(extr(pp,zlo+k*dz+.13,zlo+(k+1)*dz-.13))
facade(ground_body,.28,Z1-.25,5)
facade(mid_body,Z1+.25,Z2-.30,6)
facade(roof.buffer(-.95,join_style=2),Z2+.28,H-.62,6)
# Sparse behind-glass V structure is indicated by shallow incised lines only.
# These four front groups are illustrative, NOT a claim of exact column counts.
# No decorative external exoskeleton or freestanding miniature strut is introduced.
def v_relief(poly,z1,z2,pitch):
 coords=list(poly.exterior.coords)[:-1]
 for a,b in zip(coords,coords[1:]+coords[:1]):
  a=np.array(a);b=np.array(b);v=b-a;L=np.linalg.norm(v);t=v/L
  n=max(1,round(L/pitch))
  c=poly.representative_point();inward=np.array([-t[1],t[0]])
  if np.dot(np.array([c.x,c.y])-(a+b)/2,inward)<0:inward=-inward
  a=a+inward*.04
  for j in range(n):
   center=a+t*((j+.5)*L/n);half=min(3.3,L/n*.35)
   left=center-t*half;right=center+t*half;foot=center
   for p in [left,right]:relief.append(beam([*foot,z1],[*p,z2],.36,.24))
v_relief(ground_body,.22,Z1-.22,13.0)
v_relief(roof.buffer(-.95,join_style=2),Z2+.22,H-.58,14.0)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in relief:solid=solid-p


assert len(solid.decompose())==1,'disconnected original geometry'
# Source-CSG tolerance 0.0001mm stabilizes float32 STL intersections; no input-STL
# repair is used by any validator. This is 1/8000 of the opening reference width.
m=solid.simplify(.0001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(json.dumps({'dimensions_mm':mesh.extents.tolist(),'faces':len(mesh.faces),'sha256':hashlib.sha256((OUT/'model.stl').read_bytes()).hexdigest()}))
