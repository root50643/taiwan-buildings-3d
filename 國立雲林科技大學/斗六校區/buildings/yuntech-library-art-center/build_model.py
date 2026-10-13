"""圖書館暨藝術中心建築群外觀縮模（毫米）。
自建幾何；官方各層平面決定逐層退縮、2008–2014多面照片決定窗組，2021空拍核屋頂。
舊圖名『圖書館暨專業大樓』。層高、隱蔽小窗、玻璃分格是照片近似，非測繪。
"""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent;parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h,side='front'):
 q=box(x,y,z,w,d,h)
 if side=='front':outside=box(x,(y-d/2-100)/2,z,w,y-d/2+100-.01,h)
 elif side=='rear':outside=box(x,(y+d/2+100)/2,z,w,100-y-d/2-.01,h)
 elif side=='right':outside=box((x+w/2+100)/2,y,z,100-x-w/2-.01,d,h)
 elif side=='left':outside=box((x-w/2-100)/2,y,z,x-w/2+100-.01,d,h)
 else:outside=None
 cuts.append((q,outside))
def plan(x0,x1,y0,y1,z,h):return box((x0+x1)*.0085-66,(y0+y1)*-.0085+44,z,(x1-x0)*.017,(y1-y0)*.017,h)
def mass(x0,x1,y0,y1,z,h):parts.append(plan(x0,x1,y0,y1,z,h))
add(0,0,0,150,112,2.8)
# Documented 79.45 x 51.75 m irregular footprint; do not fill the entire rectangle.
mass(0,7270,675,2375,2.6,59.4)
mass(5245,7270,0,695,2.6,59.4) # high book-stack bar
mass(1195,5245,1375,4100,2.6,25.4)
mass(1195,5245,1375,3400,2.6,33.4)
mass(1195,5245,1375,2675,2.6,41.4)
# Left service-stair projection, right low teaching/art wing, and projecting library lobby.
mass(-370,520,1050,1725,2.6,44.4)
mass(520,1195,1350,2025,2.6,35.4)
mass(5245,7945,0,4500,2.6,28.4)
mass(5245,7270,675,4500,2.6,40.4)
mass(4570,6595,2025,5175,2.6,41.9)
# Long roof-light well in the projecting low wing (7F roof plan).
cut(29,-18,42.9,11,25,3,side="top")
# Front lobby is defined by a high recessed glazed slit; projecting monumental entry frame.
mass(5320,6220,4700,5480,2.7,15.3)
# Thick parapets preserve the terrace outlines. Connected relief; no isolated thin plants.
for x0,x1,y,z in [(1195,5245,2675,44),(1195,5245,3400,36),(1195,4570,4100,28)]:
 p=plan(x0,x1,y-65,y+65,z-.2,1.6);parts.append(p)
# Long rooftop 9F plant, two roof wells and broad square skylight visible in aerial and roof plan.
mass(5245,6595,0,750,61.6,8.4)
mass(675,3075,735,1065,61.7,5.3)
# Roof parapet, clear recesses deliberately open to sky rather than enclosed cavities.
cut(-5,16.7,61.1,108,24,3,side="top")
details.append(box(-24,16.7,61,10,10,1.6))
# Low pyramid skylight, generated from our own four triangles via convex hull.
pts=np.array([[-29,11.7,62.5],[-19,11.7,62.5],[-19,21.7,62.5],[-29,21.7,62.5],[-24,16.7,66]])
details.append(Manifold.hull_points(pts))
# Main front high facade: square upper windows, long recessed ribbon, broad glazed lower wall.
front=44-2375*.017
for x in np.linspace(-57,48,20):cut(float(x),front-.15,55.2,3.4,2.2,4.5)
cut(-3,front-.15,47.5,111,2.7,5.1)
for x in np.linspace(-57,49,22):details.append(box(float(x),front+.95,47.5,.9,1.2,5.1))
# Large glazing wall is hidden behind the terraced mass at its middle, visible at each end.
for x in np.linspace(-55,46,22):
 for z,h in [(5.6,7.9),(14.5,7.5),(23,7.5),(31.5,7.5),(40,5.2)]:cut(float(x),front-.12,z,3.55,2.5,h)
