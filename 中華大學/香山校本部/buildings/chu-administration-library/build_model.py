"""中華大學行政暨圖資大樓：官方平面＋NLSC＋跨年照片有界原創模型。"""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection,Mesh64,OpType
R=Path(__file__).resolve().parent;S=1.75;B=1.6;parts=[];cuts=[];late=[]
def poly(p,a,b):
 p=np.asarray(p)*S
 if np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])<0:p=p[::-1]
 return CrossSection([p.tolist()]).extrude((b-a)*S).translate((0,0,B+a*S))
def box(x0,y0,x1,y1,a,b):return poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],a,b)
def add(*a):parts.append(box(*a))
def cut(*a):cuts.append(box(*a))
def cyl(x,y,r,a,b):return Manifold.cylinder((b-a)*S,r*S,r*S,48).translate((x*S,y*S,B+a*S))
def xzshape(p,y0,y1):
 p=np.array([[x*S,B+z*S]for x,z in p]);
 if np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])<0:p=p[::-1]
 q=CrossSection([p.tolist()]).extrude((y1-y0)*S)
 return q.transform(np.array([[1,0,0,0],[0,0,-1,y1*S],[0,1,0,0]],float))
def arch(r,b,spring):return [(-r,b),(r,b)]+[(r*np.cos(t),spring+r*np.sin(t))for t in np.linspace(0,np.pi,33)]
parts.append(Manifold.cube((150,100,B)).translate((-75,-50,0)))
# Main 60 x 34.5m rectangular building. All z values are photo-bounded.
add(-30,-17.25,30,17.25,-.03,28)
# South central lower extension shown in 1F/2F plans, not a second building.
add(-12,-23,12,-16.9,-.03,7.8)
# Front platform and finite broad stairs.
add(-14,-24,14,-20,-.03,.8)
for i in range(5):add(-14,-26+i*.4,14,-23.8,-.03,.15+i*.13)
# Glazed central lower extension; avoid presenting the occupied rooms as a blank plinth.
for lo,hi in [(1.1,3.5),(4.5,7.35)]:
 cut(-11.4,-23.3,11.4,-22.65,lo,hi)
 for x in np.linspace(-10.8,10.8,9):
  if not (lo<2 and abs(x)<2.5):late.append(box(x-.10,-22.80,x+.10,-22.60,lo-.03,hi+.03))
 for side in [-1,1]:
  a,b=sorted([side*11.65,side*12.3]);cut(a,-21.8,b,-19.0,lo,hi)
cut(-2.4,-23.4,2.4,-21.8,.8,3.5)
# Horizontal white structural bands represented by modest exterior projection.
for h in [3.8,7.8,11.8,15.8,19.8,23.8,27.8]:
 add(-30.15,-17.43,30.15,17.43,h,h+.32)
for x in [-29.6,-20,-10,-3.33,3.33,10,20,29.6]:
 for y in [-17.3,17.3]:add(x-.20,y-.12,x+.20,y+.12,3.8,28.12)
# Distinct upper tall-window groups, middle wing windows and lower shorter bands.
for face in [-1,1]:
 yout=face*17.7; yin=face*16.88;y0,y1=sorted([yout,yin])
 for h0,h1,groups in [(24.3,27.65,[(-29,-20.8),(-19.2,-14.7),(-9.3,-3.7),(-2.9,2.9),(3.7,9.3),(14.7,19.2),(20.8,29)]),(20.5,23.6,[(-29,-20.8),(-19.2,-14.7),(14.7,19.2),(20.8,29)]),(18.3,19.5,[(-29,-20.8),(-19.2,-14.7),(14.7,19.2),(20.8,29)]),(13.5,15.5,[(-29,-20.8),(-19.2,-14.7),(14.7,19.2),(20.8,29)]),(9.2,11.5,[(-29,-20.8),(-19.2,-14.7),(14.7,19.2),(20.8,29)]),(4.7,7.4,[(-29,-20.8),(-19.2,-14.7),(14.7,19.2),(20.8,29)])]:
  if face==1:
   if h0<9:continue # north foot is tree-obscured; no invented lower row
   groups=[(-29,-12),(-9,9),(12,29)] if h0>24 else [(-29,-12),(12,29)]
  for xa,xb in groups:
   cut(xa,y0,xb,y1,h0,h1)
   pane_count=6 if abs(xa)>20 or abs(xb)>20 else 3 if min(abs(xa),abs(xb))>12 else 5
   for x in (np.linspace(xa,xb,pane_count+1)[1:-1] if face==-1 else []):
    ya,yb=sorted([face*16.84,face*17.04]);late.append(box(x-.10,ya,x+.10,yb,h0-.03,h1+.03))
   if h1-h0>2.5 and face==-1:
    ya,yb=sorted([face*16.84,face*17.04]);late.append(box(xa,ya,xb,yb,h1-.9,h1-.74))
 # Tiny upper side lights beside the inner three-pane groups; source south detail.
 for xa,xb in ([(-14.35,-13.15),(13.15,14.35)] if face==-1 else []):
  for lo,hi in [(26.7,27.65),(22.8,23.6)]:cut(xa,y0,xb,y1,lo,hi)
 # Central large arched glazing recess, distinct from smaller roof ear.
 cuts.append(xzshape(arch(11.2,4.2,10.6),min(face*16.80,face*17.8),max(face*16.80,face*17.8)))
 # Backed fine frame lines clipped to original arch profile; no free small bars.
 glass=xzshape(arch(11.08,4.2,10.6),min(face*16.76,face*17.02),max(face*16.76,face*17.02))
 for x in [-9,-6,-3,0,3,6,9]:late.append(glass ^ box(x-.11,-18,x+.11,18,4.2,22))
 for h in [7.9,11.9,15.9,19.9]:late.append(glass ^ box(-12,-18,12,18,h,h+.22))
