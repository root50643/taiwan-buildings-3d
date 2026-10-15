"""Original CTUST Tianji bounded exterior. Coordinates metres east/north/up,
scaled to mm. Official floor datum 1F +0.30, B1 court -3.40, 10F+32.95.
79m high-bar dimension chain supports scale; roof height photo-bounded.
No source images or third-party meshes embedded. Draft pending visual review.
"""
from pathlib import Path
import numpy as np,trimesh,json,hashlib,math
from manifold3d import Manifold,CrossSection
R=Path(__file__).resolve().parent;S=150/88;BASE=2.; parts=[];cuts=[];details=[]
def box(a,b,c,d,e,f):return Manifold.cube(((b-a)*S,(d-c)*S,(f-e)*S)).translate((a*S,c*S,BASE+e*S))
def add(*a):parts.append(box(*a))
def cut(*a):cuts.append(box(*a))
def detail(*a):details.append(box(*a))
def extrude_x(poly,x1,x2):
 # yz polygon extruded in +x; (u,v,w) -> (w,u,v)
 return CrossSection([np.array(poly)*S]).extrude((x2-x1)*S).transform(np.array([[0,0,1,x1*S],[1,0,0,0],[0,1,0,BASE]]))
def rounded_platform(x1,x2,y1,y2,z,h,r=1.0):
 pts=[]
 for cx,cy,start in [(x2-r,y2-r,0),(x1+r,y2-r,90),(x1+r,y1+r,180),(x2-r,y1+r,270)]:
  for a in np.linspace(start,start+90,9):pts.append([cx+r*math.cos(math.radians(a)),cy+r*math.sin(math.radians(a))])
 return CrossSection([np.array(pts)*S]).extrude(h*S).translate((0,0,BASE+z*S))
def cylinder(x,y,z,r,h):return Manifold.cylinder(h*S,r*S,r*S,48).translate((x*S,y*S,BASE+z*S))
parts.append(Manifold.cube((78*S,150,BASE)).translate((-40*S,-75,0)))
# Grade perimeter surrounds a genuine recessed B1 courtyard over the B2 hall.
parts.append(box(-35,31,-41,41,-.01,4.0)-box(-23.8,10,-19.85,19.85,.6,4.01))
# B1 walks flank the 29.1 x 29.2 metre court; 1F opening is 39.7 x33.8.
add(-23.8,10,-19.85,-14.55,.58,.76)
add(-23.8,10,14.55,19.85,.58,.76)
add(5.4,10,-14.55,14.55,.58,.76)
# Paired lightwells beside B1 landings: shallow but real recesses, below B1 walk.
for sign in [-1,1]:
 for xx in [-18,-8]:
  a,b=sorted((sign*15.4,sign*19.4));cut(xx,xx+5,a,b,.12,.81)
# 1F indoor +.30m; 10F +32.95m. Intermediate storeys are distributed
# between supplied datum planes; no invented official individual elevations.
floors=np.array([.30,4.15,7.75,11.35,14.95,18.55,22.15,25.75,29.35,32.95])+4
add(10,29,-39.46,39.46,3.9,40.0)
# Long east facade, six upper bands of closely paired but substantial windows;
# lower two storeys share tall recess bays, top has larger canopy openings.
for i,z in enumerate(floors):
 if i<2 or i>7:continue
 for j in range(22):
  y=-28.8+j*2.72
  cut(28.20,29.1,y,y+1.95,z+.72,z+2.92)
  detail(28.19,28.38,y,y+1.95,z+1.95,z+2.08)
# Ninth-floor broad paired bays; tenth floor is recessed behind the roof shelter.
for j in range(11):
 y=-28.8+j*5.4;cut(27.9,29.1,y,y+4.25,34.05,36.35)
 detail(27.89,28.18,y+2.05,y+2.20,34.05,36.35)
 detail(26.2,30.0,y-.2,y+4.45,36.40,37.05)
cut(27.0,30.2,-29.5,29.5,36.95,40.8)
for y in [-25,-19,-13,7,13,19,25]:
 cut(27.7,29.1,y,y+4.1,5.1,11.1)
 detail(27.69,28.0,y,y+4.1,7.85,8.45)
