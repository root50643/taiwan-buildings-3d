"""三一禮拜堂來源限定近似。原創CSG；官方2F圖像座標為平面參考。
0.124m/px bounded cross-registration, NOT the conflicting architect graphic scale.
"""
from pathlib import Path
import numpy as np,trimesh
from shapely.geometry import LineString
from manifold3d import Manifold,CrossSection,Mesh64
R=Path(__file__).resolve().parent;S=2.0;P=.124*S;BASE=1.6
parts=[];cuts=[];late=[]
def xy(x,y):return ((x-485)*P,(320-y)*P)
def z(h):return BASE+h*S
def cs(p):
 if sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))<0:p=p[::-1]
 return CrossSection([p])
def poly(p,a,b):return cs([xy(*q) for q in p]).extrude((b-a)*S).translate((0,0,z(a)))
def box(x0,y0,x1,y1,a,b):return poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],a,b)
def add(*a):parts.append(box(*a))
def cut(*a):cuts.append(box(*a))
def wall(a,b,width,lo,hi,collection=parts):
 a=np.array(a,float);b=np.array(b,float);v=b-a;n=np.array([-v[1],v[0]])/np.linalg.norm(v)*width/2
 collection.append(poly([a+n,b+n,b-n,a-n],lo,hi))
parts.append(Manifold.cube((150,100,BASE)).translate((-75,-50,0)))
# A bounded local plinth, not the shared whole-campus basement.
add(195,190,775,410,-.05,.22)
# Main high body and western atrium. Interior rib vault is not an exterior roof.
add(235,203,550,375,-.05,14.9)
parts.append(poly([(235,203),(310,203),(310,375),(235,375),(235,325),(218,245),(235,240)],-.05,15.0))
# Flat roof parapet, with lower inset deck and two west equipment/light structures.
add(235,203,550,375,14.4,15.1)
for y in [226,351]:
 late.append(box(309,y-5,317,y+5,14.5,15.5))
# West large glass face, shallow recessed backing plane with fused fine frames.
# Face runs obliquely from (218,245) to (235,325); upper stair remains opaque north.
a=np.array([218.,245.]);b=np.array([235.,325.]);v=b-a;n=np.array([-v[1],v[0]])/np.linalg.norm(v)
# Outward normal points west. The cut penetrates to a backing plane 5 px inward.
for lo,hi in [(.45,3.0),(3.45,14.3)]:
 cuts.append(poly([a+n*3,b+n*3,b-n*1.2,a-n*1.2],lo,hi))
for t in np.linspace(.05,.95,10):
 p=a+v*t;wall(p-n*.15,p-n*3,2,.4 if min(abs(t-.25),abs(t-.75))<1e-6 else 3.35,14.4,late)
for h in [3.45,7.2,10.3,13.8]:wall(a-n*1.5,b-n*1.5,2.7,h,h+.15,late)
# Recessed doorway below glass; 3 door divisions, all fused to backing.
for t in [.5]:
 p=a+v*t;wall(p-n*.15,p-n*3,2,.4,3.4,late)
# North west stair few irregular punched windows, not a repeated curtain wall.
for yy,lo,hi,w in [(216,1.0,1.7,7),(216,3.4,4.0,15),(217,5.3,6.4,6),(217,8.1,8.7,15),(216,10.1,10.8,6),(216,12.5,14.0,6)]:cut(231,yy,241,yy+w,lo,hi)
# Nave south horizontal deep corridor, lower wall distinct from upper mass.
cut(311,365,545,383,5.2,8.0)
add(290,374,568,402,4.65,5.0)
add(291,373,560,395,8.0,8.45)
for x in [315,360,405,450,495,537]:
 cut(x,364,x+9,369,5.45,6.4)
 cut(x,369,x+13,379,.65,2.65)
# North glazing band remains smaller; no mirrored southern grand stair.
cut(315,198,538,209,5.45,6.65)
for x in np.linspace(318,535,9):late.append(box(x-2,203,x+2,211,5.4,6.7))
# East lower altar projection below main roof, and terrace over canteen.
add(549,235,570,350,-.05,10.9)
wing=[(548,203),(662,203),(677,231),(770,231),(770,325),(715,347),(735,400),(548,400)]
parts.append(poly(wing,-.05,5.0))
# Terrace edge guards are thickened low rails, separated from main walls.
for aa,bb in zip(wing,wing[1:]+wing[:1]):wall(aa,bb,5,4.8,5.75)
for x,y in wing:add(x-3,y-3,x+3,y+3,4.8,5.75)
# East and south continuous glazing strips with backing and vertical divisions.
cut(763,248,776,319,.6,3.8)
for y in np.linspace(252,315,7):late.append(box(761,y-2,771,y+2,.5,3.9))
cut(579,392,710,405,.6,3.8)
for x in np.linspace(584,705,10):late.append(box(x-2,390,x+2,401,.5,3.9))
# East altar cross relief, rooted in solid end face.
late.append(box(568,289,572,293,7.7,10.4));late.append(box(568,282,572,300,9.25,9.7))
# Western tower base and distinctly staggered folded upper walls.
tower=[(217,325),(264,325),(285,375),(285,402),(215,402),(208,359)]
parts.append(poly(tower,-.05,18.2))
# Roof inset is confined to the hall; it must never cut across the tower core.
cuts.append(box(240,208,545,370,14.6,16)-poly(tower,14.5,16.1))
# Mitered planar folds keep a finite continuous wall through direction changes.
# This constructs authored wall footprints, not a repair of mesh/section evidence.
def fold(points,lo,hi):
 shape=LineString(points).buffer(2.5,cap_style=2,join_style=2)
 assert shape.is_valid and shape.geom_type=='Polygon'
 section=cs([xy(*p) for p in shape.exterior.coords[:-1]])
 for ring in shape.interiors:section-=cs([xy(*p) for p in ring.coords[:-1]])
 parts.append(section.extrude((hi-lo)*S).translate((0,0,z(lo))))
