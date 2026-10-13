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
# One theater mass with high stage tower and lower auditorium. Adjacent academic blocks excluded.
add(0,0,0,150,142,3)
# Front west facade is y=-50; stage tower sits behind at north.
add(0,-12,2.8,111,93,61)
add(0,47,2.8,106,29,89)
add(0,47,91,109,32,2)
# Theatre rounded stair end on front-left; round porthole recesses documented by daylight photo.
parts.append(Manifold.cylinder(70,11,11,circular_segments=64).translate((-49,-52,2.8)))
for z in [9,21,36,50,61]:
 cuts.append(Manifold.cylinder(4,2.1,2.1,circular_segments=32).rotate((90,0,0)).translate((-50,-59.8,z)))
# Cylinder horizontal cladding seams follow the actual daylight elevation.
for z in range(7,72,4):
 outer=Manifold.cylinder(.65,11.2,11.2,circular_segments=64)
 inner=Manifold.cylinder(.85,10.5,10.5,circular_segments=64).translate((0,0,-.1))
 cuts.append((outer-inner).translate((-49,-52,z)))
# Recessed public facade horizontal glazing and canopy.
for z in [7,22]:
 for x in [-29,-11,7,25,43]:cut(x,-58.5,z,14,3,7)
for z in [37,52]:cut(-29,-58.5,z,14,3,7)
add(30,-62,32,27,8,2.4)
# Thin horizontal cladding grooves are shallow, supported throughout.
for z in range(7,62,5):
 cut(4,-59,z,98,1.2,.7)
 cut(55.4,-10,z,1.2,90,.7)
# Repeated tall bent vertical light channels, represented as relief attached to west facade.
for x in [-9,9,28]:
 line_path([(x,-59.1,40),(x-2,-59.1,49),(x+1,-59.1,60)],1.1)
# Side elevation strips bend between high upper facade and lower entry strip.
for y in [-39,-17,5,25]:
 line_path([(55.8,y,37),(55.8,y-2,48),(55.8,y,62)],.8)
# Tower: narrow vertical ribs and small offset rectangular accents.
for x in range(-51,52,6):add(x,31.9,58,1,1.5,33)
for x in range(-51,52,8):add(x,62,4,1,1.5,87)
for y in range(34,63,6):
 for side in [-1,1]:add(side*53.2,y,4,1.5,1,87)
for x in range(-45,50,13):
 for z in [61,72,83]:cut(x,31.5,z,2.3,2.0,3)
# Prominent exterior dogleg stair against the photographed public elevation.
# Backed step volumes replace the unprintable open underside, explicitly disclosed.
for i in range(16):add(46-i*1.7,-63,2.8,1.9,9,10+i*1.1)
add(16,-63,28,8,10,3)
for i in range(10):add(46,-68+i*.8,2.8,10,1,1+i*1.1)
line_path([(49,-68,15),(43,-68,16),(19,-68,33),(12,-68,33)],.9)
# Unseen rear service doors and roofs are deliberately undecorated.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