# Real east-west double-height arch passage: two rectangular jambs and semicircle.
r=4.35;poly=[[-r,3.92],[r,3.92],[r,7.45]]+[[r*math.cos(t),7.45+r*math.sin(t)] for t in np.linspace(0,math.pi,49)]+[[-r,3.92]]
cuts.append(extrude_x(poly,9.9,29.2))
# Court-facing deep open corridor recess, continuous horizontal parapets/slabs.
for i,z in enumerate(floors):
 if i==0:
  for y in [-25,-18,-11,7,14,21]:cut(9.9,13.3,y,y+5.5,z+.7,z+3.15)
 else:cut(9.9,13.3,-29.5,29.5,z+.9,min(z+3.12,39.75))
 for y in np.arange(-28,29,5.4):
  if not (i<2 and abs(y)<5):detail(13.25,13.43,y,y+.34,z+1.0,min(z+3.0,39.8))
# Court corridor piers and backing glazing divisions attach to slab and wall.
for z in floors:
 for y in np.arange(-27.0,28,5.4):
  if z<12 and abs(y)<5:continue
  detail(9.97,13.5,y-.38,y+.38,z+.8,min(z+3.25,40.0))
# Roof shelter and two distinct deep end cores, not a uniform ten-storey slab.
add(9.7,29.5,-29.8,29.8,39.85,40.65)
for sign in [-1,1]:
 a,b=sorted((sign*29.6,sign*40.2))
 add(8.0,30.1,a,b,3.9,42.7)
 # courtyard stair/washroom block projects from end cores
 c,d=sorted((sign*26,sign*37.8));add(4.5,10.3,c,d,4,42.7)
 # Four centered broad windows above wing roof, plus four narrow head lights.
 mid=(c+d)/2
 for z in floors[6:]:
  cut(4.4,5.5,mid-1.65,mid+1.65,z+.65,z+2.95)
  detail(5.32,5.52,mid-1.65,mid+1.65,z+1.5,z+1.7)
 for yy in np.linspace(mid-3.4,mid+3.4,4):cut(4.4,5.0,yy-.3,yy+.3,40.6,41.8)
 # glazed stair-end plane: shallow backed grid, not free floating thin bars
 yface=sign*40.2
 for z in np.arange(5,41,1.75):
  ya,yb=sorted((yface-sign*.32,yface+sign*.05));cut(18,28.5,ya,yb,z,z+.14)
 for x in np.arange(18,29,1.6):
  ya,yb=sorted((yface-sign*.32,yface+sign*.05));cut(x,x+.12,ya,yb,4.5,41.4)
 # north/south tall balcony notch adjoining glazed stair
 ya,yb=sorted((yface-sign*1.3,yface+sign*.1))
 for z in floors:cut(11.0,17.5,ya,yb,z+.8,z+2.9)
