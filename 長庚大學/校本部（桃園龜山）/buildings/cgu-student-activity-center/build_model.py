"""長庚大學活動中心：NLSC投影＋公開照片有界新草稿。
2018灰圖只約束拓撲，外加格網未配準，不當測量尺寸。舊HOLD未改。
"""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection,Mesh64,OpType
R=Path(__file__).resolve().parent;P=.13526818060929474;S=1.18;B=1.6;parts=[];cuts=[];late=[]
def xy(x,y):return ((x-650)*P*S,(680-y)*P*S)
def z(h):return B+h*S
def poly(p,a,b):
 pts=[xy(*q)for q in p]
 if sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1]for i in range(len(pts)))<0:pts=pts[::-1]
 return CrossSection([pts]).extrude((b-a)*S).translate((0,0,z(a)))
def box(x0,y0,x1,y1,a,b):return poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],a,b)
def add(*a):parts.append(box(*a))
def cut(*a):cuts.append(box(*a))
def cylinder(x,y,r,a,b):return Manifold.cylinder((b-a)*S,r*S,r*S,32).translate((*xy(x,y),z(a)))
parts.append(Manifold.cube((140,150,B)).translate((-70,-75,0)))
# Bounded slope: main 3F front approach at +8m, rear field at +0.2m; no exposed B1 ring.
profile=[(xy(0,400)[1],z(-.04)),(xy(0,1120)[1],z(-.04)),(xy(0,1120)[1],z(.2+11*.65))]
for i in range(11,-1,-1):
 yy=xy(0,400+i*55)[1];profile.append((yy,z(.2+i*.65)))
 if i:profile.append((yy,z(.2+(i-1)*.65)))
q=CrossSection([profile[::-1]]).extrude((948-352)*P*S)
late.append(q.transform(np.array([[0,0,1,xy(352,0)[0]],[1,0,0,0],[0,1,0,0]],float)))
# Main large hall lower mass, conservative inset from aerial eaves.
add(386,438,728,966,-.04,14.2)
# Right lower wing behind small entrance, and terrace facing membrane court.
add(738,433,877,710,-.04,7.2);add(875,710,928,953,-.04,8.4)
add(863,714,881,953,-.04,8.4)
# Rear low strip leads to stands; not an extra full-height storey around the building.
add(392,361,880,445,-.04,5.2)
add(726,440,741,714,-.04,7.2)
# Stage/podium is a low attached component, independent of the main pitched hall.
add(847,233,1030,363,-.04,3.8)
add(864,214,1017,293,3.5,4.4)
# Open field-facing stage porch with four rooted posts and finite canopy.
cut(875,210,1006,257,.4,3.55)
for xx in [878,920,962,1004]:late.append(box(xx-3.3,217,xx+3.3,224,-.03,4.4))
# Limited field stands tied to the activity center; adjoining membrane and far stands omitted.
for i in range(13):add(295,218+i*11,872,370,-.04,.4+i*.29)
# Two actual stair aisles recessed into the seating silhouette.
for xx in [458,656]:
 for i in range(26):cut(xx-7,218+i*5.5,xx+7,223.5+i*5.5,.4+(i+1)*.145,5)
# Side lower open gallery from official 1F photographs, behind roof terrace edge.
cut(863,450,882,694,.65,3.25)
for yy in np.linspace(455,685,9):late.append(box(865,yy-3.5,882,yy+3.5,-.03,3.55))
# Rear terrace guards and small rooftop services, bounded low-relief forms.
parts.append(poly([(391.5,360),(879,360),(879,432),(873,432),(873,366),(398,366),(398,432),(391.5,432)],5.1,6.0))
for x0,y0,x1,y1 in [(740,430,876,436),(870,430,877,705),(738,700,877,706),(875,710,881,953),(920,710,927,953)]:add(x0,y0,x1,y1,5.1 if y0<430 else 7.1 if y0<710 else 8.3,6.0 if y0<430 else 8.0 if y0<710 else 9.2)
add(770,550,860,650,7.0,8.1)
for x,y in [(790,575),(833,575),(800,624)]:parts.append(cylinder(x,y,1.4,7.9,9.0))
add(795,647,857,691,7.0,8.5)
# Main roof prism with full-height attic: ridge axis is front-to-back (image vertical).
def roof(x0,y0,x1,y1,eave,peak,collection=parts):
 w=(x1-x0)*P*S;xc=(x0+x1)/2
 prof=[(xy(x0,0)[0],z(eave-.65)),(xy(x1,0)[0],z(eave-.65)),(xy(x1,0)[0],z(eave)),(xy(xc+3.0,0)[0],z(peak)),(xy(xc-3.0,0)[0],z(peak)),(xy(x0,0)[0],z(eave))]
 q=CrossSection([prof]).extrude((y1-y0)*P*S)
 # profile XY represents world XZ, extrusion runs world -Y.
 collection.append(q.transform(np.array([[1,0,0,0],[0,0,-1,xy(0,y0)[1]],[0,1,0,0]],float)))
