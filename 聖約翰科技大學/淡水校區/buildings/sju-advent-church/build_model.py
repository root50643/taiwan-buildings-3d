"""Original photo-based circa-2014 Advent Church exterior approximation.
Metre-like design parameters below are inferred except the 28–30m roof envelope.
Output mm. Four square ruled curved faces are an approximation, not surveyed math.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
from manifold3d import Manifold,Mesh64
OUT=Path(__file__).resolve().parent
S=4.55; BASE=3.; EAVE=4.4; ROOF_RISE=10.0; TOP_HALF=1.6
parts=[];cuts=[]
def cube(x1,x2,y1,y2,z1,z2):
 return Manifold.cube(((x2-x1)*S,(y2-y1)*S,(z2-z1)*S)).translate((x1*S,y1*S,BASE+z1*S))
def add(*a):parts.append(cube(*a))
def cut(*a):cuts.append(cube(*a))
parts.append(Manifold.cube((150,150,BASE)).translate((-75,-75,0)))
# Low main wall body: cross-plan recesses under the square eaves, not full roof box.
add(-10.6,10.6,-12.1,12.1,-.02,EAVE)
add(-12.1,12.1,-8.4,8.4,-.02,EAVE)
# Entrance faces -Y; post-2003 broad central glazing and flanking doors.
add(-6.4,6.4,-12.65,-10.8,-.02,3.85)
# Central four horizontal glazing rows with one vertical division, framed doors
# on both sides and one slender outer opening each, matching newer front photo.
for xa,xb in [(-2.6,-.12),(.12,2.6)]:
 for za,zb in [(.3,.88),(1.08,1.66),(1.86,2.44),(2.64,3.15)]:cut(xa,xb,-12.85,-12.25,za,zb)
for xa,xb in [(-5.15,-4.25),(-4.02,-3.12),(3.12,4.02),(4.25,5.15)]:cut(xa,xb,-12.85,-12.25,.3,3.0)
for x in [-5.9,5.9]:cut(x-.17,x+.17,-12.85,-12.25,.5,3.15)
# Wide canopy supported by rooted major piers, not tiny door mullions.
add(-8.3,8.3,-13.0,-10.8,3.6,4.2)
for x in [-7.8,7.8]:add(x-.23,x+.23,-12.85,-11.7,-.02,3.9)
# Side recessed lower bays and long narrow vertical slots, seen in source.
for y in [-6.2,5.8]:
 cut(-12.3,-11.78,y-.35,y+.35,.65,3.55)
 cut(11.78,12.3,y-.35,y+.35,.65,3.55)
for x in [-7.0,2.1,7.0]:cut(x-.32,x+.32,11.77,12.3,.55,3.6)
# Rear service door is distinct from front glazing. No mirrored porch.
cut(-3.9,-2.5,11.8,12.3,.2,2.8)
# Visible recessed corner bays remain open below the overhanging roof.
for x in [-12.1,12.1]:
 for y in [-10.1,10.1]:add(x-.23,x+.23,y-.3,y+.3,-.02,EAVE)
# Continuous printable fascia (0.35m thick) and four curved shell envelope.
add(-14.5,14.5,-14.5,14.5,EAVE-.2,EAVE+.15)
verts=[];faces=[]
N=100
for i in range(N+1):
 t=i/N;a=TOP_HALF+(14.5-TOP_HALF)*(1-t)**2.55;z=EAVE+ROOF_RISE*t
 for x,y in [(-a,-a),(a,-a),(a,a),(-a,a)]:verts.append((x*S,y*S,BASE+z*S))
for i in range(N):
 for j in range(4):
  a=i*4+j;b=i*4+(j+1)%4;c=(i+1)*4+(j+1)%4;d=(i+1)*4+j
  faces.extend([(a,b,c),(a,c,d)])
faces.extend([(0,2,1),(0,3,2)])
q=N*4;faces.extend([(q,q+1,q+2),(q,q+2,q+3)])
parts.append(Manifold(Mesh64(np.array(verts,dtype=float),np.array(faces,dtype=np.uint64))))
# Short square crown and three deep vertical slots per curve near crown.
add(-TOP_HALF,TOP_HALF,-TOP_HALF,TOP_HALF,EAVE+ROOF_RISE-.05,EAVE+ROOF_RISE+.6)
# Recesses in the solid exterior, not fictitious empty interior or tiny frame strips.
def slot(x,angle):
 vs=[];fs=[];n=30
 for i in range(n+1):
  z=10.65+(12.45-10.65)*i/n;t=(z-EAVE)/ROOF_RISE
  a=TOP_HALF+(14.5-TOP_HALF)*(1-t)**2.55
  for xx,yy in [(x-.20,-a-.10),(x+.20,-a-.10),(x+.20,-a+.25),(x-.20,-a+.25)]:vs.append((xx*S,yy*S,BASE+z*S))
 for i in range(n):
  for j in range(4):
   a=i*4+j;b=i*4+(j+1)%4;c=(i+1)*4+(j+1)%4;d=(i+1)*4+j
   fs.extend([(a,b,c),(a,c,d)])
 fs.extend([(0,2,1),(0,3,2)]);q=n*4;fs.extend([(q,q+1,q+2),(q,q+2,q+3)])
 return Manifold(Mesh64(np.array(vs,dtype=float),np.array(fs,dtype=np.uint64))).rotate((0,0,angle))
for x in [-.9,0,.9]:
 for angle in [0,90,180,270]:cuts.append(slot(x,angle))
# Root-connected cross, deliberately >=1.59mm thick for small scale.
z=EAVE+ROOF_RISE+.6
add(-.175,.175,-.175,.175,z-.12,z+2.6)
add(-1.05,1.05,-.175,.175,z+1.45,z+1.8)
# Simplified front entry steps anchored in base, landscape stair flight excluded.
for i in range(3):add(-5.8,5.8,-14.6+i*.5,-12.5,0,.12*(i+1))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for p in cuts:solid=solid-p
assert len(solid.decompose())==1
m=solid.simplify(.000001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=False)
mesh.export(OUT/'model.stl')
print(json.dumps({'dimensions_mm':mesh.extents.tolist(),'faces':len(mesh.faces),'sha256':hashlib.sha256((OUT/'model.stl').read_bytes()).hexdigest()}))
