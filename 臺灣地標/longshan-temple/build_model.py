"""Bangka Lungshan Temple, Taipei: original 150 mm solid exterior.
Official photo and public massing diagram: https://www.lungshan.org.tw/tw/03_1_9_art.php
The San-chuan front hall, central double-eaved hall, rear group, side galleries,
and two six-sided bell/drum towers follow the specific public arrangement.
Run: python build_model.py [--output model.stl]. Units: mm.
"""
from pathlib import Path
import argparse,math
import numpy as np
import manifold3d as m
import trimesh
OUT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=OUT/'model.stl');a=p.parse_args()
parts=[];cuts=[]
def box(x,y,z,w,d,h):return m.Manifold.cube((w,d,h),True).translate((x,y,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cyl(x,y,z,r,h,n=24):return m.Manifold.cylinder(h,r,r,n).translate((x,y,z))
def tube(p,q,r=.55):
 p=np.array(p);q=np.array(q);v=q-p;length=np.linalg.norm(v);u=v/length;ref=np.array([0,0,1.])
 if abs(u@ref)>.96:ref=np.array([1.,0,0])
 e=np.cross(u,ref);e/=np.linalg.norm(e);f=np.cross(u,e)
 p=p-u*.18;q=q+u*.18
 pts=[o+r*(e*math.cos(t)+f*math.sin(t)) for o in [p,q] for t in np.linspace(0,2*math.pi,8,endpoint=False)]
 return m.Manifold.hull_points(pts)
def roofheight(u,v,h,up):
 ax=abs(u);ay=abs(v);hip=min(1.,max(0,(1-ax)/.27))
 return h*min((1-ay)**1.45,hip)+up*(ax**8+ay**8)*(.35+.65*ax*ay)
def roof(x,y,z,w,d,h,up=1.4, ribs=True):
 # Closed heightfield solid, filled below all roof surfaces. No roof cavity.
 nx=48 if ribs else 24;ny=24;vs=[]
 for zz in [0,1]:
  for j in range(ny+1):
   v=-1+2*j/ny
   for i in range(nx+1):
    u=-1+2*i/nx;vs.append([x+u*w/2,y+v*d/2,z+roofheight(u,v,h,up)+(0.38*(i%2)*math.sin(math.pi*j/ny)**.25 if ribs else 0) if zz else z-.8])
 n=(nx+1)*(ny+1);fs=[]
 for j in range(ny):
  for i in range(nx):
   k=j*(nx+1)+i
   fs.extend([[k,k+nx+1,k+1],[k+1,k+nx+1,k+nx+2],[n+k,n+k+1,n+k+nx+1],[n+k+1,n+k+nx+2,n+k+nx+1]])
 perimeter=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
 for k,l in zip(perimeter,perimeter[1:]+perimeter[:1]):fs.extend([[k,l,n+k],[l,n+l,n+k]])
 mm=m.Manifold(m.Mesh(np.array(vs,dtype=np.float32),np.array(fs,dtype=np.uint32)));assert mm.status()==m.Error.NoError,mm.status();parts.append(mm)
 # Tile ribs are integrated directly into the heightfield, avoiding sliver unions.
 rr=w*.36
 parts.append(box(x,y,z+h-.6,w*.72,1.4,2.4))
 # Simplified upward-swept dragon / swallow-tail silhouette, fused solid.
 for side in [-1,1]:
  xx=x+side*rr
  crest=[(xx-side*3.5,z+h-.25),(xx-side*2.0,z+h+1.1),(xx-side*.5,z+h+1.5),(xx+side*1.0,z+h+3.4),(xx+side*2.0,z+h+3.6),(xx+side*1.55,z+h+1.0),(xx+side*.3,z+h-.8)]
  if sum(crest[i][0]*crest[(i+1)%len(crest)][1]-crest[(i+1)%len(crest)][0]*crest[i][1] for i in range(len(crest)))<0:crest.reverse()
  cs=m.CrossSection([[list(t) for t in crest]])
  parts.append(cs.extrude(1.4).rotate((90,0,0)).translate((0,y+.7,0)))
 return z+h

def arch(w,h,depth):
 r=w/2;pts=[[-r,0],[r,0]]+[[r*math.cos(t),h-r+r*math.sin(t)] for t in np.linspace(0,math.pi,17)]
 return m.CrossSection([pts]).extrude(depth).rotate((90,0,0)).translate((0,depth,0))
def relief(x,y,z,w,h,d=1.1,angle=0):cuts.append(arch(w,h,d).rotate((0,0,angle)).translate((x,y,z)))
def hall(x,y,w,d,wallh,roofh,double=False):
 add(x,y,3.5+wallh/2,w-2,d-2,wallh+1)
 add(x,y,5,w-1,d-1,2)
 # Engaged columns, no unsupported open galleries at this small scale.
 for yy in [-d/2+1.5,d/2-1.5]:
  for xx in np.linspace(-w/2+3,w/2-3,7):
   parts.append(cyl(x+xx,y+yy,5,.75,wallh-1));add(x+xx,y+yy,wallh+3,2.0,2.1,1.1)
 z=wallh+3.1
 if double:
  roof(x,y,z,w,d,3.1,1.4)
  add(x,y,z+2.8,w*.71,d*.67,4.0)
  return roof(x,y,z+4.0,w*.83,d*.79,roofh,1.8)
 return roof(x,y,z,w,d,roofh,1.7)
# Compact rectangular enclosure, with substantial open courts and perimeter path.
add(0,0,1.5,142,150,3)
# Side galleries connect the complete complex. Front is negative Y.
for sx in [-1,1]:
 add(sx*59,6,10,13,123,14)
 idx=len(parts);roof(0,0,16.7,125,16,3.0,.65,False)
 for k in range(idx,len(parts)):parts[k]=parts[k].rotate((0,0,90)).translate((sx*59,6,0))
 for yy in range(-37,57,12):
  # Flat rectangular exterior panels; gallery walls remain solid.
  cuts.append(box(sx*65.3,yy,9.5,1.6,5.0,5.5))
# Front central San-chuan hall and distinct lower left/right dragon/tiger entries.
hall(0,-46,70,25,13.0,8.0,False)
for sx in [-1,1]:
 hall(sx*49,-46,27,23,11,6.2,False)
 relief(sx*49,-58.2,4.2,6.2,8.7,1.7)
# Front entrance rhythm, central doors and octagonal stone windows.
for xx in [-24,-12,0,12,24]:
 cuts.append(box(xx,-58,9.0,5.5,5.0,9.0))
for xx in [-30,30]:
 win=m.Manifold.cylinder(3.5,3.2,3.2,8).rotate((90,0,0)).translate((xx,-55,10.2));cuts.append(win)
# Triple shallow front stair, footprint unites with main plinth.
for i in range(3):
 top=3.65+i*.5;add(0,-61+i*.8,(2.8+top)/2,29-i*1.8,4.5,top-2.8)
# Bell/drum towers stand immediately behind front side halls, as public diagram.
for sx in [-1,1]:
 x=sx*49;y=-22
 parts.append(m.Manifold.cylinder(17.5,7.5,7.5,6).rotate((0,0,30)).scale((1.14,.9,1)).translate((x,y,3)))
 # Three flattened hexagonal roofs. Thick solid flared eaves preserve silhouette.
 for z,rad,h in [(17.1,11.6,3.6),(23.3,10.2,3.2),(28.8,9.4,4.1)]:
  parts.append(m.Manifold.cylinder(h,rad,rad*.42,6).rotate((0,0,30)).scale((1.12,.84,1)).translate((x,y,z)))
  if z<28:parts.append(m.Manifold.cylinder(5.4,6.4,6.4,6).rotate((0,0,30)).scale((1.12,.84,1)).translate((x,y,z+1.2)))
  for angle in np.linspace(30,390,6,endpoint=False):
   t=math.radians(angle);pa=(x+rad*.7*math.cos(t)*1.12,y+rad*.7*math.sin(t)*.84,z+1);pb=(x+rad*math.cos(t)*1.12,y+rad*math.sin(t)*.84,z+2.2);parts.append(tube(pa,pb,.70))
 parts.append(cyl(x,y,32.1,1.3,3.1));parts.append(m.Manifold.sphere(1.65,12).translate((x,y,35.0)))
 relief(x,y-7.4,6.5,4.5,8.6,1.6)
# Central main hall is isolated by open exterior courtyard on all sides.
# Its solid platform and low front terrace are continuous with the common base.
add(0,9,4.9,58,41,4)
add(0,-13.5,4.6,25,14,3.4)
hall(0,9,65,44,15.2,7.0,True)
for sx in [-1,1]:
 for i in range(4):
  top=3.7+i*.5;add(sx*20,-15.5+i*.9,(2.8+top)/2,10,5,top-2.8)
for xx in [-18,-9,0,9,18]:cuts.append(box(xx,-12.5,11.3,5.2,4.0,10.0))
# Three rear halls: tall central double-eaved Shengmu Hall with lower end halls.
hall(0,54,70,26,13.4,6.8,True)
for sx in [-1,1]:
 hall(sx*48,54,28,27,12,6.2,False)
 # Fill tiny pockets where the rear hip and side-gallery roof intersect.
 add(sx*48,54,9.4,28,27,13.2)
for xx in np.linspace(-25,25,7):cuts.append(box(float(xx),41.1,10,4.8,3.5,8))
# Back wall simplified relief rather than fabricated interior windows.
for xx in range(-54,55,12):add(xx,65.3,9.5,.9,1.2,13.4)
# Courtyard central incense burner: deliberately omitted to keep focus on buildings.
body=m.Manifold.batch_boolean(parts,m.OpType.Add)-m.Manifold.batch_boolean(cuts,m.OpType.Add)
assert body.status()==m.Error.NoError,body.status()
body=body.as_original().set_tolerance(.01).simplify(.01)
mesh=body.to_mesh();tm=trimesh.Trimesh(vertices=mesh.vert_properties[:,:3],faces=mesh.tri_verts,process=True)
a.output.parent.mkdir(parents=True,exist_ok=True);tm.export(a.output)
print(a.output,'triangles',len(tm.faces),'dimensions',tm.extents.tolist(),'watertight',tm.is_watertight)
