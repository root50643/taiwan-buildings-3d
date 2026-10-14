"""大成館原創有界外觀草稿。m參數轉mm；前=-Y，地理東偏南。
2003側背、校方正照及2024正射跨年。名義低翼49×51m，非測繪。
"""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection,Mesh64
R=Path(__file__).resolve().parent;S=2.6;BASE=1.6
parts=[];cuts=[];late=[]
def box(x0,y0,x1,y1,a,b):return Manifold.cube(((x1-x0)*S,(y1-y0)*S,(b-a)*S)).translate((x0*S,y0*S,BASE+a*S))
def add(*a):parts.append(box(*a))
def cut(*a):cuts.append(box(*a))
def cyl(x,y,r,a,b,collection=parts):collection.append(Manifold.cylinder((b-a)*S,r*S,r*S,32).translate((x*S,y*S,BASE+a*S)))
def beam(x0,y0,x1,y1,w,a,b,collection=parts):
 v=np.array([x1-x0,y1-y0]);n=np.array([-v[1],v[0]])/np.linalg.norm(v)*w/2
 p=np.array([[x0,y0],[x1,y1],[x1,y1],[x0,y0]])+np.array([n,n,-n,-n]);p=p[::-1]
 collection.append(CrossSection([p*S]).extrude((b-a)*S).translate((0,0,BASE+a*S)))
# Common connected base and bounded gently stepped terrain: rear rises ~one level.
parts.append(Manifold.cube((146,150,BASE)).translate((-73,-75,0)))
for j in range(8):add(-27,-26+j*6.7,27,27,-.03,.15+j*.36)
# Main lower body and four lower corner wings; central upper court has a solid floor.
add(-21,-22,21,23,-.03,9.0)
for x0,x1 in [(-24.5,-9.5),(9.5,24.5)]:
 for y0,y1 in [(-25.5,-10),(10,25.5)]:add(x0,y0,x1,y1,-.03,9.0)
# Front portico: continuous landing beneath all four high columns.
add(-9.5,-25.5,9.5,-19,-.03,.72)
add(-9.5,-24.7,9.5,-22.8,8.7,9.15)
# Four tall round columns and five bays, not a repeated window wall.
cut(-9.5,-26,9.5,-19.0,.72,8.8)
for x in [-5.7,-1.9,1.9,5.7]:cyl(x,-24.2,.33,.55,9.1,late)
# Five recessed door/window fields behind portico, backed; horizontal division at 4m.
for x in np.linspace(-8.6,6.7,5):
 cut(x,-19.1,x+2.6,-18.65,.9,3.6);cut(x,-19.1,x+2.6,-18.65,4.25,7.8)
# Entrance stairs kept away from the column feet and plate.
for i in range(7):add(-9.5,-28+i*.4,9.5,-24.7,-.03,.15+i*.09)
# Four upper room wings at 3rd level; preserve corner terraces.
add(-16.7,-23.8,16.7,-9.3,8.7,12.85)
add(-16.7,10.4,16.7,23.8,8.7,12.85)
add(-21,-12,-10.2,12,8.7,12.85);add(10.2,-12,21,12,8.7,12.85)
# Fourth-level rooms sit further back behind real open colonnades.
add(-11.8,-20.2,11.8,-9.3,12.55,15.9)
add(-11.8,10.4,11.8,20.2,12.55,15.9)
add(-20.0,-11,-10.2,11,12.55,15.9);add(10.2,-11,20,11,12.55,15.9)
# Floor plates under highest external gallery and internal court gallery.
add(-13,-23,13,-9.3,12.5,12.95);add(-13,10.4,13,23,12.5,12.95)
add(-23,-11.7,-10.2,11.7,12.5,12.95);add(10.2,-11.7,23,11.7,12.5,12.95)
# Court floor is atop lower lecture rooms, not a hole through model.
add(-11.9,-12.1,11.9,12.1,8.65,9.15)
# Highest gallery support columns and railing, finite roots and 1mm+ diameter.
for yy in [-22.35,22.35]:
 for xx in np.linspace(-11.7,11.7,7):cyl(xx,yy,.24,12.8,16.35)
for xx in [-22.3,22.3]:
 for yy in np.linspace(-10.5,10.5,8):cyl(xx,yy,.24,12.8,16.35)
