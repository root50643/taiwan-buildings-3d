"""Dragon and Tiger Pagodas. Seven storeys, twelve-corner tiers and solid simplified animals.
Photo-interpreted, approximate exterior; millimeters. Decorative details are thickened.
"""
from pathlib import Path
import numpy as np,math,trimesh,manifold3d as m
OUT=Path(__file__).resolve().parent

def box(x,y,z,a,b,c):return m.Manifold.cube((a,b,c),True).translate((x,y,z))
def ball(x,y,z,a,b,c):return m.Manifold.sphere(1,40).scale((a,b,c)).translate((x,y,z))
def loft(rings,x,y):
 N=12*6;verts=[]
 for r,z,lift in rings:
  for i in range(N):
   s=i//6;t=(i%6)/6;a=math.pi/12+s*math.pi/6;b=a+math.pi/6
   verts.append([x+r*((1-t)*math.cos(a)+t*math.cos(b)),y+r*((1-t)*math.sin(a)+t*math.sin(b)),z+lift*abs(2*t-1)**3])
 faces=[]
 for k in range(len(rings)-1):
  for i in range(N):j=(i+1)%N;faces.extend([[k*N+i,k*N+j,(k+1)*N+j],[k*N+i,(k+1)*N+j,(k+1)*N+i]])
 for i in range(1,N-1):faces.extend([[0,i+1,i],[(len(rings)-1)*N,(len(rings)-1)*N+i,(len(rings)-1)*N+i+1]])
 tm=trimesh.Trimesh(verts,faces,process=True);tm.fix_normals()
 return m.Manifold(m.Mesh64(np.array(tm.vertices,np.float64),np.array(tm.faces,np.uint64)))
def tube(points,r=.6):
 pieces=[ball(*p,r,r,r) for p in points]
 for a,b in zip(points,points[1:]):
  v=np.array(b)-a;length=np.linalg.norm(v);az=math.degrees(math.atan2(v[1],v[0]));el=math.degrees(math.acos(v[2]/length))
  pieces.append(m.Manifold.cylinder(float(length),r,r,16).rotate((0,el,az)).translate(a))
 return m.Manifold.batch_boolean(pieces,m.OpType.Add)
def archcut(radius,z):
 w=3.8;depth=2.4;bottom=z+3.1;h=6.0;r=w/2
 return box(0,-radius,bottom+(h-r)/2,w,depth,h-r)+m.Manifold.cylinder(depth,r,r,24).rotate((90,0,0)).translate((0,-radius+depth/2,bottom+h-r))
parts=[box(0,0,1.4,150,124,2.8),box(0,22,4.2,111,31,3.6)]
for cx in [-36,36]:
 parts.append(m.Manifold.cylinder(3.3,1,1,72).scale((24,39,1)).translate((cx,-9,2.5)))
 parts.append(m.Manifold.cylinder(3,24,24,12).rotate((0,0,15)).translate((cx,22,4)))
 for level in range(7):
  z=6.6+12.8*level;r=13.8-.35*level;re=22.2-.45*level
  body=m.Manifold.cylinder(13.8,r,r-.35,12).rotate((0,0,15)).translate((cx,22,z-.2))
  cuts=[]
  for f in range(12):
   # Shallow arched recesses have closed backs; no interior theatre-like cavities.
   cuts.append(archcut(r*math.cos(math.pi/12)-.15,z).rotate((0,0,f*30)).translate((cx,22,0)))
  body-=m.Manifold.batch_boolean(cuts,m.OpType.Add);parts.append(body)
  parts.append(loft([(r*.96,z+8.1,0),(re,z+9.9,1.15),(re,z+11.1,1.15),(re*.88,z+11.5,.5),(r*.90,z+14.3,0)],cx,22))
  # A continuous thickened balcony band and twelve short posts replace very fine rails.
  rr=r+2.4
  parts.append((m.Manifold.cylinder(1.15,rr,rr,12)-m.Manifold.cylinder(1.6,rr-1.25,rr-1.25,12)).rotate((0,0,15)).translate((cx,22,z+2.3)))
  parts.append(m.Manifold.cylinder(.9,rr+.7,rr+.7,12).rotate((0,0,15)).translate((cx,22,z+1.1)))
  for f in range(12):
   a=math.pi/12+f*math.pi/6
   parts.append(m.Manifold.cylinder(7.4,1.0,1.0,16).translate((cx+(r+1.2)*math.cos(a),22+(r+1.2)*math.sin(a),z+1.3)))
 # Stacked finial with a robust 1.6 mm terminal diameter.
 parts.append(m.Manifold.cylinder(3.2,4.5,3.9,32).translate((cx,22,97.4)))
 for k in range(4):parts.append(m.Manifold.cylinder(2.0,3.8-.65*k,3.0-.65*k,32).translate((cx,22,100+1.6*k)))
 parts.append(m.Manifold.cylinder(3.3,1.5,.8,24).translate((cx,22,106.2)))