fold([(217,325),(264,325),(285,375),(285,402),(215,402),(208,359),(217,325)],18,27.0)
cut(190,359,240,420,24.6,28)
cut(240,375,300,420,24.6,28)
# West high opening and south broad opening are actual through-wall cuts.
cut(202,334,224,354,20.0,25.0)
cut(231,395,276,408,20.0,22.5)
cut(202,362,224,390,20.0,22.5)
# Upper internal crossbeam/landing, visible through tower openings.
add(217,355,283,360,22.3,22.9)
# A vertical slit on west lower face and south lower face, with backed fine divisions.
for lo,hi in [(.5,3.38),(3.8,6.58),(7,9.78),(10.2,12.98),(13.4,16.18),(16.6,17.5)]:cut(205,374,218,384,lo,hi)
cut(252,396,261,407,2,8);cut(252,396,261,407,10.5,14.2)
# Tower cross plate is built into south wall; not a floating thin metal ornament.
add(217,400,222,412,17.8,25.5);add(210,400,230,412,23.8,24.3)
# South broad stair and its finite sloping retaining side walls.
def stairx(x0,x1,y0,y1,lo,hi,n):
 L=(x1-x0)*P;profile=[(0,z(-.05)),(L,z(-.05)),(L,z(hi-.01))]
 for i in range(n-1,-1,-1):
  profile.append((L*i/n,z(lo+(hi-lo)*(i+1)/n-.01)))
  if i:profile.append((L*i/n,z(lo+(hi-lo)*i/n-.01)))
 q=cs(profile).extrude((y1-y0)*P)
 late.append(q.transform(np.array([[1,0,0,(x0-485)*P],[0,0,-1,(320-y0)*P],[0,1,0,0]],float)))
stairx(397,491,403,448,.22,5,25)
late[-1]=late[-1] ^ poly([(397,402),(535,402),(535,414),(491,414),(397,448)],-.1,6)
# Solid finite ends on retaining flanks preserve the slope silhouette.
def graded_wall(a,b,width,h0,h1):
 a=np.array(a,float);b=np.array(b,float);v=b-a;n=np.array([-v[1],v[0]])/np.linalg.norm(v)*width/2
 pp=[a+n,b+n,b-n,a-n];qq=[xy(*p) for p in pp]
 if sum(qq[i][0]*qq[(i+1)%4][1]-qq[(i+1)%4][0]*qq[i][1] for i in range(4))<0:pp=pp[::-1];qq=qq[::-1]
 vertices=[[*q,z(-.05)] for q in qq]+[[*q,z(h0+(h1-h0)*float(np.dot(p-a,v)/np.dot(v,v)))] for p,q in zip(pp,qq)]
 faces=[[0,2,1],[0,3,2],[4,5,6],[4,6,7]]
 for i in range(4):j=(i+1)%4;faces.extend([[i,j,j+4],[i,j+4,i+4]])
 parts.append(Manifold(Mesh64(np.array(vertices,dtype=np.float64),np.array(faces,dtype=np.uint64))))
graded_wall((397,448),(491,414),5,.7,5.5)
wall((491,414),(535,414),5,-.05,5.5)
join=LineString([(489,414+68/94),(491,414),(493,414)]).buffer(2.5,cap_style=2,join_style=2)
parts.append(poly(list(join.exterior.coords)[:-1],-.05,5.5))

# Continuous opaque wall follows the outer B207 edge west of the grand stair.
# Its near-horizontal top is independent of the stair slope; east access stays open.
add(310,402,505,407,-.05,5.4)
# Upright wall and cross beside the upper stair/altar end.
add(545,367,550,432,-.05,10.7)
profile=[(400,3.6),(404,3.6),(404,6.8),(413,6.8),(413,7.2),(404,7.2),(404,8.4),(400,8.4),(400,7.2),(391,7.2),(391,6.8),(400,6.8)]
q=cs([((320-y)*P,z(h)) for y,h in profile]).extrude(4*P)
late.append(q.transform(np.array([[0,0,1,(543-485)*P],[1,0,0,0],[0,1,0,0]],float)))
add(491,402,535,414,-.05,5.0)
# Northeast terrace exterior stair descends eastward; rooted backing.
stairx(677,770,217,231,5.0,.22,25)
# Southwest bridge terminates at model scope, including a finite support.
add(280,399,309,480,4.65,5.05)
for x in [280,305]:add(x,399,x+4,480,4.95,6.0)
add(280,472,309,480,-.05,5)
# Canonical construction grid for authored primitives BEFORE CSG.
def grid(p):
 m=p.to_mesh64();return Manifold(Mesh64(np.ascontiguousarray(np.round(m.vert_properties,5),dtype=np.float64),np.array(m.tri_verts,dtype=np.uint64,copy=True,order='C')))
parts=[grid(p) for p in parts];cuts=[grid(p) for p in cuts];late=[grid(p) for p in late]
solid=parts[0]
for p in parts[1:]:solid+=p
for p in cuts:solid-=p
for p in late:solid+=p
print('shells',[(a.volume(),a.bounding_box()) for a in solid.decompose()]);assert len(solid.decompose())==1
m=solid.to_mesh64();mesh=trimesh.Trimesh(np.array(m.vert_properties[:,:3],dtype=np.float32),np.array(m.tri_verts),process=True);mesh.export(R/'model.stl');print(mesh.extents,mesh.is_watertight)
