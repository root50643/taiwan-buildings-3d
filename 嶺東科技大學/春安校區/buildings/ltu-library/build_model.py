"""Original LTU bounded draft. Common roof-pixel coordinates; nominal heights only."""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection,OpType
from shapely.geometry import Polygon,Point,box as rect
R=Path(__file__).parent;P=[];C=[];F=[];GL=.65;M=.1362385634;named_posts=[];named_steps=[]
origin=np.array([430.,642.]);u=np.array([456.,37.]);u/=np.linalg.norm(u);v=np.array([u[1],-u[0]])
def xy(p):q=(np.array(p)-origin)*M;return np.array([q@u,q@v])
def prism(p,z,h):
 p=np.array(p);area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1));p=p if area>0 else p[::-1]
 return CrossSection([p]).extrude(h).translate((0,0,z+GL))
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z+GL))
def poly(g,z,h):
 if g.is_empty:return
 if g.geom_type=='Polygon':P.append(prism(list(g.exterior.coords)[:-1],z,h))
 else:
  for a in g.geoms:poly(a,z,h)
def wall(a,b,z,w,h,depth=.6,offset=0):
 a=np.array(a);b=np.array(b);d=b-a;L=np.linalg.norm(d);n=np.array([-d[1],d[0]])/L;c=(a+b)/2+n*offset
 return Manifold.cube((w,depth,h)).translate((-w/2,-depth/2,0)).rotate((0,0,float(np.degrees(np.arctan2(d[1],d[0]))))).translate((c[0],c[1],z+GL))
foot=np.array([xy(p)for p in [[430,642],[886,679],[771,443],[687,422],[435,558]]]);G=Polygon(foot)
low=np.array([xy(p)for p in [[771,443],[976,339],[1095,586],[886,679]]]);L=Polygon(low)
allxy=np.vstack([foot,low]);lo=allxy.min(0)-[3,5];hi=allxy.max(0)+[3,3];P.append(box(*(lo+hi)/2,-GL,*(hi-lo),GL))
poly(G,0,16.5);poly(G.intersection(rect(5.5,-2,57.3,8.1)),16.45,10.05)
ba,bb=xy([435,558]),xy([687,422]);d=bb-ba;d/=np.linalg.norm(d);n=np.array([d[1],-d[0]]);strip=Polygon([ba,bb,bb+n*7,ba+n*7])
for xa,xb,h in [(4,12,19.7),(12,23,23.2),(23,32.3,25.1)]:poly(G.buffer(-.15,join_style=2).intersection(strip).intersection(rect(xa,-2,xb,40)),16.40,h-16.40)
core=xy([681,455]);P.append(box(*core,0,5.5,8,27.2));P.append(box(*core,27.1,6.3,8.8,.65))
for xa,xb,z in [(4,12,19.7),(12,23,23.2),(23,32.3,25.1)]:
 a=ba+d*max(0,(xa-ba[0])/d[0]);b=ba+d*min(np.linalg.norm(bb-ba),(xb-ba[0])/d[0]);P.append(wall(a,b,z-.04,np.linalg.norm(b-a)+1.0,.8,.8))
# Seven backed glass bands. Horizontal frames are not additional floors.
for z,h in [(.8,3.0),(4.35,3.0),(7.95,3.0),(11.55,3.0),(15.15,3.0),(18.75,3.0),(22.35,3.0)]:
 C.append(box(30.3,-.02,z,44.7,.40,h))
 for x in np.arange(8.3,53,2.8):F.append(box(x,.05,z-.04,.56,.46,h+.08))
# Visible high west short-end glazing, shallow backed relief.
for z,h in [(17.2,3.7),(21.5,3.7)]:
 C.append(box(5.5,3.85,z,.6,5.9,h))
 F.append(box(5.48,3.85,z-.04,.65,.56,h+.08))
# East entry: two-storey glazed portal beneath a modest canopy.
for z,h in [(.35,3.1),(4.05,2.4)]:
 C.append(box(56.0,-.02,z,4.0,.6,h))
 F.append(box(56.0,-.02,z-.04,.56,.68,h+.08))
# Narrow visible east brick-end vertical window strip.
for z in [8.1,11.7,15.3,18.9,22.5]:
 C.append(box(56.3,-.02,z,.65,.6,2.8))
wa,wb=foot[-1],foot[0];wd=(wb-wa)/np.linalg.norm(wb-wa)
for z in [2,6,10,14]:
 for f in [.18,.34,.5,.66,.82]:
  c=wa+(wb-wa)*f;C.append(wall(c-wd*.5,c+wd*.5,z,1,1))
for z in [1,4.8,8.6,12.4]:
 for f in [.08,.24,.40,.56,.72,.88]:
  c=ba+(bb-ba)*f;C.append(wall(c-d*2.3,c+d*2.3,z,4.6,2.9))
for xa,xb,z0,z1 in [(5,11,17,19.4),(13,22,17,22.4),(24,31,17,24.2)]:
 for z in np.arange(z0,z1-2.3+.001,3.4):
  a=ba+d*(xa-ba[0])/d[0];b=ba+d*(xb-ba[0])/d[0];C.append(wall(a,b,z,np.linalg.norm(b-a)-1,2.3))