for x in np.linspace(-57,49,23):details.append(box(float(x),front+.95,5.5,1.0,1.2,39.8))
for z in [13.5,22.0,30.5,39.0]:details.append(box(-4,front+.95,z,109,1.2,1.0))
# Terraced front blocks: tall ground windows, square windows, and tiny clerestory vents.
for yc,zmax,x0,x1 in [(2675,44,1195,5245),(3400,36,1195,5245),(4100,28,1195,4570)]:
 y=44-yc*.017
 for cm in np.arange(x0+260,x1-150,550):
  x=cm*.017-66
  for z,h in [(5.2,9.3),(19.5,5.0),(29.5,5.0)]:
   if z+h<zmax:cut(x,y-.12,z,3.8,2.0,h)
  if zmax>=36:cut(x,y-.12,zmax-5,1.5,2.0,1.7)
# Art-centre entrance at exposed end: cantilever canopy made robust and connected to body.
add(-59,front-2.0,14.4,14,6.5,1.5);cut(-59,front-1.0,3.9,7.0,2.5,10.2)
# Rear flat facade observed in official 2009 photos: discrete square rows, not mirrored glazing.
rear=44-675*.017
for x in np.linspace(-54,49,18):
 for z,h in [(6,5),(16,4.2),(26,4.2),(36,4.2),(47.8,4.5),(55.5,4.3)]:cut(float(x),rear+.12,z,3.4,2.2,h,side="rear")
# Two ends have tall vertical recessed staircase glazing plus square side windows.
for x in [-66,57.59]:
 cut(x,21.5,5,2.5,4.2,46.5,side="left" if x<0 else "right")
 for y in [11,31]:
  for z in [7,18,29,40,55]:cut(x,y,z,2.3,3.4,4.4,side="left" if x<0 else "right")
# Right-wing exterior open balcony-like bands are backed recesses, from the 2009 side photograph.
xside=7270*.017-66
for z in [17,27,37]:cut(xside+.1,-14,z,2.4,33,4.7,side="right")
for y in [-29,-19,-9,1]:details.append(box(xside-.4,y,16.5,1.8,1.0,26.3))
# Front library entrance and glass-block panel, shown in the official 2004 photograph.
y=44-5175*.017
cut(31,y-.15,20,21,2.5,20)
cut(32,-49.25,4.2,12,2.7,11.5)
for z in [25,30,35]:details.append(box(31,y+.95,z,21,1.2,1))
for x in [23,27,31,35,39]:details.append(box(x,y+.95,20,1,1.2,20))
# Low right wing's large windows are constrained by the official floor plan; tree-hidden heights estimated.
for y in [36,25,14,3,-8,-19,-30]:
 for z in [6,19]:cut(69.06,y,z,2.4,4.8,7,side="right")
for x in [51,61]:
 for z,h in [(5,10),(21,6)]:cut(x,-32.6,z,4.6,2.2,h)
# Simple entry stair, no free railings or reproduced text/logo/sculpture.
for i in range(5):add(32,-51+i*.9,2.6+i*.4,18,2,.8)
solid=parts[0]
for p in parts[1:]:solid=solid+p
# Only cut externally exposed bays. Hidden windows are not internal sealed cavities.
uncut=solid
for c,outside in cuts:
 if outside is None or (uncut^outside).volume()<1e-5:solid=solid-c
# Only expose mullion details where they meet existing facade. Intersect backing band with original volume.
for p in details:solid=solid+p
assert len(solid.decompose())==1,'Disconnected or enclosed shell'
m=solid.simplify(1e-5).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
