"""2012多功能學生健康活動中心：原創來源比例外觀近似，不是實測BIM。
Source roof traces use original 1792px north-up NLSC mosaic. Dimensions are
image-derived roof edges, not measured wall bases. Grade and height are bounded.
"""
from pathlib import Path
import math,json
import numpy as np,trimesh
from shapely.geometry import Polygon,LineString
from shapely.ops import triangulate
from shapely import constrained_delaunay_triangles
from manifold3d import Manifold,CrossSection,Mesh,OpType
OUT=Path(__file__).resolve().parent
K=.1378645278805804;S=150/132;BASE=2.4;GRADE=3.2
parts=[];cuts=[];after=[];terrain_cuts=[]
TRACE={
'main_outer':[[730,775],[1000,764],[1195,750],[1230,890],[1230,1010],[1205,1110],[870,1155],[705,1124],[690,837],[730,825]],
'west_slope':[[690,837],[773,831],[808,1042],[780,1085],[705,1124]],
'south_slope':[[705,1124],[780,1085],[1070,1068],[1205,1110],[870,1155]],
'east_slope':[[1000,810],[1195,750],[1230,890],[1230,1010],[1205,1110],[1070,1068],[960,905]],
'north_small_slope':[[795,788],[940,820],[860,850],[780,820]],
'canopy':[[755,675],[1145,710],[1100,754],[780,768]],
'annex_back':[[645,484],[812,348],[848,397],[679,520],[665,578],[642,557]],
'annex_west':[[690,510],[774,467],[822,506],[730,553]],
'annex_east':[[847,310],[908,299],[926,431],[836,488],[793,453],[872,402],[874,350],[848,350]],
'bridge_axis':[[738,541],[766,775]],
'plaza':[[710,568],[935,479],[1080,669],[760,777]],
'sunken_court':[[850,668],[960,684],[1000,657],[944,596],[876,615]]}
def xy(p):return np.array([(p[0]-930)*K,(790-p[1])*K])
def path(name):return [xy(p) for p in TRACE[name]]
def prism(poly,z1,z2):
 poly=np.asarray(poly);poly=poly if Polygon(poly).exterior.is_ccw else poly[::-1]
 assert Polygon(poly).is_valid
 return CrossSection([poly*S]).extrude((z2-z1)*S).translate((0,0,BASE+z1*S))
def box(x1,x2,y1,y2,z1,z2):return Manifold.cube(((x2-x1)*S,(y2-y1)*S,(z2-z1)*S)).translate((x1*S,y1*S,BASE+z1*S))
def cyl(x,y,z,h,r,n=48):return Manifold.cylinder(h*S,r*S,r*S,circular_segments=n).translate((x*S,y*S,BASE+z*S))
def beam(a,b,r):
 a=np.array(a,float);b=np.array(b,float);v=b-a;L=np.linalg.norm(v);az=math.degrees(math.atan2(v[1],v[0]));tilt=math.degrees(math.acos(v[2]/L))
 return Manifold.cylinder(L*S,r*S,r*S,circular_segments=32).rotate((0,tilt,az)).translate((a[0]*S,a[1]*S,BASE+a[2]*S))
def edged(a,b,start,end,depth,z1,z2,inset=0):
 a=np.array(a);b=np.array(b);u=(b-a)/np.linalg.norm(b-a);n=np.array([u[1],-u[0]]);p=a+(b-a)*start+n*inset;q=a+(b-a)*end+n*inset
 return prism([p,q,q+n*depth,p+n*depth],z1,z2)
def balcony_rail(a,b,t0,t1,z1,z2):
 # Original printable filleted rail: capsule ends remove brittle square corners.
 a=np.asarray(a);b=np.asarray(b);u=(b-a)/np.linalg.norm(b-a);n=np.array([u[1],-u[0]])
 p=a+(b-a)*t0+n*1.15+u*.3;q=a+(b-a)*t1+n*1.15-u*.3
 return prism(list(LineString([p,q]).buffer(.7,quad_segs=12).exterior.coords)[:-1],z1,z2)