# Side slabs, double-height 5F/6F half-round projections, smaller 3F/4F below.
def semi(side,rx,ry):
 p=[(side*29.65,-ry),(side*29.65,ry)]+[(side*(30+rx*np.cos(t)),ry*np.sin(t))for t in np.linspace(np.pi/2,-np.pi/2,49)]
 return p
for side in [-1,1]:
 for rx,ry,lo,hi in [(4.7,7.8,8.1,11.45),(6.5,9,11.6,15.7),(8.7,10.3,15.8,24)]:
  parts.append(poly(semi(side,rx,ry),lo,hi));idx=len(parts)-1
  # Continuous bowed glass belts cut radially into the original source solid only.
  levels=[(lo+.65,hi-.55)] if hi-lo<5 else [(16.5,19.55),(20.35,23.45)]
  for aa,bb in levels:
   ring=poly(semi(side,rx+.15,ry+.15),aa,bb)-poly(semi(side,rx-.25,ry-.25),aa-.1,bb+.1)
   parts[idx]-=ring
   for t in np.linspace(-np.pi/2+.12,np.pi/2-.12,13):
    # Radial backed mullions live inside the broad curved wall.
    xx=side*(30+(rx-.17)*np.cos(t));yy=(ry-.17)*np.sin(t)
    pp=[(side*(30+(rx-dr)*np.cos(ang)),(ry-dr)*np.sin(ang))for dr,ang in [(.50,t-.013),(.08,t-.013),(.08,t+.013),(.50,t+.013)]]
    late.append(poly(pp,aa-.03,bb+.03))
  parts.append(poly(semi(side,rx+.22,ry+.22),lo-.3,lo+.25))
 # One visible supporting column under the smaller projection.
 parts.append(cyl(side*36.1,0,.72,-.03,11.8))
 # Visible flat annular terrace and solid red parapet outside the inset crown.
 parts.append(poly(semi(side,8.92,10.52),23.75,24.65)-poly(semi(side,8.12,9.72),23.7,24.75))
 # Half ellipsoidal glass crown. Finite top cap avoids a microscopic last tip.
 dome=Manifold.sphere(1,64).scale((6.5*S,8.0*S,5*S)).translate((side*29.8*S,0,B+24*S))
 clip=box(29.6,-11,39,11,23.9,28.7) if side>0 else box(-39,-11,-29.6,11,23.9,28.7)
 parts.append(dome ^ clip)
 # Side lower rectangular window bands not full-height half-cylinder.
 for a,b in [(1.3,2.5),(4.7,7.4)]:
  x0,x1=sorted([side*29.65,side*30.2]);cut(x0,-11,x1,11,a,b)
  for yy in np.linspace(-10,10,11):
   x0,x1=sorted([side*29.61,side*29.85]);late.append(box(x0,yy-.1,x1,yy+.1,a-.02,b+.02))
# Mostly flat roof, two narrow long red sloped strips. No all-over pitched roof.
for side in [-1,1]:
 p=[(-30,28.1),(30,28.1),(30,30.5),(-30,30.5)]
 # YZ wedge extrusion along X.
 yz=[(side*17.25,28),(side*13.1,28),(side*13.1,30.8),(side*13.8,30.8),(side*17.25,29)]
 q=xzshape(yz,-30,30).rotate((0,0,90));parts.append(q)
# End screen walls and corner raised piers.
for x in [-29.7,29.7]:add(x-.45,-17.25,x+.45,17.25,27.9,30.8)
for x in [-29.7,29.7]:
 for y in [-16.9,16.9]:add(x-.55,y-.55,x+.55,y+.55,27.9,32.2)
# Four genuinely through-open arch ears, 1m thick, root into roof screens.
for angle,y in [(0,-16.2),(180,-16.2),(90,-29.7),(270,-29.7)]:
 outer=xzshape(arch(3.4,28.3,31),y-.55,y+.55)
 hole=xzshape(arch(2.15,28.8,31),y-.8,y+.8)
 parts.append((outer-hole).rotate((0,0,angle)))
# Long barrel skylight on the flat central roof; solid support below shallow crown.
add(-22,-4.1,22,4.1,27.9,28.4)
p=[(-4,28.2),(4,28.2)]+[(4*np.cos(t),28.2+2.9*np.sin(t))for t in np.linspace(0,np.pi,41)]
parts.append(xzshape(p,-22,22).rotate((0,0,90)))
# Few low rooftop service units, bounded simplified, not exact plant inventory.
for x,y,w,d,h in [(-21,9,3.8,3,2.2),(-12,10,4,3,1.8),(5,10,5,3.5,2),(19,10,4,3,2.3)]:add(x-w/2,y-d/2,x+w/2,y+d/2,27.9,28+h)
for x in [-17,12,23]:parts.append(cyl(x,8,.85,28,29.7))
# Quantize authored primitives before union, never repair exported mesh.
def grid(p):
 m=p.to_mesh64();return Manifold(Mesh64(np.ascontiguousarray(np.round(m.vert_properties,4)),np.array(m.tri_verts,dtype=np.uint64,copy=True)))
solid=Manifold.batch_boolean([grid(p)for p in parts],OpType.Add)-Manifold.batch_boolean([grid(p)for p in cuts],OpType.Add)
solid+=Manifold.batch_boolean([grid(p)for p in late],OpType.Add)
assert solid.status().name=='NoError';m=solid.to_mesh64();mesh=trimesh.Trimesh(np.array(m.vert_properties[:,:3],dtype=np.float32),np.array(m.tri_verts),process=False);mesh.export(R/'model.stl');print(len(mesh.faces),mesh.extents,mesh.is_watertight,len(mesh.split(only_watertight=False)))
