"""崑山圖書資訊館有界草稿。官方55m總高口徑，非實測逐層；2022頂與建築師兩面交叉。"""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection,Mesh64,OpType
R=Path(__file__).parent;S=1.5;B=1.6;parts=[];cuts=[];late=[]
def poly(p,a,b):
 p=np.asarray(p,float)*S
 if np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])<0:p=p[::-1]
 return CrossSection([p.tolist()]).extrude((b-a)*S).translate((0,0,B+a*S))
def box(x0,y0,x1,y1,a,b):return poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],a,b)
def add(*a):parts.append(box(*a))
def cut(*a):cuts.append(box(*a))
def semi(cx,cy,rx,ry):return [(cx-rx,cy+1),(cx+rx,cy+1)]+[(cx+rx*np.cos(t),cy-ry*np.sin(t))for t in np.linspace(0,np.pi,49)]
def loft(sections):
 verts=[];faces=[];n=len(sections[0][1])
 for z,p in sections:verts.extend([(x*S,y*S,B+z*S)for x,y in p])
 for k in range(len(sections)-1):
  for i in range(n):a=k*n+i;b=k*n+(i+1)%n;c=(k+1)*n+(i+1)%n;d=(k+1)*n+i;faces.extend([(a,b,c),(a,c,d)])
 for i in range(1,n-1):faces.extend([(0,i+1,i),((len(sections)-1)*n,(len(sections)-1)*n+i,(len(sections)-1)*n+i+1)])
 m=trimesh.Trimesh(verts,faces,process=False)
 if m.volume<0:m.invert()
 return Manifold(Mesh64(np.ascontiguousarray(m.vertices),np.asarray(m.faces,dtype=np.uint64)))
parts.append(Manifold.cube((150,100,B)).translate((-75,-50,0)))
# Main floor plates and north three-tier retreats; no full exposed basement ring.
add(-43,-23,43,14,-.03,5.6)
add(-42,-22,42,-9,5.5,23.2)
add(-36,-15,38,10,5.5,29.0)
add(-36,-8,39,10,5.5,46.0)
# Western vertical service tower, official nominal highest endpoint55m; antenna omitted.
add(-43,-6,-34,12,-.03,52)
add(-44.2,-4,-41.6,13,-.03,55)
add(-43.7,9,-39.5,13,49,54.8)
cut(-44.4,-2.8,-43.95,10.8,6,50)
for z in np.arange(6,51,4.4):late.append(box(-44.22,-3,-43.6,11,z,z+.4))
# West lower stepped red terraces visible from south.
for xa,xb,yy,h in [(-42,-29,19,10),(-29,-17,23,17),(-17,-5,21,26)]:add(xa,8,xb,yy,-.03,h)
# Visible south-facing red terrace windows belong to each actual stepped face.
for xa,xb,yy,h in [(-42,-29,19,10),(-29,-17,23,17),(-17,-5,21,26)]:
 for x in [xa+3.1,xb-3.1]:
  for lo in [2,7,12,17,22]:
   if lo+3<h-.5:cut(x-1.75,yy-.22,x+1.75,yy+.2,lo,lo+3)
# Narrow east-west upper roof and southern white deep-window screen.
add(-22,1.4,28,11,45.7,49.5)
add(-22,10,28,11.5,39.8,49.5)
for x in [-17,-12.5,-6.5,-2]:
 for lo,hi in [(41.35,43.15),(45.65,47.45)]:cut(x-1.6,8.0,x+1.6,12,lo,hi)
# North central inclined bow: smaller at bottom, wider at top; behind joins solid core.
def scaled_extrusion(points,lo,hi,sx,sy,cx,cy):
 p=np.asarray(points,float)*S
 if np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])<0:p=p[::-1]
 return CrossSection([p.tolist()]).extrude((hi-lo)*S,scale_top=(sx,sy)).translate((cx*S,cy*S,B+lo*S))
bow=scaled_extrusion(semi(0,0,10.5,11),23,39.6,15.5/10.5,13.8/11,5,-5);parts.append(bow)
# Curved glass cutters are direct closed scaled cross-sections, without coplanar nested cutter caps.
def wedge(cx,cy,t0,t1,lo,hi):
 return poly([(cx,cy),(cx+60*np.cos(t0),cy-60*np.sin(t0)),(cx+60*np.cos(t1),cy-60*np.sin(t1))],lo,hi)
# One continuous inner curved cutter shared by all horizontal rows. Constant-angle
# plane boundaries avoid separately scaled near-coincident sliver edges at mullions.
inner_bow=scaled_extrusion(semi(0,0,10.3,10.8),23,39.6,15.3/10.3,13.6/10.8,5,-5)
bow_shell=box(-50,-45,50,5,23,39.6)-inner_bow
for lo,hi in [(23.5,26.6),(26.8,28.9),(29.0,29.8),(30,33),(33.2,36.2),(36.4,39.2)]:
 for a,b in zip(np.linspace(.04,np.pi-.04,13)[:-1],np.linspace(.04,np.pi-.04,13)[1:]):
  cuts.append(bow_shell ^ wedge(5,-5,a+.008,b-.008,lo,hi) ^ box(-50,-40,50,-15.01 if hi<29 else -8.01,lo,hi))