def roof(poly,heights,bottom,cap=None):
 poly=[list(p) for p in poly];P=Polygon(poly);assert P.is_valid
 if not P.exterior.is_ccw:poly.reverse();heights=list(heights)[::-1];P=Polygon(poly)
 v=[[p[0]*S,p[1]*S,BASE+h*S] for p,h in zip(poly,heights)]+[[p[0]*S,p[1]*S,BASE+bottom*S] for p in poly];N=len(poly);f=[]
 for t in triangulate(P):
  if not P.covers(t):continue
  ids=[poly.index(list(p)) for p in list(t.exterior.coords)[:3]]
  f.append(ids);f.append([i+N for i in ids[::-1]])
 for i in range(N):j=(i+1)%N;f.extend([[i,i+N,j+N],[i,j+N,j]])
 m=Manifold(Mesh(np.array(v,np.float32),np.array(f,np.uint32)));assert m.status()==__import__('manifold3d').Error.NoError
 if cap is not None:m=m^box(-100,100,-100,100,-1,cap)
 return m
# Base spans the entire group, not only the main hall.
parts.append(Manifold.cube((96*S,150,BASE)).translate((-48*S,-60*S,0)))
# Grade platform, locally cut to expose the basement court; no invented closed atrium.
platform=[[-45,-55],[44,-55],[44,18],[8,70],[-41,70]]
parts.append(prism(platform,0,GRADE))
parts.append(prism(list(Polygon(path('main_outer')).buffer(-.08,join_style=2).exterior.coords)[:-1],-.03,GRADE+17.0))
# Three unequal roof pieces and small northern infill; central plane stays solid.
parts.append(roof(path('west_slope'),[19.6,25.2,25.0,25.0,19.6],19.35,24.0))
parts.append(roof(path('south_slope'),[19.6,25.0,25.0,19.6,19.6],19.35,24.0))
parts.append(roof(path('east_slope'),[25.2,19.6,19.6,19.6,19.6,25.0,25.2],19.35,24.0))
parts.append(roof(path('north_small_slope'),[21.8,21.8,20.2,20.2],19.5,21.3))
# Independent broad non-rectangular north canopy with real void below.
canopy_outline=path('canopy');canopy_outline[2]+=np.array([0,1.4]);canopy_outline[3]+=np.array([0,1.4])
parts.append(prism(canopy_outline,GRADE+16.8,GRADE+18.1))
# North main facade is a near east-west line; right (west) glazing differs from east.
fa=xy([730,775]);fb=xy([1195,750]);u=(fb-fa)/np.linalg.norm(fb-fa);north=np.array([-u[1],u[0]])
# Entire glass field is shallow-backed; solid north facade never becomes floating sheets.
for t0,t1 in [(0.13,.47),(.49,.87)]:
 for z0,z1 in [(GRADE+.45,GRADE+5.1),(GRADE+6.0,GRADE+14.87),(GRADE+11.5,GRADE+16.2)]:
  cuts.append(edged(fb,fa,1-t1,1-t0,1.15,z0,z1,inset=-.65))
# Larger western continuous glazed wall: recessed bands joined visually by major grid.
for t in np.linspace(.16,.86,15):
 for z0,z1 in [(GRADE+.45,GRADE+5.1),(GRADE+6,GRADE+14.87),(GRADE+11.5,GRADE+16.2)]:
  cuts.append(edged(fb,fa,1-t-.013,1-t+.013,.95,z0,z1,inset=-.55))
# Glazing mullions are rooted relief, not freestanding thin window sheets.
for t in np.linspace(.15,.85,13):after.append(edged(fb,fa,1-t-.006,1-t+.006,1.05,GRADE+.3,GRADE+16.4,inset=-.9))
# East half horizontal belts and projecting 3F terrace.
for z,dep in [(GRADE+5.45,.9),(GRADE+11.0,2.5)]:
 parts.append(edged(fb,fa,.12,.54,dep+1.65,z-.55,z+.45,inset=-1.8))
 if dep>1:
  parts.append(edged(fb,fa,.12,.54,1.0,z+.25,z+1.45,inset=dep-.9))
# Blank end cores and west stair/service volume, anchored in main hall.
for t0,t1,h in [(0,.115,21.0),(.885,1,18.0)]:parts.append(edged(fb,fa,1-t1,1-t0,4.0,GRADE-.1,GRADE+h,inset=-3.3))
# Major canopy columns, purposely thickened to ~2.05mm miniature diameter.
column_xy=[]
for t in [.10,.25,.40,.55,.70,.85]:
 p=fa+(fb-fa)*t+north*(8.2-4*t);column_xy.append(p.tolist());after.append(cyl(*p,-.05,GRADE+18.0,.90))