# Low wing shallow hipped roof with broad flat centre.
body=L.buffer(-.75,join_style=2);poly(body,0,12.5);P.append(prism(low,12.35,.75))
# 2016 aerial resolves four hip slopes converging to a short central ridge.
# A narrow 0.7m nominal crest is a printing approximation, not a broad flat roof.
centre=low.mean(0);long=(low[2]-low[1]);ll=np.linalg.norm(long);long/=ll;short=np.array([-long[1],long[0]]);ridgehalf=max(1.,(ll-np.linalg.norm(low[1]-low[0]))/2)
top=np.array([centre+long*i*ridgehalf+short*j*.35 for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]])
bottom=np.array(L.buffer(-.12,join_style=2).exterior.coords)[:-1]
P.append(Manifold.hull_points(np.vstack([np.c_[bottom,np.full(len(bottom),12.9+GL)],np.c_[top,np.full(len(top),14.8+GL)]])))
for i,j in [(3,2),(0,3)]:
 a,b=low[i],low[j];dd=(b-a)/np.linalg.norm(b-a);nn=np.array([-dd[1],dd[0]]);mid=(a+b)/2
 if not body.contains(Point(mid+nn)):nn=-nn
 a=a+nn*.75;b=b+nn*.75
 for z in [2.5,6.4,10.3]:
  for f in np.linspace(.12,.88,7):
   c=a+(b-a)*f;C.append(wall(c-dd*1.6,c+dd*1.6,z,3.2,.85,.65))
p=xy([864,668]);F.append(box(p[0],p[1]-1.4,3.5,5.6,3.2,.65))
for x in [p[0]-2.3,p[0]+2.3]:
 P.append(box(x,p[1]-2.6,0,.8,.8,3.8));named_posts.append(dict(family="entry",center=[x,p[1]-2.6],width=.8,depth=.8,top=3.8))
for k in range(4):P.append(box(p[0],p[1]-2-k*.55,0,5.7,1.3,.2*(4-k)))
p=ba+(bb-ba)*.69;F.append(wall(p-d*2.6,p+d*2.6,3.8,5.2,.65,3,-1))
for k in range(5):P.append(wall(p-d*3.2,p+d*3.2,0,6.4,.15*(5-k),1.4,-1.2-k*.48))
# Exposed low-wing folded stairs, reinforced draft flights and outer frame.
a,b=low[3],low[2];dd=(b-a)/np.linalg.norm(b-a);out=np.array([dd[1],-dd[0]]);c=a+(b-a)*.82+out*2.5
for side in [-1,1]:
 for k in range(14):
  q=c+dd*((k/13-.5)*6*side)+out*side*.8;z=(k+1)/14*5.8+(0 if side==1 else 5.8);P.append(wall(q-dd*.4,q+dd*.4,max(0,z-.8),.8,1,1.8));named_steps.append(dict(flight=side,index=k,center=[*q,max(0,z-.8)+.5],run_direction=dd.tolist(),cross_direction=out.tolist()))
for q in [c-dd*3,c+dd*3]:
 P.append(box(*q,0,.8,3.8,11.8));named_posts.append(dict(family="stairs",center=q.tolist(),width=.8,depth=3.8,top=11.8))
P.append(wall(c-dd*3.5,c+dd*3.5,11.4,7,.7,3.8))
solid=Manifold.batch_boolean(P,OpType.Add)
# Preserve the visible solid brick vertical core and a backed jamb at its joins.
# Window cutters must not shave a detached triangular sliver from that core.
keep_core=box(*core,-.1,6.5,9.0,28.5)
for c in C:solid=solid-(c-keep_core)
for f in F:solid=solid+f
solid=solid.rotate((0,0,float(-np.degrees(np.arctan2(u[1],u[0])))));b=solid.bounding_box();solid=solid.translate((-(b[0]+b[3])/2,-(b[1]+b[4])/2,0));b=solid.bounding_box();scale=150/max(b[3]-b[0],b[4]-b[1],b[5]-b[2]);solid=solid.scale((scale,)*3);a=solid.to_mesh64();m=trimesh.Trimesh(np.asarray(a.vert_properties,dtype=np.float32)[:,:3],np.asarray(a.tri_verts),process=False);m.export(R/'model.stl');print([(s.volume(),s.bounding_box())for s in solid.decompose()]);print('scale',scale,'extent',m.extents,'shells',len(solid.decompose()))

import json
rot=np.array([[u[0],u[1]],[-u[1],u[0]]]);world_center=(lo+hi)/2@rot.T
(R/'source-parameters.json').write_text(json.dumps(dict(units='nominal prototype metres, not measured',scale_mm_per_m=scale,ground_m=GL,rotation_xy=rot.tolist(),rotated_center_m=world_center.tolist(),posts=named_posts,steps=named_steps,outline_nominal_m=dict(high=foot.tolist(),low=low.tolist()),source_roof_pixels=dict(high=[[430,642],[886,679],[771,443],[687,422],[435,558]],low=[[771,443],[976,339],[1095,586],[886,679]],source_image_width_height=[1280,1280],image_year=2024,metres_per_pixel=M,precision_note="Initial outline +/-5 to 10 pixels; roof parallax is not ground measurement"),limits='Roof projection candidates and photographic ratios; no surveyed floor plan'),indent=2))