roof(379,429,735,968,14.4,21.4)
main_roof_index=len(parts)-1
# Solar panel coverage is shallow recessed relief for print stability, not roof perforations.
# Long strips on either slope inset from eaves and ridge, divided into three sourced zones.
for xa,xb in [(390,520),(592,724)]:
 for ya,yb in [(447,620),(630,787),(797,950)]:
  # a plane-following finite prism by clipping an offset full roof
  tmp=[];low=[];roof(379,429,735,968,14.4,21.4,tmp);roof(379,429,735,968,14.2,21.2,low)
  parts[main_roof_index]-=(box(xa,ya,xb,yb,14,40)-low[0])
# Fifteen ridge skylight/vent covers: capped relief, not holes in the gym.
for yy in np.linspace(470,932,15):
 add(530,yy-6,584,yy+6,20.75,21.65)
 # cap slightly higher at one edge suggests observed sawtooth repeats without thin sheets.
 add(530,yy-1,584,yy+6,21.3,21.95)
# Small entry gable, visibly separate at right of large hall.
add(727,714,865,978,-.04,11.45);roof(719,705,873,980,11.5,16.4)
entry_roof_index=len(parts)-1
for xa,xb in [(728,781),(811,864)]:
 tmp=[];low=[];roof(719,705,873,980,11.5,16.4,tmp);roof(719,705,873,980,11.3,16.2,low);parts[entry_roof_index]-=(box(xa,725,xb,963,11,40)-low[0])
# Deep pentagonal porch cut under roof; retain backing and side structural piers.
def gable_cut(x0,x1,y0,y1,bottom,eave,peak,collection):
 xc=(x0+x1)/2;prof=[(xy(x0,0)[0],z(bottom)),(xy(x1,0)[0],z(bottom)),(xy(x1,0)[0],z(eave)),(xy(xc,0)[0],z(peak)),(xy(x0,0)[0],z(eave))]
 q=CrossSection([prof]).extrude((y1-y0)*P*S);collection.append(q.transform(np.array([[1,0,0,0],[0,0,-1,xy(0,y0)[1]],[0,1,0,0]],float)))
gable_cut(740,852,957,990,8.05,11.1,15.15,cuts)
# Actual dark entrance is a shallow backed gabled glass plane behind the porch.
gable_cut(746,846,954,958,8.2,10.9,13.8,cuts)
# Glass tracery is shallow backed relief; no independent slender diagonal rods.
from shapely.geometry import LineString
lines=[((746,10.9),(796,13.8)),((796,13.8),(846,10.9)),((796,8.2),(796,13.8)),((746,10.4),(846,10.4))]
for x0,x1 in [(746,778),(814,846)]:lines.extend([((x0,8.2),(x1,10.9)),((x0,10.9),(x1,8.2))])
lines.extend([((758,10.8),(814,12.7)),((834,10.8),(778,12.7))])
for a,b in lines:
 pp=LineString([(xy(a[0],0)[0],z(a[1])),(xy(b[0],0)[0],z(b[1]))]).buffer(.13,cap_style=2,join_style=2)
 coords=list(pp.exterior.coords)[:-1]
 if pp.exterior.is_ccw is False:coords=coords[::-1]
 q=CrossSection([coords]).extrude(2.5*P*S)
 late.append(q.transform(np.array([[1,0,0,0],[0,0,-1,xy(0,953)[1]],[0,1,0,0]],float)))