# East long facade: two continuous backed glass bands visible in school 2023 photo.
# Original wall bays follow roof footprint; frames are relief, not open holes.
outer=path('main_outer')
for idx in [2,3,4]:
 a=outer[idx+1];b=outer[idx];L=np.linalg.norm(b-a)
 for z0,z1 in [(GRADE+6.1,GRADE+10.0),(GRADE+12.2,GRADE+15.9)]:
  cuts.append(edged(a,b,.035,.965,1.15,z0,z1,inset=-1.0))
  for t in np.linspace(.08,.92,max(3,int(L/2.5))):
   half=.36/L
   after.append(edged(a,b,t-half,t+half,.8,z0-.1,z1+.1,inset=-1.05))
 parts.append(edged(a,b,.02,.98,.65,GRADE+4.7,GRADE+5.6,inset=-.3))
# South / west are footprint-supported but detailed rear fenestration unverified.
for idx in [5,6,7]:
 a=outer[idx];b=outer[(idx+1)%len(outer)]
 for t in [.2,.5,.8]:cuts.append(edged(a,b,t-.055,t+.055,.4,GRADE+2.2,GRADE+4.8,inset=-.3))
# Northern folded annex: three overlapping nonrectangular prisms, individual roofs.
# A constructively buffered 0.12m margin ensures overlap, not a mesh repair.
annexes=[]
for name in ['annex_back','annex_west','annex_east']:
 poly=path(name);P=Polygon(poly);assert P.is_valid
 poly=list(P.buffer(.12,join_style=2).exterior.coords)[:-1];body_poly=poly
 parts.append(prism(body_poly,-.05,16.6));annexes.append(body_poly)
 # Original offset-contour hipped roof keeps both concave returns and the equipment valley.
 # No centroid contraction across an L-shaped courtyard; all triangles cover the actual polygon.
 P=Polygon(poly).buffer(.04,join_style=2)
 ridge_axes={'annex_back':[[657,552],[660,494],[821,375]],'annex_west':[[714,528],[787,490]],'annex_east':[[879,323],[899,418],[817,460]]}
 cap=LineString([xy(v)for v in ridge_axes[name]]).buffer(.60,quad_segs=12)
 assert P.contains(cap),('ridge cap outside source roof',name)
 rings=[(P,17.0),(cap,19.4)]
 assert all(not shape.is_empty and shape.is_valid for shape,z in rings)
 verts=[];faces=[];lookup={}
 def vi(x,y,z):
  key=(float(x),float(y),float(z))
  if key not in lookup:lookup[key]=len(verts);verts.append([x*S,y*S,BASE+z*S])
  return lookup[key]
 def patch(shape,z_for_xy,reverse=False):
  for t in constrained_delaunay_triangles(shape).geoms:
   cc=list(t.exterior.coords)[:-1]
   if not t.exterior.is_ccw:cc=cc[::-1]
   ids=[vi(x,y,z_for_xy(x,y)) for x,y in cc];faces.append(ids[::-1]if reverse else ids)
 def coords(shape):
  ps=[shape]if shape.geom_type=='Polygon'else list(shape.geoms)
  return {tuple(c) for pp in ps for ring in [pp.exterior,*pp.interiors]for c in list(ring.coords)[:-1]}
 for (low,zlo),(high,zhi) in zip(rings,rings[1:]):
  D=low.difference(high);hc=coords(high)
  patch(D,lambda x,y: zhi if (x,y)in hc else zlo)
 patch(rings[-1][0],lambda x,y:rings[-1][1]);patch(P,lambda x,y:16.4,True)
 cc=list(P.exterior.coords)[:-1]
 if not P.exterior.is_ccw:cc=cc[::-1]
 for aa,bb in zip(cc,cc[1:]+cc[:1]):
  ids=[vi(*aa,17),vi(*aa,16.4),vi(*bb,16.4),vi(*bb,17)];faces.extend([[ids[0],ids[1],ids[2]],[ids[0],ids[2],ids[3]]])
 roof_mesh=Manifold(Mesh(np.asarray(verts,np.float32),np.asarray(faces,np.uint32)));assert roof_mesh.status()==__import__('manifold3d').Error.NoError;parts.append(roof_mesh)
