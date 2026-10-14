"""Original FGU Huaien Hall exterior approximation; no third-party mesh.
Parameters are photo/plan-derived estimates in metres; final output millimetres.
White cap is a shallow parallel-arch envelope, not a hemisphere. Cap offset
provisionally zero, with unresolved image parallax explicitly documented.
"""
from pathlib import Path
import numpy as np, trimesh,json,hashlib,math
from manifold3d import Manifold,Mesh64
R=Path(__file__).resolve().parent;S=2.;BASE=3.;N=192
parts=[];cuts=[];structural=[]
def cube(x1,x2,y1,y2,z1,z2):return Manifold.cube(((x2-x1)*S,(y2-y1)*S,(z2-z1)*S)).translate((x1*S,y1*S,BASE+z1*S))
def add(*a):parts.append(cube(*a))
def cyl(rad,z1,z2):return Manifold.cylinder((z2-z1)*S,rad*S,rad*S,N).translate((0,0,BASE+z1*S))
def rings(profiles,corrugated=False):
 v=[];f=[]
 for rad,z in profiles:
  for i in range(N):
   t=2*math.pi*i/N;x=rad*math.cos(t);y=rad*math.sin(t)
   zz=z
   if corrugated:
    zz-=.20*(1-math.cos(2*math.pi*(.866025403784*x-.5*y)/4.4))*max(0,1-(rad/25.7)**2)*min(1,(rad/15.)**2)
    # Finite summit landing, 0.10mm lower than mathematical apex, avoids a
    # vanishing corrugated cusp at miniature scale without changing sampling.
    zz=min(zz,22.30)
   v.append((S*x,S*y,BASE+S*zz))
 for k in range(len(profiles)-1):
  for i in range(N):a=k*N+i;b=k*N+(i+1)%N;c=b+N;d=a+N;f.extend([(a,b,c),(a,c,d)])
 for i in range(1,N-1):f.append((0,i+1,i))
 q=(len(profiles)-1)*N
 for i in range(1,N-1):f.append((q,q+i,q+i+1))
 return Manifold(Mesh64(np.array(v,float),np.array(f,dtype=np.uint64)))
def sector(r1,r2,a1,a2,z1,z2):
 pts=[];n=max(4,int((a2-a1)/2))
 for i in range(n+1):t=math.radians(a1+(a2-a1)*i/n);pts.append((r2*math.cos(t),r2*math.sin(t)))
 for i in range(n,-1,-1):t=math.radians(a1+(a2-a1)*i/n);pts.append((r1*math.cos(t),r1*math.sin(t)))
 from manifold3d import CrossSection
 return CrossSection([np.array(pts)*S]).extrude((z2-z1)*S).translate((0,0,BASE+z1*S))
def beam(a,b,w):
 a=np.array(a)*S+np.array([0,0,BASE]);b=np.array(b)*S+np.array([0,0,BASE]);d=b-a;length=np.linalg.norm(d)
 z=d/length;x=np.cross([0,1,0],z);x=x/np.linalg.norm(x);y=np.cross(z,x);M=np.column_stack([x,y,z,a]);return Manifold.cube((w*S,w*S,length)).translate((-w*S/2,-w*S/2,0)).transform(M)
parts.append(Manifold.cube((150,144,BASE)).translate((-75,-72,0)))
# Low-side reference grade; westward terrain wedge indicates partly buried B1.
# Keep wedge local to building, not a claim of surveyed landscape contours.
v=[(-34,-33,0),(34,-33,0),(34,33,0),(-34,33,0),(-34,-33,6.0),(34,-33,.05),(34,33,.05),(-34,33,6.0)]
f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
parts.append(Manifold(Mesh64(np.array(v)*S+[0,0,BASE],np.array(f,dtype=np.uint64))))
# Basement and main tall hall are not three equal full-height storeys.
parts.append(cyl(27.9,-.02,6.5));parts.append(cyl(26.15,6.2,13.8))
# Upper level gallery / outdoor colonnade deck.
parts.append(cyl(29.5,6.0,6.6))
# East/southeast exposed side: broad high curved concrete wall below a
# continuous upper glazing band. This enclosed arc differs from rear colonnade.
# Angular extent and 8.6m solid-wall top are bounded photo interpretations.
# 0.2 degree construction overlaps avoid exact tangency at gallery end planes.
parts.append(sector(25.0,29.60,-157.7,-22.3,-.02,13.75))
# Main east B1 entry is recessed beneath its lower portico, not repeated windows.
cuts.append(sector(25.0,28.1,-20,28,.25,5.65))
for i in range(32):
 a=i*360/32; signed=(a+180)%360-180
 enclosed=-157.5<=signed<=-22.5
 if enclosed:
  # Main solid base reaches 8.6m; only upper band is glazed, five shallow rows.
  for za,zb in [(8.8,9.5),(9.7,10.4),(10.6,11.3),(11.5,12.2),(12.4,13.1)]:
   cuts.append(sector(29.25,29.9,a-4.1,a+4.1,za,zb))
 else:
  for za,zb in [(7.15,8.15),(8.4,9.4),(9.65,10.65),(10.9,11.9),(12.15,13.15)]:
   cuts.append(sector(25.8,26.5,a-4.2,a+4.2,za,zb))
 t=math.radians(a)
 if enclosed:structural.append(beam((29.55*math.cos(t),29.55*math.sin(t),8.55),(29.55*math.cos(t),29.55*math.sin(t),13.85),.9))
 else:structural.append(beam((28.6*math.cos(t),28.6*math.sin(t),6.35),(30.0*math.cos(t),30.0*math.sin(t),13.85),.9))
# Continuous low outer railing simplified as rooted solid parapet; entry opening.
parts.append(sector(28.1,29.5,38,202.7,6.5,7.45))
# Grey sloped ring; solid miniature roof fills unseen interior.
parts.append(rings([(30.5,13.55),(30.5,14.0),(25.7,19.05),(25.7,19.45)]))
# Shallow cap interpolating parallel-arch envelope, rise3m on diameter51.4m.
profiles=[]
for i in range(65):
 r=25.7*(1-i/65);z=19.35+3.0*(1-(r/25.7)**2);profiles.append((r,z))
profiles.append((.03,22.35))
parts.append(rings(profiles,True))
# East low curved portico, independent from wider paving. Plan/orthophoto footprint.
parts.append(sector(25.7,36.0,-32,32,10.8,11.45))
parts.append(sector(26.0,35.0,-31,31,5.9,6.6))
for angle in [-29,-15,0,15,29]:
 t=math.radians(angle);x=34.6*math.cos(t);y=34.6*math.sin(t);parts.append(beam((x,y,.0),(x,y,11.15),.95))
# Fine diagonal entrance braces omitted at miniature scale; main radial slanted
# colonnade and five rooted canopy posts are retained.
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in structural:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.000001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=False);mesh.export(R/'model.stl')
print(json.dumps({'dimensions_mm':mesh.extents.tolist(),'triangles':len(mesh.faces),'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()}))