late.append(box(776,950,817,967,10.55,10.9))
# Entrance solid platform and broad steps, all rooted into bounded terrain.
add(713,976,876,994,-.03,8.0)
for i in range(8):add(715,994+i*4,875,998+i*4,-.03,8.0-i*.15)
# Lower doorway behind terrace, exposed 1F only; do not duplicate it on every level.
for yy in [468,509,550,591,632,673]:cut(862,yy,883,yy+26,.7,2.9)
# Large rear gable primarily opaque: low-resolution photo supports circular central vent and few lights.
cuts.append(Manifold.cylinder(.8*S,.75*S,.75*S,32).rotate((90,0,0)).translate((*xy(557,427),z(17.5))))
for xx in [412,480,548,616,684]:cut(xx,433,xx+9,441,9.5,10.25)
# Hall north/front facade openings are sparse where trees obscure source, no invented dense grid.
for yy in [735,785,835,885]:cut(382,yy,390,yy+12,9.1,11.0)
# Clock tower: solid lower stem plus open upper cage and three X-braced tiers.
add(732,756,760,784,-.04,20.0)
for xx in [732,752]:
 for yy in [756,776]:add(xx,yy,xx+8,yy+8,19.6,33.4)
for lo in [20,23,26]:
 for yy in [756,776]:add(732,yy,760,yy+8,lo,lo+.6)
 for xx in [732,752]:add(xx,756,xx+8,784,lo,lo+.6)
 # diagonal plate braces on four faces, finite section ~1mm.
 def brace(a,b,width):
  a=np.array(a);b=np.array(b);v=b-a;L=np.linalg.norm(v);unit=v/L
  axis=np.array([0.,0.,1.]);rot=np.cross(axis,unit);angle=np.degrees(np.arccos(np.clip(unit[2],-1,1)))
  q=Manifold.cylinder(L,width/2,width/2,12)
  if np.linalg.norm(rot)>1e-8:
   # Rodrigues rotation, affine applied to the authored cylinder.
   k=rot/np.linalg.norm(rot);K=np.array([[0,-k[2],k[1]],[k[2],0,-k[0]],[-k[1],k[0],0]]);A=np.eye(3)+np.sin(np.radians(angle))*K+(1-np.cos(np.radians(angle)))*(K@K)
  else:A=np.eye(3)
  late.append(q.transform(np.column_stack((A,a))))
 for yy in [760,780]:
  a=np.array([*xy(736,yy),z(lo+.4)]);b=np.array([*xy(756,yy),z(lo+2.8)]);brace(a,b,1.3);a[2],b[2]=b[2],a[2];brace(a,b,1.3)
 for xx in [736,756]:
  a=np.array([*xy(xx,760),z(lo+.4)]);b=np.array([*xy(xx,780),z(lo+2.8)]);brace(a,b,1.3);a[2],b[2]=b[2],a[2];brace(a,b,1.3)
# Recessed structural backing core for miniature X-cage: source through-openings simplified.
add(736,760,756,780,19.9,29.1)
add(732,756,760,784,29,31.2)
# Four shallow circular clock faces; neutral dials, no purported real time.
for mode,xx,yy in [('front',746,785),('back',746,755),('left',731,770),('right',761,770)]:
 q=Manifold.cylinder(.5*S,.75*S,.75*S,32)
 if mode in ['front','back']:q=q.rotate((-90 if mode=='front' else 90,0,0))
 else:q=q.rotate((0,-90 if mode=='right' else 90,0))
 cuts.append(q.translate((*xy(xx,yy),z(30.1))))
# Finite tapered lantern cap; no unprintable needle.
q=CrossSection.square((30*P*S,30*P*S),center=True).extrude(2.5*S,scale_top=(.23,.23)).translate((*xy(746,770),z(33.1)));parts.append(q)
# V2: solid finite lantern cap. Original open triangles omitted for print robustness.
# V1 blind triangular cuts created a real 0.0132 mm lip above their z42.664 endpoint.
# Construction grid quantization before CSG, never repair final evidence.
def grid(p):
 m=p.to_mesh64();return Manifold(Mesh64(np.ascontiguousarray(np.round(m.vert_properties,4)),np.array(m.tri_verts,dtype=np.uint64,copy=True)))
solid=Manifold.batch_boolean([grid(p)for p in parts],OpType.Add)-Manifold.batch_boolean([grid(p)for p in cuts],OpType.Add)
solid+=Manifold.batch_boolean([grid(p)for p in late],OpType.Add)
assert solid.status().name=='NoError';m=solid.to_mesh64();mesh=trimesh.Trimesh(np.array(m.vert_properties[:,:3],dtype=np.float32),np.array(m.tri_verts),process=False);mesh.export(R/'model.stl');print(len(mesh.faces),mesh.extents,mesh.is_watertight,len(mesh.split(only_watertight=False)))