# The A/C equipment valley stays open; no invented connector blocks the C glazing.
# Annex A source-facing long facade: four staggered balconies and three window bands.
a=xy([812,348]);b=xy([645,484])
for z in [GRADE+.65,GRADE+5.2,GRADE+9.75]:
 for t in np.linspace(.08,.92,10):cuts.append(edged(a,b,t-.027,t+.027,2.5,z,z+2.8,inset=-.55))
for z,segments in [(GRADE+4.8,[(.08,.54),(.84,.99)]),(GRADE+9.4,[(.06,.20),(.35,.80)])]:
 for t0,t1 in segments:
  after.append(edged(a,b,t0,t1,3.5,z-.55,z+.45,inset=-1.5));after.append(balcony_rail(a,b,t0,t1,z+.18,z+1.35))
# Rear minor openings remain conservative plain bands.
for aa,bb in [([730,553],[822,506]),([836,488],[926,431])]:
 a=xy(aa);b=xy(bb)
 for z in [GRADE+.7,GRADE+5.2,GRADE+9.7]:cuts.append(edged(a,b,.15,.85,.9,z,z+2.2,inset=-.5))
# C3-C2 flank has source-visible small recessed balcony/window bays.
a=xy([926,431]);b=xy([908,299])
for z in [GRADE+.8,GRADE+5.3,GRADE+9.8]:
 for t in [.22,.5,.78]:
  cuts.append(edged(a,b,t-.08,t+.08,1.6,z,z+2.6,inset=-1.15))
  after.append(edged(a,b,t-.10,t+.10,1.25,z-.5,z+.28,inset=-.8))
# C full north return: source-visible G lies on the northern SHORT eave, not the SE slope patch.
# 2014/2018 complete roof evidence supersedes the rejected four-corner footprint.
a=xy([908,299]);b=xy([847,310])
cuts.append(edged(a,b,.14,.59,.75,.45,16.2,inset=-.55))
for t in [.29,.44]:after.append(edged(a,b,t-.045,t+.045,1.15,.3,16.15,inset=-.9))
for z in [3.0,5.4,7.8,10.2,12.6,15.85]:after.append(edged(a,b,.14,.59,.65,z,z+.55,inset=-.9))
# Local B1 forecourt outside the glass/entry, with a short straight stair and two curved edges.
terrain_cuts.append(edged(a,b,.02,.98,6.2,.1,GRADE+.1,inset=.18))
# Its stair connection is modelled at A's observed recessed entrance below.
# Bridge at 2F floor level, not the high third-floor terrace.
ba,bb=path('bridge_axis');du=(bb-ba)/np.linalg.norm(bb-ba);bn=np.array([du[1],-du[0]]);BW=5.0
bridgepoly=[ba+bn*BW/2,bb+bn*BW/2,bb-bn*BW/2,ba-bn*BW/2]
parts.append(prism(bridgepoly,GRADE+5.1,GRADE+6.3))
for sign in [-1,1]:
 rail=[ba+bn*(sign*BW/2),bb+bn*(sign*BW/2),bb+bn*(sign*BW/2-.95*sign),ba+bn*(sign*BW/2-.95*sign)]
 parts.append(prism(rail,GRADE+6.1,GRADE+7.5))
# Source-observed diagonal braces tied to western canopy columns and bridge landing.
# The secondary diagonal braces are omitted at this scale; the six full rooted columns remain.
# Sunken plaza is cut in the grade slab, with curved retaining wall and descending steps.
court=path('sunken_court');cuts.append(prism(court,.15,GRADE+.1))
# Arc wall on east side of court; no invented exterior full circular building.
c=np.array([4.0,16.5]);ang=np.linspace(-.3,1.8,35);outerarc=[c+np.array([math.cos(t),math.sin(t)])*9 for t in ang];innerarc=[c+np.array([math.cos(t),math.sin(t)])*7.8 for t in ang[::-1]]
parts.append(prism(outerarc+innerarc,.1,GRADE+1.0))
# Broad steps leading down toward the open northern plaza, each rooted to base.
for i in range(8):after.append(box(-4,0,14.3+i*1.2,15.6+i*1.2,0,GRADE*(8-i)/8))
# Main entrance plaza broad straight stair flight, beside the separate basement court.
cuts.append(box(-27,-9,9,24,2.0,GRADE+.1))
for i in range(6):after.append(box(-27,-9,9+i*2.5,11.6+i*2.5,0,GRADE-i*.2))
# Main B1 court has straight perimeter walls as well as its curved side, leaving an open floor.
for aa,bb in [(court[3],court[4]),(court[4],court[0])]:
 wall=LineString([aa,bb]).buffer(.55,quad_segs=12);after.append(prism(list(wall.exterior.coords)[:-1],0,GRADE+.8))
