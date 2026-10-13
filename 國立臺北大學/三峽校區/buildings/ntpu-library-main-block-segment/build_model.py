"""National Taipei University Library main-block segment, handmade approximation.
The lower IT-center block behind the library is deliberately excluded.
Millimetres; photo-derived proportions, not construction or survey dimensions.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection,Mesh
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];detail=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile_xz(points,y,depth):return CrossSection([points]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def beam(p,q,w,h):
 p=np.array(p);q=np.array(q);v=q-p;l=np.linalg.norm(v);xy=np.linalg.norm(v[:2]);yaw=math.degrees(math.atan2(v[1],v[0]));pitch=-math.degrees(math.atan2(v[2],xy))
 return box(0,0,-h/2,l,w,h).rotate((0,pitch,yaw)).translate(tuple((p+q)/2))
add(0,0,0,150,115,3)
# Twin library wings: the deep 26mm axial void remains open from entry to rear.
add(-36.5,0,2.8,47,74,63.2)
add(36.5,4,2.8,47,66,63.2)
add(36.5,-34,2.8,47,13,56.2)
# Smaller set-back top floor beneath the shallow upswept canopy.
for xa,xb in [(-59,-14),(14,59)]:
 xs=np.linspace(xa,xb,33);pts=[(xa,65),(xb,65)]+[(float(x),75+.00135*x*x) for x in xs[::-1]]
 parts.append(profile_xz(pts,0,64))
# Curved unified roof: shallow upsweep, robust thickened 1.7mm edge, no giant box lid.
xs=np.linspace(-68,68,97);pts=[(float(x),75+.00135*x*x) for x in xs]+[(float(x),76.7+.00135*x*x) for x in xs[::-1]]
parts.append(profile_xz(pts,0,85))
# Curtain-wall rhythm on independently observed front and rear, shallow relief 1.15mm.
for side in [-1,1]:
 for x0 in [-36.5,36.5]:
  for x in np.arange(x0-21,x0+22,4):
   for z in np.arange(6,56 if side==-1 and x0>0 else 63,9):cut(x,(-40.5 if side==-1 and x0>0 else side*37),z,2.5,2.1,7.1)
  # Upper floor glazing is set back under canopy, visibly a different storey.
  for x in np.arange(x0-19,x0+20,6):cut(x,side*32,67,4.2,2.3,6.6)
for x in np.arange(16,58,4):cut(x,-29,60.5,2.5,2.2,4.4)
# Inner elevations face the axial street. Staggered glazing channels preserve huge void.
for side in [-1,1]:
 for y in np.arange(-31,34,6):
  for z in np.arange(6,63,9):cut(side*13,y,z,2.4,4.2,7)
# Side-wall base curtain grid, on which the broad curved ribbons are backed and fused.
for side in [-1,1]:
 for y in np.arange(-33,34,6):
  for z in np.arange(6,63,9):cut(side*60,y,z,2.4,4.1,7)
# Curved white outer skin has different sequences on the two photographed sides.
# Each is a broad continuous S ribbon, not a duplicated window lattice.
def ribbon(side,y0,width,phase,amp):
 # Backed volumetric loft: changing lateral centre, out-of-plane bow and twist.
 # Inner surface remains embedded in the wall, so there are no thin detached ribbons.
 zs=np.linspace(4,65,81);vertices=[]
 for z in zs:
  t=(z-4)/61;yc=y0+amp*math.sin(2*math.pi*t+phase)
  w=width*(1+.12*math.sin(2*math.pi*t+phase*.7))
  bow=3.2+2.2*math.sin(math.pi*t)**2
  twist=1.4*math.sin(2*math.pi*t+phase)
  ring=[(side*58.3,yc-w/2,z),(side*(60+bow+twist),yc-w/2,z),(side*(60+bow-twist),yc+w/2,z),(side*58.3,yc+w/2,z)]
  if side<0:ring=ring[::-1]
  vertices.extend(ring)
 faces=[[0,2,1],[0,3,2]]
 for k in range(len(zs)-1):
  for j in range(4):
   a=k*4+j;b=k*4+(j+1)%4;c=(k+1)*4+j;d=(k+1)*4+(j+1)%4
   faces.extend([[a,b,d],[a,d,c]])
 n=(len(zs)-1)*4;faces.extend([[n,n+1,n+2],[n,n+2,n+3]])
 r=Manifold(Mesh(np.asarray(vertices,dtype='float32'),np.asarray(faces,dtype='uint32')))
 assert r.status().name=='NoError'
 detail.append(r)
# Seen on architect front-left/side photo; wide and narrow ribbons interweave.
for y,w,p,a in [(-29,7.5,.1,4.0),(-13,7.8,2.4,6.0),(5,9.7,.2,5.7),(25,7.1,2.6,4.2)]:ribbon(-1,y,w,p,a)
# Opposite outer elevation observed in the distant elevated front photo.
for y,w,p,a in [(-28,6.5,2.5,3.0),(-11,8.6,.2,4.9),(8,8.0,2.7,5.4),(28,6.1,.1,3.1)]:ribbon(1,y,w,p,a)
# Three glazed diagonal bridges over the open axial street, at different heights.
for z,ya,yb in [(23,-23,-12),(40,15,-8),(56,-7,20)]:
 parts.append(beam((-14,ya,z+2.6),(14,yb,z+2.6),7.5,5.2))
# Roof X trusses, prominent in the architect courtyard photograph.
parts.append(beam((-14,-29,75),(14,29,75),2.2,2.3));parts.append(beam((-14,29,75),(14,-29,75),2.2,2.3))
# Entry stair and small sloping-roof vestibule at the front, leaving lateral circulation.
for i in range(6):add(0,-49+i*1.5,2.9,23,1.8,.7*(i+1))
add(0,-35.5,2.8,18,13,8.2)
# Skylight canopy profile reads as a tilted wedge rather than a generic porch.
parts.append(profile_xz([(-6.5,10),(6.5,10),(6.5,15),(-6.5,11)],0,18).rotate((0,0,90)).translate((0,-35.5,0)))
cut(0,-42,4.0,12,2.5,5.5)
for x in [-6,-2,2,6]:cut(x,-36,12.2,2.2,7,4.2)
solid=parts[0]
for i,p in enumerate(parts[1:]):
 solid=solid+p
 assert not solid.is_empty(),('part',i,p.status(),solid.status())
for i,c in enumerate(cuts):
 solid=solid-c
 assert not solid.is_empty(),('cut',i,c.status(),solid.status())
for i,p in enumerate(detail):
 solid=solid+p
 assert not solid.is_empty(),('detail',i,p.status(),solid.status())
assert len(solid.decompose())==1,[(m.volume(),m.bounding_box()) for m in solid.decompose()]
m=solid.simplify(.00001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
