"""v9p待核候選；原創來源比例近似，單位毫米。未通過QA，非測繪。"""
from pathlib import Path
import numpy as np, trimesh
from manifold3d import Manifold, CrossSection, Mesh64
from shapely.geometry import Polygon, box as sbox
OUT=Path(__file__).resolve().parent
parts=[]; grooves=[]
# Coordinates refer to 1888x1334 displayed PLAN, not original2048x1448.
# Plan x points north, plan y east; 04/06 source roof candidate, not surveyed.
S=.125

def xy(p):return ((p[0]-950)*S,(650-p[1])*S)
def cube(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def prism(poly,bot,top):
 p=Polygon(poly)
 if not p.exterior.is_ccw:poly=list(reversed(poly))
 n=len(poly); vs=[(*xy(q),bot(q)) for q in poly]+[(*xy(q),top(q)) for q in poly]
 # y is reflected, so original CCW becomes clockwise.
 fs=[]
 # Ear clipping preserves concave footprint boundaries; never triangulate by a blind fan.
 ids=list(range(n)); triangles=[]
 while len(ids)>3:
  found=False
  for k in range(len(ids)):
   a,b,c=ids[k-1],ids[k],ids[(k+1)%len(ids)]
   pa,pb,pc=np.array(poly[a]),np.array(poly[b]),np.array(poly[c])
   u=pb-pa;v=pc-pb
   if u[0]*v[1]-u[1]*v[0]<=1e-9:continue
   tri=Polygon([poly[a],poly[b],poly[c]])
   if any(tri.buffer(-1e-8).contains(__import__('shapely').geometry.Point(poly[j])) for j in ids if j not in (a,b,c)):continue
   triangles.append((a,b,c));ids.pop(k);found=True;break
  assert found, 'Non-simple or degenerate source polygon'
 triangles.append(tuple(ids))
 for a,b,c in triangles:fs.extend([[a,b,c],[n+a,n+c,n+b]])
 for i in range(n):j=(i+1)%n;fs.extend([[i,n+i,n+j],[i,n+j,j]])
 m=Manifold(Mesh64(np.array(vs,float),np.array(fs,np.uint64)))
 assert str(m.status()).endswith('NoError'),str(m.status())
 return m
parts.append(cube(0,0,0,140,150,2.4))
# Lower court is real open space; perimeter terrain is represented by low east/west lips.
parts.append(cube(0,-72,2.3,140,6,3.6))
parts.append(cube(0,72,2.3,140,6,2.9))
# Western grade meets the two descending roof tips; the sunken court remains lower.
for poly in [[(705,70),(825,70),(900,230),(770,285)],[(1200,70),(1400,70),(1400,230),(1170,270)]]:
 parts.append(prism(poly,lambda q:2.3,lambda q:5.2))
MAIN_Z=lambda q:5.8+(q[1]-145)/995*15.0
cap_plane=np.linalg.solve(np.array([[945,875,1],[1270,895,1],[1350,1140,1]],float),np.array([MAIN_Z((945,875)),20.8,20.8]))
CAP_Z=lambda q:float(np.dot(cap_plane,[q[0],q[1],1]))
# Roof panels in architect-plan coordinates, checked against completed aerials.
ROOFS=[
 ('south_east',[(500,1140),(705,1140),(810,450),(730,410),(645,450)],MAIN_Z),
 ('south_west',[(490,145),(705,145),(670,470),(545,470)],lambda q: MAIN_Z((0,450))+(450-q[1])/305*5.9),
 ('central',[(737,156),(930,416),(1080,805),(1170,935),(970,1140),(880,790),(777,433)],lambda q: 5.8+(q[1]-145)/995*15.0),
 ('east_fold',[(1010,1140),(1090,805),(1315,960),(1350,1140)],MAIN_Z),
 ('north_west',[(1233,126),(1342,123),(1127,752),(1036,500)],MAIN_Z),
]
for name,poly,zfun in ROOFS:
 # Printable 1.6mm folded roof with inset glazed mass; 1.25mm mullions are relief.
 p=Polygon(poly).buffer(.8,join_style=2); poly=list(p.exterior.coords)[:-1]; inner=p.buffer(-18,join_style=2)
 
 if name.startswith('east_fold'): inner=Polygon([(1010,1140),(1090,805),(1315,960),(1350,1140)]).buffer(-18,join_style=2)
 if name=='north_west': inner=Polygon([(1233,126),(1342,123),(1167,635),(1036,500)]).buffer(-4,join_style=2)
 pts=list(inner.exterior.coords)[:-1]
 parts.append(prism(pts,lambda q:2.3,lambda q:max(2.35,zfun(q)-1.35)))
 parts.append(prism(poly,lambda q:zfun(q)-1.6,zfun))
 if name=='south_west':
  # Printable 1.2mm high-eave landing prevents a 0.27mm final-slice sliver.
  cap=p.intersection(sbox(0,0,2000,154))
  parts.append(prism(list(cap.exterior.coords)[:-1],lambda q:zfun(q)-.3,lambda q:zfun((0,144.2))))
 # Back the low eave into the slope so a hairline unsupported first slice cannot appear.
 lowregion = sbox(0,0,2000,400 if name=='central' else 280) if name in ('central','north_west') else sbox(0,410,2000,510) if name in ('south_east','south_west') else sbox(0,0,1,1)
 low=p.intersection(lowregion)
 if low.geom_type=='Polygon' and low.area>2:parts.append(prism(list(low.exterior.coords)[:-1],lambda q:2.3,lambda q:max(2.35,zfun(q)-.8)))
 # Shallow roof strip relief: 1.1mm wide; integrated with roof, no freestanding foil.
 for yy in np.arange(min(q[1] for q in poly)+18,max(q[1] for q in poly)-12,37):
  strip=p.intersection(sbox(0,yy,2000,yy+9.6))
  if strip.geom_type=='Polygon' and strip.area>80:
   ps=list(strip.exterior.coords)[:-1]
   grooves.append(prism(ps,lambda q:zfun(q)-.35,lambda q:zfun(q)+.1))
 # Two-storey glazing division: integrated horizontal facade band, clipped below roof.
 bandpoly=inner.buffer(4,join_style=2)
 if bandpoly.geom_type=='Polygon':
  band=prism(list(bandpoly.exterior.coords)[:-1],lambda q:10.1,lambda q:11.0)
  clip=prism(list(bandpoly.exterior.coords)[:-1],lambda q:2.3,lambda q:max(2.35,zfun(q)-1.4))
  parts.append(band ^ clip)
 # Facade vertical fins on polygon edges. Inset mass provides continuous backing.
 for a,b in zip(pts,pts[1:]+pts[:1]):
  a=np.array(a);b=np.array(b);le=np.linalg.norm(b-a)
  for t in np.linspace(.12,.88,max(2,int(le/30))):
   q=a+(b-a)*t;x,y=xy(q);h=zfun(q)-3.15
   if h>1.2:parts.append(cube(x,y,2.3,1.3,1.3,h))
# Local 1.6mm rounded plan tip shares the original roof plane and 1.6mm slab.
rounded_tip=[(950+(2.65+.8*np.cos(a))/.125,650-(-60.55+.8*np.sin(a))/.125) for a in np.linspace(0,2*np.pi,48,endpoint=False)]
tip=prism(rounded_tip,lambda q:MAIN_Z(q)-1.6,MAIN_Z)
h=15/995/.125;a=5.8+(650-145)*15/995
# Preserve top plane; shear the underside along its normal, eliminating edge lips.
parts.append(tip.transform([[1,0,0,0],[0,1+h*h,h,-h*a],[0,0,1,0]]))
# Source-visible first O column: rooted to backing and roof, not a detached fin.
qx,qy=xy((1167,635));parts.append(cube(qx,qy,2.3,1.3,1.3,MAIN_Z((1167,635))-.8-2.3))
# Bent exterior shade canopy follows the main roof edge; kept solid for the miniature.
for poly,zf in [([(737,156),(795,180),(980,405),(1036,500),(1127,752),(1135,785),(1080,815),(930,416)],MAIN_Z), ([(1090,805),(1127,752),(1318,870),(1312,880)],lambda q:MAIN_Z(q) if q[0]<1200 else 7.9)]:
 parts.append(prism(poly,lambda q:zf(q)-1.6,zf))
# Source-visible dark/glazed backing is only below the white ribbon edge,
# never across the O opening from white ribbon to D first column.
aa=np.array((1127.,752.));bb=np.array((1315.,875.));u=(bb-aa)/np.linalg.norm(bb-aa);nn=np.array([-u[1],u[0]])*10.4
wall=[tuple(aa),tuple(bb),tuple(bb+nn),tuple(aa+nn)]
def ribbon_wall_top(q):
 t=np.clip(np.dot(np.array(q)-aa,bb-aa)/np.dot(bb-aa,bb-aa),0,1)
 return MAIN_Z((1127,752))*(1-t)+7.9*t-.5
# 04 source: high two-thirds glazed with a shallow setback, low third opaque.
# The 1.3mm backing remains printable; framing is connected relief, not free wire.
nunit=nn/np.linalg.norm(nn)
def ribbon_rect(t0,t1,d0,d1):
 a0=aa+(bb-aa)*t0;a1=aa+(bb-aa)*t1
 return [tuple(a0+nunit*d0),tuple(a1+nunit*d0),tuple(a1+nunit*d1),tuple(a0+nunit*d1)]
parts.append(prism(ribbon_rect(0,.67,4,14.4),lambda q:2.3,ribbon_wall_top))
# Hidden rear footing strengthens the ribbon/upper-stair grade junction.
parts.append(prism(ribbon_rect(.45,1,4,26),lambda q:2.3,lambda q:7.9))
parts.append(prism(ribbon_rect(.67,1,0,10.4),lambda q:2.3,ribbon_wall_top))
half=4.4/np.linalg.norm(bb-aa)
for t in np.linspace(.035,.65,8):
 parts.append(prism(ribbon_rect(t-half,t+half,1.6,5.0),lambda q:2.3,ribbon_wall_top))
parts.append(prism(ribbon_rect(0,.67,1.6,5.0),lambda q:6.7,lambda q:7.5))
# Triangular landscaped berm is outside the open sunken plaza and exterior passage.
parts.append(prism([(710,1050),(900,1050),(755,510)],lambda q:2.3,lambda q:2.6+(q[1]-510)/540*2.8))
# East street is GL101, 5m above GL96 court. Approximate scale 1.1mm/m.
# Grade meets lecture-hall outer glass; slopes back toward the court at the sides.
# It is not a new building and never fills the central open throat.
for poly in [[(935,1140),(1400,1140),(1400,1250),(935,1250)],
             [(950,970),(1010,1140),(935,1140),(900,995)],
             [(1315,950),(1350,1140),(1400,1140),(1400,980)]]:
 parts.append(prism(poly,lambda q:2.3,lambda q:2.4+5.5*max(0,min(1,(q[1]-950)/190))))
# Existing upper street extends beneath the lecture-hall inset glazing foot.
parts.append(prism([(1025,1105),(1335,1105),(1335,1150),(1025,1150)],lambda q:2.3,lambda q:7.9))
# Long sunken-plaza stair bank and planted retaining berm from the plan's north edge.
# These are site relief, not additional buildings. The court stays at base-top elevation.
A=np.array((1245.,825.));B=np.array((1368.,590.));D=np.array((70.,20.))
for i in range(7):
 t0=max(0,i/7-0.002);t1=min(1,(i+1)/7+0.002) # explicit tiny tread overlap avoids coplanar-only union
 poly=[tuple(A+D*t0),tuple(B+D*t0),tuple(B+D*t1),tuple(A+D*t1)]
 parts.append(prism(poly,lambda q:2.3,lambda q:2.4+5.5*(i+1)/7))
parts.append(prism([(1390,150),(1480,450),(1480,750),(1420,860),(1315,845),(1438,610)],lambda q:2.3,lambda q:4.4+(q[1]-150)/710*2.0))
# Upper landing joins the known GL101 level; B1 gray court stays unchanged.
parts.append(prism([(1305,840),(1435,605),(1455,625),(1340,895),(1305,890)],lambda q:2.3,lambda q:7.9))
solid=Manifold.batch_boolean(parts, __import__('manifold3d').OpType.Add)
print([(q.volume(),q.bounding_box()) for q in solid.decompose()]); assert len(solid.decompose())==1
# Roof-strip cuts temporarily omitted during primary mass review.
# for g in grooves:solid=solid-g
m=solid.to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=False)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight,mesh.volume)