parts.append(poly(semi(7,-3.6,13.8,9.5),39.5,44.6))
# High rounded roof enclosure: plan semicircle with flat roof, not a half sphere.
parts.append(poly(semi(10,-3.8,15.3,15.2),44.5,50.8))
for cx,cy,rx,ry,rows in [(7,-3.6,13.8,9.5,[(40.2,41.6),(41.74,43.4),(43.54,43.9)]),(10,-3.8,15.3,15.2,[(45.3,46.6),(46.74,48.4),(48.54,50)])]:
 for aa,bb in rows:
  shell=box(-60,-50,60,5,aa,bb)-poly(semi(cx,cy,rx-.18,ry-.18),aa-.1,bb+.1)
  for a,b in zip(np.linspace(.04,np.pi-.04,16)[:-1],np.linspace(.04,np.pi-.04,16)[1:]):
   cuts.append(shell ^ wedge(cx,cy,a+.007,b-.007,aa-.1,bb+.1) ^ box(-50,-40,50,-8.01,aa-.1,bb+.1))
# South offset curved wing: eastern tall bowed wall, western lower terraces are separate.
def southline():return [(x,24-0.0088*(x+5)**2)for x in np.linspace(-5,28,49)]
line=southline();wall=line+[(x,y-4.1)for x,y in line[::-1]]
parts.append(poly(wall,4.8,37.0))
# Exposed horizontal links across the local slot, not a full filled-in courtyard.
for h in [5.0,10.2,15.4,20.6,25.8,31.0,36.2]:
 for x in [-4,13,27]:add(x-.75,8.5,x+.75,23-0.0088*(x+5)**2,h,h+.9)
# Curved south glazing recess, distinct five high tiers and a top open beam slot.
for lo,hi in [(7,11),(12.2,16.2),(17.4,21.4),(22.6,26.6),(27.8,31.3)]:
 for xa,xb in [(-3,1),(3,7),(9,10.7),(12.5,15.89),(16.11,19.89),(20.11,23.89),(24.11,27)]:
  pts=[(x,24-0.0088*(x+5)**2+.10)for x in np.linspace(xa,xb,17)];p=pts+[(x,y-.38)for x,y in pts[::-1]];cuts.append(poly(p,lo,hi))
for xa,xb in [(-3,3),(5,11),(13,19),(21,26)]:
 pts=[(x,24-0.0088*(x+5)**2+.12)for x in np.linspace(xa,xb,17)];p=pts+[(x,y-4.6)for x,y in pts[::-1]];cuts.append(poly(p,32.3,35.5))

# End glass stair towers; backed recessed glazing and strong horizontal slabs.
for x in [-29,31]:
 add(x-1.9,12,x+1.9,16,0,43)
 for lo in np.arange(2,40,4.5):
  if x>0 or lo>=10:cut(x-1.5,15.72,x+1.5,16.2,lo,lo+3.5)
 for z in np.arange(1.3,42,3):late.append(box(x-1.9,15.45,x+1.9,16.08,z,z+.5))
# North front windows: paired groups, three visible rows above the true colonnade.
for x in [-37,-29,-21,-13,-5,5,13,21,29,37]:
 for lo,hi in [(7,10.4),(12.3,15.7),(17.6,21.0)]:
  for dx in [-1.2,1.2]:cut(x+dx-.9,-22.2,x+dx+.9,-21.78,lo,hi)
# Mid setback has one principal band; upper flanks have low windows and two recessed rows.
for x in [-31,-23,-15,29,35]:
 cut(x-1.6,-15.2,x+1.6,-14.78,24.2,27.7)
for centers in [[-33,-28,-23,-18,-13],[23,27.5,32,36.5]]:
 for x in centers:
  for lo,hi in [(30,33),(35,38)]:cut(x-1.4,-8.2,x+1.4,-7.78,lo,hi)
  for lo,hi in [(39.4,41.7),(42.6,45.1)]:cut(x-1.9,-8.3,x+1.9,-5.8,lo,hi)
# South red upper field with large independent windows; unknown west short face simplified.
for x in [-30,-23,-16,-9,-2,5,12,19,26,33]:
 for lo in [7,12,17,22,27,32,37]:
  minimum=10 if x<-29 else 17 if x<-17 else 26 if x<-5 else 0
  if lo>=minimum:cut(x-1.5,9.78,x+1.5,10.2,lo,lo+3)
# Open north colonnade below building: a real void, closed only at inner wall.
cut(-42,-24,42,-16,1.0,5.3)
# Late supported entrance/columns keep facade recess differences from biting into structural roots.
for x in [-41,-34,-27,-20,-13,13,20,27,34,41]:late.append(box(x-.7,-26,x+.7,-24.4,.6,6.3))
late.append(box(-44,-27,44,-16,5.3,6.6))
for x in [-8.2,6.7]:late.append(box(x,-29,x+1.5,-26,.6,12))
late.append(box(-8.2,-29,8.2,-20,10.5,12.3))
# Broad finite forecourt steps and rear local ramp; no invented full terrain.
add(-45,-30,45,-22,-.03,.7)
for i in range(4):add(-14+i*.04,-32+i*.45,14-i*.04,-29.5,-.03,.15+i*.15)
add(36,12,44,20,-.03,.8)
# Original double-precision primitives before union; no post-CSG or STL repair.
def grid(p):
 m=p.to_mesh64();return Manifold(Mesh64(np.array(m.vert_properties,dtype=np.float64,copy=True),np.array(m.tri_verts,dtype=np.uint64,copy=True)))
solid=Manifold.batch_boolean([grid(p)for p in parts],OpType.Add)-Manifold.batch_boolean([grid(p)for p in cuts],OpType.Add)
solid+=Manifold.batch_boolean([grid(p)for p in late],OpType.Add)
# Source image y points south; convert once to physical north-positive model Y.
solid=solid.scale((1,-1,1))
assert solid.status().name=='NoError';m=solid.to_mesh64();mesh=trimesh.Trimesh(np.array(m.vert_properties[:,:3],dtype=np.float32),np.array(m.tri_verts),process=False);mesh.export(R/'model.stl');print(mesh.extents,len(mesh.faces),mesh.is_watertight,len(mesh.split(only_watertight=False)))