# Inner court colonnade is a deep recess into room faces; retain structural backs.
for yy in [-9.3,10.4]:
 for xx in np.linspace(-8.9,8.9,7):
  if yy<0:cut(xx-.95,yy-.5,xx+.95,yy+.2,13.3,15.5)
  else:cut(xx-.95,yy-.2,xx+.95,yy+.5,13.3,15.5)
for xx in [-10.2,10.2]:
 for yy in np.linspace(-9.5,9.5,7):
  if xx<0:cut(xx-.45,yy-1,xx+.15,yy+1,13.3,15.5)
  else:cut(xx-.15,yy-1,xx+.45,yy+1,13.3,15.5)
# Railings simplified to thick top/bottom bands with posts, no loose micro-balusters.
def rail(a,b,h):
 beam(*a,*b,.4,h,h+.28);beam(*a,*b,.4,h+.72,h+1.04)
 n=max(2,int(np.linalg.norm(np.array(b)-a)/2.5)+1)
 for p in np.linspace(a,b,n):add(p[0]-.22,p[1]-.22,p[0]+.22,p[1]+.22,h-.12,h+1.08)
for yy in [-22.35,22.35]:rail((-12.5,yy),(12.5,yy),12.9)
for xx in [-22.35,22.35]:rail((xx,-11.6),(xx,11.6),12.9)
# Four lower terraces, perimeter only; taller inner room walls remain separate.
for x0,x1 in [(-24.5,-9.5),(9.5,24.5)]:
 for y0,y1 in [(-25.5,-10),(10,25.5)]:
  for a,b in [((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]:rail(a,b,9)
# Middle frontal five large glass bays and one balcony, thin frames fused to back.
for x in np.linspace(-8.9,5.6,5):
 cut(x,-24.0,x+3.1,-23.48,9.4,12.35)
 late.append(box(x+1.4,-23.66,x+1.6,-23.30,9.35,12.4))
 late.append(box(x,-23.65,x+3.1,-23.30,11.35,11.50))
rail((-9.2,-24.3),(9.2,-24.3),9.0)
# Highest front and rear windows are behind the column line, not through the wall.
for yy in [-20.2,20.2]:
 for x in np.linspace(-10.8,7.8,6):
  cut(x,yy-.2 if yy<0 else yy-.25,x+2.5,yy+.25 if yy<0 else yy+.2,13.35,15.3)
# Side facades: eight main bays, three visible window rows per 2003 rectification.
for side in [-1,1]:
 for y in np.linspace(-10.6,8.1,8):
  for lo,hi in [(1.05,3.5),(4.25,6.85),(9.35,12.3)]:
   x=21*side;cut(x-.28,y,x+.28,y+2.25,lo,hi)
   # A fine center mullion sits in the recess, with >0.5mm overlap into backing.
   # Minor historic glazing mullions omitted at this scale; one broad backed pane per bay.
 # Corner outer side has paired large windows, third row is terrace (no full-height corner).
 for y in [-23.7,-20.1,-16.5,12,15.6,19.2,22.6]:
  for lo,hi in [(1.2,3.2),(4.4,6.7)]:
   x=24.5*side;cut(x-.28,y,x+.28,y+2.4,lo,hi)
# Front corner monumental blank panels and narrow decorative recesses, no window grid.
for x in [-21.5,20.4]:
 for lo,hi in [(1.5,2.8),(3.7,5),(6.0,7.1)]:cut(x,-25.7,x+1.1,-25.25,lo,hi)
 add(x-.35,-25.8,x+1.45,-25.25,7.5,7.9)
# Rear low elevation, larger round window and paired rectangular groups per 2003 photos.
for x in [-20.8,-17.5,15,18.3,21.6]:
 for lo,hi in [(3.1,4.9),(5.65,7.7)]:cut(x,25.23,x+2.0,25.7,lo,hi)
# Rear central round window in the recessed midbody, shallow backing and integral cross.
r=Manifold.cylinder(.65*S,1.45*S,1.45*S,48).rotate((90,0,0)).translate((0,23.3*S,BASE+5.9*S));cuts.append(r)
late.append(box(-.12,22.4,.12,22.85,4.45,7.35));late.append(box(-1.45,22.4,1.45,22.85,5.8,6.0))
for x in [-10.4,-7.0,5,8.4]:
 for lo,hi in [(3.2,4.9),(9.5,11.65)]:cut(x,22.7 if lo<5 else 23.55,x+2.2,23.3 if lo<5 else 24,lo,hi)
# Original mesh roofs: curved finite-thickness surfaces, authored grid, not borrowed mesh.
def roof(cx,cy,W,D,eave,rise,kind='hip',turn=False):
 # X is ridge direction. Hip front, hip-and-gable side, rounded rear barrel ridge.
 xs=np.unique(np.r_[np.linspace(-W/2,W/2,21),[-W*.25,W*.25]])
 ys=np.unique(np.r_[np.linspace(-D/2,D/2,15),[-.24,.24]])
 vv=[]
 for lower in [False,True]:
  for y in ys:
   for x in xs:
    ty=max(0,(abs(y)-.24)/(D/2-.24))
    tx=max(0,(abs(x)-W*.25)/(W*.25))
    if kind=='hip':t=max(ty,tx);h=rise*(1-t)**1.55
    elif kind=='gable':
     # Lower hipped skirt meets an upper exposed triangular gable.
     h=rise*(1-ty)**1.55
     if abs(x)>W*.40:h=min(h,.9*(1-(abs(x)-W*.40)/(W*.1)))
    else:h=rise*np.cos(min(1,ty)*np.pi/2)**1.25
    uplift=.10*max(ty,tx)**8
    z=(eave-.48) if lower else eave+h+uplift
    xx,yy=(y,x) if turn else (x,y);vv.append([(cx+xx)*S,(cy+yy)*S,BASE+z*S])
 nx=len(xs);ny=len(ys);N=nx*ny;ff=[]
 for j in range(ny-1):
  for i in range(nx-1):
   a=j*nx+i;b=a+1;c=a+nx;d=c+1
   ff.extend([[a,b,d],[a,d,c],[a+N,d+N,b+N],[a+N,c+N,d+N]])
 ring=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+[ (ny-1)*nx+i for i in range(nx-2,-1,-1)]+[j*nx for j in range(ny-2,0,-1)]
 for i,a in enumerate(ring):b=ring[(i+1)%len(ring)];ff.extend([[a,a+N,b+N],[a,b+N,b]])
 if turn:ff=[f[::-1] for f in ff]
 q=Manifold(Mesh64(np.array(vv),np.array(ff,dtype=np.uint64)));assert q.status().name=='NoError';parts.append(q)
 # finite ridge trim, omitted on rear barrel.
 if kind!='barrel':
  if turn:add(cx-.22,cy-W*.25,cx+.22,cy+W*.25,eave+rise-.15,eave+rise+.25)
  else:add(cx-W*.25,cy-.22,cx+W*.25,cy+.22,eave+rise-.15,eave+rise+.25)
roof(0,-16.5,27.0,16.8,16.2,3.15,'hip')
roof(0,18.0,22.4,14.8,16.2,2.65,'barrel')
roof(-18.1,0,24.8,14.7,16.2,2.65,'gable',True)
roof(18.1,0,24.8,14.7,16.2,2.65,'gable',True)
# Gallery roof-edge beams connect every column and support finite eaves.
for yy in [-22.35,22.35]:add(-12.6,yy-.3,12.6,yy+.3,15.75,16.45)
for xx in [-22.3,22.3]:add(xx-.3,-11.8,xx+.3,11.8,15.75,16.45)
# Construction coordinate quantization precedes Boolean, no final mesh repair.
def grid(p):
 m=p.to_mesh64();return Manifold(Mesh64(np.ascontiguousarray(np.round(m.vert_properties,5)),np.array(m.tri_verts,dtype=np.uint64,copy=True)))
parts=[grid(p) for p in parts];cuts=[grid(p) for p in cuts];late=[grid(p) for p in late]
solid=Manifold.batch_boolean(parts, __import__('manifold3d').OpType.Add)
solid=solid-Manifold.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
solid=solid+Manifold.batch_boolean(late,__import__('manifold3d').OpType.Add)
assert solid.status().name=='NoError'
m=solid.to_mesh64();mesh=trimesh.Trimesh(np.array(m.vert_properties[:,:3],dtype=np.float32),np.array(m.tri_verts),process=False)
mesh.export(R/'model.stl');print(len(mesh.faces),mesh.extents,mesh.is_watertight,len(mesh.split(only_watertight=False)))
