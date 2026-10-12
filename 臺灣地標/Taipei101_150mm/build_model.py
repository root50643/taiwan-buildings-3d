"""Taipei 101: 150 mm, photo-interpreted FDM miniature. Units: mm.
Eight main modules follow the documented eight-floor segmentation.
Facade marks and podium are intentionally simplified, not a floor survey.
Run with numpy, trimesh, manifold3d installed (see requirements.txt).
"""
from pathlib import Path
import math
import numpy as np
import manifold3d as m
import trimesh
OUT=Path(__file__).resolve().parent
parts=[]
def box(x,y,z,sx,sy,sz):return m.Manifold.cube((sx,sy,sz),True).translate((x,y,z))
def frustum(z0,z1,w0,w1,ch=.10,x=8,y=-8):
 pts=[]
 for z,w in [(z0,w0),(z1,w1)]:
  a=w/2;b=a-w*ch
  for xx,yy in [(-b,-a),(b,-a),(a,-b),(a,b),(b,a),(-b,a),(-a,b),(-a,-b)]:pts.append([x+xx,y+yy,z])
 return m.Manifold.hull_points(pts)
def cylinder(z,h,r1,r2=None,x=8,y=-8,n=48):return m.Manifold.cylinder(h,r1,r1 if r2 is None else r2,n).translate((x,y,z))
# Flat plinth and adjoining L-shaped shopping podium (mass simplified).
parts=[box(-1,1,1.4,56,54,2.8),box(-11,1,7.3,20,40,9.2),box(5,18,7.3,36,16,9.2)]
parts += [box(-11,1,11.8,21,41,1.0),box(5,18,11.8,37,17,1.0)]
# Broad low barrel roof strips; continuous, printable support beneath.
for x,y,sx,sy in [(-11,1,14,32),(5,18,28,11)]:
 for k in range(12):
  yy=(k/11-.5)*sy; h=1.6*math.sqrt(max(0,1-(2*yy/sy)**2))
  parts.append(box(x,y+yy,12.1+h/2,sx,sy/11+.05,.7+h))
# Lower taper: proportion read from published elevation and two photographs.
parts.append(frustum(2.7,36.8,25.2,19.0))
# Facade relief gives continuous glazing rhythm, not an invented floor count.
for z in np.arange(8,36,2.0):
 w=25.2+(19-25.2)*(z-2.7)/(36.8-2.7)
 parts.append(frustum(float(z),float(z+.35),float(w+.4),float(w+.32)))
# Four ancient-coin motifs, embedded discs with a shallow square center.
coins=[]
for angle in [0,90,180,270]:
 disc=m.Manifold.cylinder(.85,2.7,2.7,64).rotate((90,0,angle)).translate((8+9.65*math.sin(math.radians(angle)),-8-9.65*math.cos(math.radians(angle)),36.8))
 coins.append(disc)
parts.extend(coins)
# Eight outward-flaring modules; each module has seven internal floor-belt marks.
for j in range(8):
 z=37.3+j*10.75
 parts += [frustum(z-.7,z+9.7,17.8,20.8),frustum(z+9.7,z+10.1,20.8,21.15),frustum(z+10.1,z+10.75,21.15,17.8)]
 for k in range(1,8):
  zz=z+k*1.24;w=17.8+(20.8-17.8)*(zz-z+.7)/10.4
  parts.append(frustum(zz,zz+.3,w+.30,w+.39))
 # Four raised corner piers follow the outward slope. No floating ornaments.
 for sx in [-1,1]:
  for sy in [-1,1]:
   pts=[]
   for zz,a in [(z,7.85),(z+9.6,9.18)]:
    for dx in [-.55,.55]:
     for dy in [-.55,.55]:pts.append([8+sx*a+dx,-8+sy*a+dy,zz])
   parts.append(m.Manifold.hull_points(pts))
 # Stylized solid ruyi-shaped caps on face centers, chamfered underside.
 for a in [0,90,180,270]:
  cap=m.Manifold.hull_points([[-1.5,-.4,0],[1.5,-.4,0],[-1.1,.65,.7],[1.1,.65,.7],[-.55,.1,-.6],[.55,.1,-.6]]).rotate((0,0,a)).translate((8-10.25*math.sin(math.radians(a)),-8+10.25*math.cos(math.radians(a)),z+9.7))
  parts.append(cap)
# Set-back crown and lantern, clearly narrower than the repeated tower modules.
parts += [frustum(122.9,124.4,16,12),frustum(124.3,126.2,12,9.5),frustum(126,135.6,8.1,10),frustum(135.6,136.3,10.7,10.7),frustum(136.2,140.0,5.3,4.8)]
for z in np.arange(127,135.5,1.25):
 w=8.1+(10-8.1)*(z-126)/9.6
 parts.append(frustum(float(z),float(z+.35),float(w+.45),float(w+.51)))
# Strengthened spire: minimum final diameter 1.4 mm, blunt safe print tip.
parts += [cylinder(139.7,.8,3),cylinder(140.2,7.4,1.1,.85),cylinder(147.4,2.6,.85,.70)]
body=m.Manifold.batch_boolean(parts,m.OpType.Add)
# Coin center relief is shallow and does not weaken the main tower.
cut=[]
for angle in [0,90,180,270]:
 cut.append(box(0,0,0,1.5,.55,1.5).rotate((0,0,angle)).translate((8+10.37*math.sin(math.radians(angle)),-8-10.37*math.cos(math.radians(angle)),36.8)))
body=body-m.Manifold.batch_boolean(cut,m.OpType.Add)
mesh=body.to_mesh();tm=trimesh.Trimesh(vertices=mesh.vert_properties[:,:3],faces=mesh.tri_verts,process=True);tm.export(OUT/'model.stl')
print('Exported',len(tm.faces),'triangles; dimensions',tm.extents,'watertight',tm.is_watertight)
