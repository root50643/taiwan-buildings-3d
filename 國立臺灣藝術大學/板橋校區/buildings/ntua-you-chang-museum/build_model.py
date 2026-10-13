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
# Current old-administration museum; both public long facades have monumental letters.
add(0,0,0,150,79,3)
add(0,4,2.8,132,26,43)
# Shallow pitched black-tile roof behind deep horizontal fascia.
parts.append(CrossSection.square((133,26),center=True).extrude(3.2,scale_top=(1,.02)).translate((0,4,45.3)))
add(0,4,44.3,137,30,2.1)
# Facade glazing grid backed by wall, three levels. A real central stair entrance.
for side in [-1,1]:
 y=4+side*13
 for x in [-60,-48,-36,-24,-12,0,12,24,36,48,60]:
  for z in [6,20,33]:cut(x,y,z,9,2,8)
 for x in range(-66,67,12):add(x,y+side*.3,3,1.2,1.5,41)
 for z in [16,29]:add(0,y+side*.3,z,132,1.5,1.2)
# Wide front staircase reaches second-storey central recessed portal.
for i in range(12):add(0,-34+i*1.65,2.8,20,2,1+(i+1)*1.05)
cut(0,-9.4,17,17,5,13)
add(0,-12,29,21,8,1.6)
# Massive OUR MUSEUM typography reproduced as simple geometric strokes, backed on glass.
def letter(ch,x,y,z,w,h):
 # Each segment follows the photographed ultra-condensed linear letterforms.
 if ch=='O':
  pts=[(x+w/2+w/2*math.cos(t),y,z+h/2+h/2*math.sin(t)) for t in np.linspace(0,2*math.pi,65)];line_path(pts,.9)
 if ch=='U':
  line_path([(x,y,z+h),(x,y,z+w/2)]+[(x+w/2+w/2*math.cos(t),y,z+w/2+w/2*math.sin(t)) for t in np.linspace(math.pi,2*math.pi,25)]+[(x+w,y,z+h)],.9)
 if ch=='R':
  line_path([(x,y,z),(x,y,z+h),(x+w*.5,y,z+h)]+[(x+w*.5+w*.5*math.cos(t),y,z+h*.76+h*.24*math.sin(t)) for t in np.linspace(math.pi/2,-math.pi/2,25)]+[(x,y,z+h*.52),(x+w,y,z)],.9)
 if ch=='M':line_path([(x,y,z),(x,y,z+h),(x+w/2,y,z),(x+w,y,z+h),(x+w,y,z)],.9)
 if ch=='E':
  line_path([(x+w,y,z+h),(x,y,z+h),(x,y,z),(x+w,y,z)],.9);line_path([(x,y,z+h/2),(x+w*.85,y,z+h/2)],.9)
 if ch=='S':
  pts=[(x+w/2+w/2*math.cos(t),y,z+h*.75+h*.25*math.sin(t)) for t in np.linspace(.1,math.pi*1.5,30)]
  pts += [(x+w/2+w/2*math.cos(t),y,z+h*.25+h*.25*math.sin(t)) for t in np.linspace(math.pi*.5,-math.pi+.1,30)];line_path(pts,.9)
for side in [-1,1]:
 y=4+side*13.4
 for ch,x,w in [('O',-64,20),('U',-42,11),('R',-29,11),('M',-14,18),('U',6,10),('S',18,10),('E',30,8),('U',40,10),('M',52,12)]:
  # Front center entrance interrupts the lower monument strokes as in photograph.
  start=len(details)
  letter(ch,x,y,17,w,26)
  if side==1:
   for k in range(start,len(details)):details[k]=details[k].scale((-1,1,1))
# Full monumental OUR MUSEUM sign, simplified strokes rather than a font facsimile.
# Back and front curtain wall structural grid keeps glazing opaque at print scale.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