# Dragon at viewer's left, tiger at right, both facing toward negative Y.
for cx,kind in [(-36,'dragon'),(36,'tiger')]:
 body=ball(cx,-11,19,14,24,12)+ball(cx,-37,20,13.8,14,14)
 if kind=='dragon':
  body+=ball(cx,-45,27,11.4,9,4.8)
  body+=ball(cx,-48,9.2,11,8,4)
 else:
  body+=ball(cx,-48,8.7,10.5,7.5,3.8)
  body+=ball(cx-5,-46,25,6.3,7,4.1)+ball(cx+5,-46,25,6.3,7,4.1)
  body+=ball(cx,-51,27,3.4,3.2,2.4)
 # Wide accessible mouth recess, open to the front with a substantial back and jaw.
 body-=ball(cx,-48,17,9.3,14,9.2)
 parts.append(body)
 # Fused fore and hind paws, broad supports rather than fine disconnected legs.
 for dx in [-10.5,10.5]:
  for y in [-23,3]:parts.append(ball(cx+dx,y,11,4.5,6.4,7.2))
 # Upper eye ridges and eyeballs are low relief.
 for dx in [-8.7,8.7]:
  parts.append(ball(cx+dx,-43,29,3.6,3.4,2.0));parts.append(ball(cx+dx,-45,28.4,1.7,1.9,1.4))
 # Four thickened fangs are rooted in the upper jaw, not loose needles.
 for dx in [-7.4,7.4]:
  parts.append(m.Manifold.cylinder(3.5,.9,1.45,18).translate((cx+dx,-48,21.6)))
  parts.append(m.Manifold.cylinder(2.5,1.35,.85,18).translate((cx+dx,-48,8.9)))
 if kind=='dragon':
  for dx in [-7.5,7.5]:
   parts.append(m.Manifold.cylinder(10,2.6,.9,24).rotate((-17,0,0)).translate((cx+dx,-34,31)))
   # Broad side fins reference the dragon's flared cheek/ear silhouette.
   parts.append(m.Manifold.hull_points([[cx+dx,-36,23],[cx+dx*1.9,-31,31],[cx+dx*1.3,-28,24],[cx+dx,-34,30],[cx+dx*1.8,-29.4,30]]))
  for y in [-17,-8,1]:
   parts.append(m.Manifold.hull_points([[cx-2,y-4,29],[cx+2,y-4,29],[cx-1.2,y,36],[cx+1.2,y,36],[cx-2,y+5,28],[cx+2,y+5,28]]))
  # Whiskers are deliberately broad relief curves fused to the cheek, not thin free wires.
  for s in [-1,1]:parts.append(tube([(cx+s*8,-46,24),(cx+s*12,-42,23),(cx+s*13,-36,25)],1.0))
 else:
  for dx in [-9.2,9.2]:parts.append(ball(cx+dx,-31,31,4.6,3.7,4.2))
  # Raised stripes are schematic geometry on the actual printable body.
  for y in [-24,-18,-12,-6,0,6]:
   k=math.sqrt(max(.05,1-((y+11)/24)**2));pts=[]
   for a in np.linspace(.10,math.pi-.10,25):pts.append((cx+14*k*math.cos(a),y,19+12*k*math.sin(a)))
   parts.append(tube(pts,.55))
  # Tail curls back into the body to avoid an unsupported thin tip.
  parts.append(tube([(cx+11,4,18),(cx+17,6,21),(cx+18,10,26),(cx+14,13,28),(cx+10,10,26)],1.8))
# Short continuous deck rails at rear, simplified posts all rooted in the foundation.
for cx in [-36,36]:
 for x in [cx-23,cx+23]:
  parts.append(box(x,17,6.8,1.6,39,2.5))
  for y in [0,10,20,30]:parts.append(box(x,y,7.3,2.6,2.6,4.6))
result=m.Manifold.batch_boolean(parts,m.OpType.Add).set_tolerance(.0001).simplify(.007)
mesh=result.to_mesh64();tm=trimesh.Trimesh(np.asarray(mesh.vert_properties)[:,:3],np.asarray(mesh.tri_verts),process=True);tm.fix_normals()
(OUT/'model.stl').write_text(trimesh.exchange.stl.export_stl_ascii(tm))
print('Status:',result.status(),'size:',tm.extents,'watertight:',tm.is_watertight,'components:',len(tm.split()),'triangles:',len(tm.faces))