# Annex deep entrance: short straight stairs and paired curved retaining edges outside A's NE end.
a=xy([812,348]);b=xy([645,484]);uu=(b-a)/np.linalg.norm(b-a);nn=np.array([uu[1],-uu[0]])
terrain_cuts.append(edged(a,b,.01,.27,6.0,.1,GRADE+.1,inset=.15))
origin=a+(b-a)*.04;ww=np.linalg.norm(b-a)*.19;step_parts=[]
for i in range(8):
 h=.35+i*(GRADE-.35)/7;step_parts.append(Manifold.cube((ww*S,.85*S,(h+.05)*S)).translate((0,-(.5+i*.65+.85)*S,BASE-.05*S)))
after.append(Manifold.batch_boolean(step_parts,OpType.Add).rotate((0,0,math.degrees(math.atan2(uu[1],uu[0])))).translate((origin[0]*S,origin[1]*S,0)))
for side in [0,1]:
 local=[(-.8,.4),(-1.4,2.0),(-1.2,3.7),(-.2,5.4)] if side==0 else [(ww+.7,.4),(ww+1.3,2.0),(ww+1.5,3.7),(ww+.8,5.4)]
 line=[origin+uu*x+nn*y for x,y in local];wall=LineString(line).buffer(.55,quad_segs=12);after.append(prism(list(wall.exterior.coords)[:-1],0,GRADE+.7))
parts[1]=parts[1]-Manifold.batch_boolean(terrain_cuts,OpType.Add)
solid=(Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add))+Manifold.batch_boolean(after,OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError,solid.status()
m=solid.to_mesh();tm=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=False);assert tm.is_watertight and tm.volume>0
raw=trimesh.exchange.stl.export_stl(tm);T=np.frombuffer(raw,offset=84,dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]))['v'].astype(float);assert (np.linalg.norm(np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]),axis=1)>1e-9).all(),'Change source to remove degeneracy; never repair STL'
(OUT/'model.stl').write_bytes(raw)
params={'unit':'mm','scale_mm_per_m':S,'roof_image_m_per_pixel':K,'trace_source':'Main: watermark2024; annex: watermark2014 with2018 crosscheck. Both1792px north-up; service year is not image capture proof','trace_pixels':TRACE,'xy_origin_px':[930,790],'grade_above_sunken_level_m':GRADE,'main_eave_above_grade_m':17.0,'main_max_roof_above_grade_m':20.8,'canopy_above_grade_m':18.1,'annex_ridge_cap_width_m':1.2,'G_horizontal_recessed_frame_front_offset_m':-.25,'G_horizontal_frame_height_m':.55,'A_end_wall_setback_m':0,'A_rejected_old_setback_m':3.5,'annex_eave_above_grade_m':13.8,'annex_roof_above_grade_m':16.2,'bridge_deck_above_grade_m':6.3,'third_floor_terrace_above_grade_m':11.0,'main_column_centres_m':column_xy,'dimensions_mm':tm.extents.tolist(),'limitations':['高度是照片配景有界假設，非官方標高。','屋頂描點非牆基地籍，未校正影像位移。','北遮棚微坡未測，簡化為非矩形等高實體板；柱、橋欄、屋頂脊線作列印加厚。','中央平屋面為封閉屋面，不是天井；室內旋轉坡道不建到室外。','西南細窗不足，以航照完整屋面及外輪廓為主，次要窗簡化。']}
(OUT/'parameters.json').write_text(json.dumps(params,ensure_ascii=False,indent=2));print(params)
