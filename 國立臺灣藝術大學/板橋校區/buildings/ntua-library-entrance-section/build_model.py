"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. No survey or interior data used.
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
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def gable(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x,z+h)],y,d))
def arch(x,y,z,w,h,depth):
 r=w/2; spring=z+h-r
 pts=[(x-r,z),(x+r,z),(x+r,spring)]
 pts += [(x+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,25)[1:]]
 return profile(pts,y,depth)
def arch_cut(x,y,z,w,h,depth):cuts.append(arch(x,y,z,w,h,depth))
def arch_trim(x,y,z,w,h):
 # Backed relief ring, fused into the wall, not a separate floating shell.
 details.append(arch(x,y,z,w+1.7,h+.85,1.7)-arch(x,y-.1,z-.2,w,h+.2,2.3))
def hip(x,y,z,w,d,h):parts.append(CrossSection.square((w,d),center=True).extrude(h,scale_top=(.72,.03)).translate((x,y,z)))
def column(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
def step(x,y,w,n=3):
 for i in range(n):add(x,y+i*1.4,2.8,w,1.7,.7*(i+1))

def rod(a,b,r=0.7):
 a=np.array(a);b=np.array(b);v=b-a;h=float(np.linalg.norm(v))
 if h<1e-6:return
 u=v/h
 axis=np.cross([0,0,1],u);c=u[2]
 if np.linalg.norm(axis)<1e-8:R=np.eye(3) if c>0 else np.diag([1,-1,-1])
 else:
  K=np.array([[0,-axis[2],axis[1]],[axis[2],0,-axis[0]],[-axis[1],axis[0],0]])
  R=np.eye(3)+K+K@K/(1+c)
 details.append(Manifold.cylinder(h,r,r,circular_segments=12).transform(np.column_stack([R,a])))
def line_path(points,r=.7):
 from shapely.geometry import LineString
 from manifold3d import FillRule
 if max(p[1] for p in points)-min(p[1] for p in points)<1e-7:
  q=LineString([(p[0],p[2]) for p in points]).buffer(r,cap_style=2,join_style=2)
  polys=[list(q.exterior.coords)]+[list(i.coords) for i in q.interiors]
  details.append(CrossSection(polys,FillRule.EvenOdd).extrude(2*r).rotate((90,0,0)).translate((0,points[0][1]+r,0)))
 elif max(p[0] for p in points)-min(p[0] for p in points)<1e-7:
  q=LineString([(p[1],p[2]) for p in points]).buffer(r,cap_style=2,join_style=2)
  polys=[list(q.exterior.coords)]+[list(i.coords) for i in q.interiors]
  details.append(CrossSection(polys,FillRule.EvenOdd).extrude(2*r).rotate((90,0,90)).translate((points[0][0]-r,0,0)))
 else:
  for a,b in zip(points,points[1:]):rod(a,b,r)
# Public entrance section only. Unseen rear and full six-storey tower excluded.
add(0,0,0,150,100,3)
add(0,15,2.8,134,40,62)
add(-43,15,62.5,48,40,27)
# Three horizontal stepped upper facade ribbons of the photographed low wing.
for z in [20,35,50]:add(23,-7,z,87,5,2.2)
# Irregular pentagonal windows, shallow engravings rather than pierced internal rooms.
for row,z in enumerate([24,39,54]):
 for j,x in enumerate([-60,-47,-30,-10,8,28,48,60]):
  if x<0:continue
  w=5.5 if j%2 else 6.8
  pts=[(x-w/2,z),(x+w/2,z+.7),(x+w*.6,z+4),(x,z+6),(x-w*.55,z+4)]
  cuts.append(profile(pts,-5.5,2.5))
for x,z in [(-60,69),(-44,77),(-28,68)]:
 cuts.append(profile([(x-4,z),(x+3,z-1),(x+5,z+4),(x,z+7),(x-5,z+5)],-5.5,2.5))
# Transparent glass represented as solid print substrate; globe retained as curved volume.
center=np.array([-34,-16,40]);radii=np.array([25,20,31])
parts.append(Manifold.sphere(1,48).scale(radii).translate(center))
# Cylinder/entry at ground level intersects globe and building.
parts.append(Manifold.cylinder(24,20,20,circular_segments=64).translate((-34,-17,2.8)))
parts.append(Manifold.cylinder(2,23,23,circular_segments=64).translate((-34,-17,23)))
# Visible globe metal grid is backed relief, not floating hollow ribs.
for lat in [-45,-20,5,30,55]:
 t=math.radians(lat);pts=[]
 for u in np.linspace(0,2*math.pi,97):pts.append(center+(radii-.6)*[math.cos(t)*math.cos(u),math.cos(t)*math.sin(u),math.sin(t)])
 line_path(pts,.8)
for lon in range(0,180,30):
 u=math.radians(lon);pts=[]
 for t in np.linspace(0,2*math.pi,97):pts.append(center+(radii-.6)*[math.cos(t)*math.cos(u),math.cos(t)*math.sin(u),math.sin(t)])
 line_path(pts,.85)
# Ground glazing and oblique braces beside the entrance.
for x in [-61,-52,-8,7,22,37,52,62]:
 if x>-15:
  cut(x,-5.5,5,10,2.8,12)
  rod((x-5,-6.8,3),(x+5,-6.8,20),.9)
for x in [-43,-34,-25]:cut(x,-36.5,4,6,4,15)
add(-34,-37,19,30,2,2)
for x in [-52,-16]:column(x,-32,3,1.4,22)
# Plain cropped rear is explicitly approximate; no claim of complete library footprint.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