# Six-floor wings. Their level-7 plans are open roof terraces with west round hole.
for sign in [-1,1]:
 a,b=sorted((sign*26.5,sign*39.5));add(-29.7,10.2,a,b,3.9,26.2)
 # court-side corridor behind descending room pods
 ca,cb=sorted((sign*24.0,sign*26.6));add(-29.7,10.2,ca,cb,3.9,26.2)
 for i,z in enumerate(floors[:6]):
  lo,hi=sorted((sign*23.9,sign*27.9));cut(-34,5.6,lo,hi,z+.95,z+3.0)
 # stair-stepped inner mass, 2/3/4/5 floors increasing eastward.
 for x1,x2,n in [(-29.7,-21,2),(-21,-11,3),(-11,-1,4),(-1,7,5)]:
  lo,hi=sorted((sign*19.9,sign*24.4));h=floors[n]+.15;add(x1,x2,lo,hi,3.9,h)
  for z in floors[:n]:
   va,vb=sorted((sign*19.8,sign*20.65));cut(x1+1.15,x2-.95,va,vb,z+1.05,z+2.8)
   # broad panes with shallow backed single subdivision
   mid=(x1+x2)/2;da,db=sorted((sign*20.47,sign*20.68));detail(mid-.10,mid+.10,da,db,z+1.05,z+2.8)
  # parapet at each terrace attaches to room roof
  add(x1,x2,lo,hi,h-.05,h+.6)
 # outer wing facade groups: clear paired windows, not all fine grid
 for z in floors[:6]:
  for x in np.arange(-26,7,5.7):
   va,vb=sorted((sign*39.6,sign*38.7));cut(x,x+3.9,va,vb,z+.95,z+2.9)
   da,db=sorted((sign*38.68,sign*38.88));detail(x+1.85,x+2.05,da,db,z+.95,z+2.9)
 # projecting solid roof edge, round aperture at far end preserved
 add(-33.8,10.4,*sorted((sign*24.0,sign*40.0)),25.95,26.8)
 cuts.append(cylinder(-31.0,sign*26.1,25.85,1.1,1.1))
 # wing end stair core and open, thick-backed zigzag flight silhouette
 add(-30.5,-27.2,*sorted((sign*27.75,sign*39.1)),3.9,26.2)
 for i,z in enumerate((floors[1:5]+floors[2:6])/2):
  ya,yb=sorted((sign*28.0,sign*39.0));parts.append(rounded_platform(-33.0,-27.0,ya,yb,z,.65,1.8 if i==0 else .75))
  # each flight is a solid wedge rooted to central stair core, with thick parapet
  y0,y1=sorted((sign*28.5,sign*38.5)); low=z+.30;high=min(z+1.85,26.1)
  # One broad rising guard-wall outline per storey; folded return flight is
  # represented behind this backed plane. No detached saw-tooth strips.
  pp=[[y0,low],[y1,high],[y1,high+1.10],[y0,low+1.10]]
  parts.append(extrude_x(pp,-33.1,-29.1)^rounded_platform(-33.1,-27.0,ya,yb,z,4.2,1.0))
 # Lower approach and diagonal ground support below the first half-landing.
 ya,yb=sorted((sign*28.5,sign*38.5))
 parts.append(extrude_x([[ya,3.85],[ya+1.25,3.85],[yb,9.3],[yb,10.3]],-32.8,-30.2))
 for k in range(7):
  yy=ya+k*1.3;add(-32.7,-29.65,yy-.02,yy+1.32,3.85,4.2+(k+1)*.60)
# Western two-level colonnade: B1 arcade, 1F walkway and roof viewing platform.
add(-34,-23.8,-20,20,4.05,4.75);add(-34.0,-29,-20,20,8.0,8.7)
for y in np.linspace(-19,19,8):add(-33,-31.7,y-.55,y+.55,.55,8.05)
add(-34,-33.3,-20,20,8.65,9.35);add(-29.7,-29,-20,20,8.65,9.35)
# B1 western arcade opens toward court while the exterior grade wall remains.
for y in np.linspace(-19,19,8)[:-1]:cut(-32.5,-23.7,y+.56,y+38/7-.56,.6,4.02)
# East/west court ledges and four real stairs descending to B1 floor.
for sign in [-1,1]:
 for x0 in [-23.7,5.8]:
  for k in range(4):
   a,b=sorted((sign*(14.8+k*1.1),sign*19.2));add(x0,x0+3.6,a,b,.55,.65+(k+1)*.92)
# Top high canopy shallow plane with rooted piers leaves discernible upper gap.
add(12,28,-29,29,41.4,42.05)
for y in np.arange(-27,28,6):add(12.3,13.4,y-.55,y+.55,40.5,41.5)
# Order: subtract from union, then attach shallow detail in original recess backs.
print('union',len(parts),'cut',len(cuts),flush=True)
m=Manifold.batch_boolean(parts,__import__('manifold3d').OpType.Add)
m=m-Manifold.batch_boolean(cuts,__import__('manifold3d').OpType.Add)
if details:m=Manifold.batch_boolean([m]+details,__import__('manifold3d').OpType.Add)
mesh=m.to_mesh();t=trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:,:3],faces=np.asarray(mesh.tri_verts),process=False)
t.export(R/'model.stl');print('done',len(t.faces),t.is_watertight,t.extents,flush=True)
(R/'parameters.json').write_text(json.dumps({'name':'中臺科技大學天機教學大樓','scale_mm_per_m':S,'base_mm':BASE,'floor_datum_m':list(floors-4),'official_datum_1F':.30,'official_datum_10F':32.95,'court_datum_m':-3.4,'high_bar_dimension_chain_m':78.92,'highest_roof_relative_1F_m':38.4,'height_bound_m':[37,40],'status':'visual draft, not frozen or print approved'},ensure_ascii=False,indent=2))
