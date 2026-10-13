"""人社二館八角塔與院落：2006–2017 historical exterior approximation.
Original miniature-mm CSG. Official B1–4F plans establish unequal wings and bridges.
No neighbouring Humanities I square tower; no excavated basement/interior replica.
"""
from pathlib import Path
import math, numpy as np, trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
P={'base_mm':[150,140,2.5],'four_storey_wall_z':40.2,'three_storey_wall_z':31.0,'two_storey_gallery_z':22.0,'tower_body_z':60,'east_top_bays':22,'east_narrow_row_bays':36,'opening_min_mm':1.25}
parts=[];cuts=[];after=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def poly(pts,z,h):return CrossSection([pts]).extrude(h).translate((0,0,z))
def cyl(x,y,z,r,h,n=64):return Manifold.cylinder(h,r,r,n).translate((x,y,z))
def hip(x,y,z,w,d,rise):
 # Thick eave, truncated ridge (not a zero-thickness razor-tip).
 pts=[(x+sx*w/2,y+sy*d/2,z+zz) for sx in [-1,1] for sy in [-1,1] for zz in [0,1.2]]
 if w>=d: pts +=[(x+sx*(w-d)/2,y+sy*.65,z+rise+1.2) for sx in [-1,1] for sy in [-1,1]]
 else: pts +=[(x+sx*.65,y+sy*(d-w)/2,z+rise+1.2) for sx in [-1,1] for sy in [-1,1]]
 parts.append(Manifold.hull_points(pts))
def beam_between(a,b,z,w,h):
 x,y=(a[0]+b[0])/2,(a[1]+b[1])/2;dx,dy=b[0]-a[0],b[1]-a[1]
 return box(0,0,z,math.hypot(dx,dy),w,h).rotate((0,0,math.degrees(math.atan2(dy,dx)))).translate((x,y,0))
add(0,0,0,*P['base_mm'])
# 1F plan-derived silhouette: D northern arm starts near the middle; A east, B south.
add(31,48,2.4,73,18,37.8)
add(59,-1,2.4,17,104,37.8)
add(-7,-52,2.4,115,17,28.6)
# B east portion rises one floor, the west/central B roof remains lower at z31.
add(37,-52,30.8,39,17,9.4)
# C auditorium has broad two-storey volume on western side, with a lower lobby.
add(-49,-6,2.4,30,49,23.6)
add(-49,-38,2.4,30,19,17.6)
hip(-49,-6,25.6,32.8,51.8,6.4)
hip(-32,-52,30.6,66,19.5,4.0)
hip(31,48,39.8,75.5,20.5,4.6)
hip(59,-1,39.8,19.5,106,4.6)
hip(37,-52,39.8,40.5,19.5,4.0)
# Northeast projecting staircase/glass bay bridges 2F/3F, with solid structural back.
add(68.3,39,11.0,3.7,16,20.0)
cuts.append(box(70.15,39,12.6,1.4,13.2,16.6))
for z in [17.2,22.4,27.6]:after.append(box(69.9,39,z,1.6,14.5,1.1))
for y in [34.5,39,43.5]:after.append(box(69.9,y,12.4,1.6,1.1,17.4))
# D north end is a three-storey octagonal room; 4F plan shows its roof, NOT the tower.
parts.append(cyl(-10,49,2.4,8.7,28.6,8))
parts.append(Manifold.cylinder(4.0,9.5,1.5,8).translate((-10,49,30.7)))
# Actual tall octagonal tower is the southeast A/B staircase core, proved by all elevations.
tx,ty=61,-52
parts.append(cyl(tx,ty,2.4,10.4,57.6,8))
parts.append(cyl(tx,ty,59.5,11.0,1.8,8))
# Open lantern is genuinely perforated, all eight posts connect lower ring and roof.
for ang in np.arange(0,360,45):
 a=math.radians(ang);parts.append(box(tx+8.7*math.cos(a),ty+8.7*math.sin(a),60.7,4.0,4.0,5.5))
parts.append(cyl(tx,ty,65.7,11.5,1.4,8))
parts.append(Manifold.cylinder(4.5,11.5,1.5,8).translate((tx,ty,67.0)))
# Four cardinal slit faces form the recognizable narrow upper / wide lower glazing.
for ang in [0,90,180,270]:
 buried=ang in [0,90]
 cuts.append(box(0,9.85,41.4 if buried else 29.2,2.2,2.1,18.0 if buried else 30.2).rotate((0,0,ang)).translate((tx,ty,0)))
 if not buried:
  cuts.append(box(0,9.75,18.5,4.6,2.3,14.0).rotate((0,0,ang)).translate((tx,ty,0)))
  for dx in [-3,3]:cuts.append(box(dx,9.85,12.0,1.65,1.9,2.5).rotate((0,0,ang)).translate((tx,ty,0)))
  cuts.append(box(0,9.85,3.8,6.0,1.9,5.3).rotate((0,0,ang)).translate((tx,ty,0)))
# A east main elevation: 22 broad upper bays and 36 narrow slots below.
# Lower floors have distinct wide grouping; north projecting glass bay masks part of 2/3F.
for y in np.linspace(-40,45,P['east_top_bays']):cuts.append(box(67.55,y,33.1,2.05,2.65,5.7))
for y in np.linspace(-40,29,P['east_narrow_row_bays']):cuts.append(box(67.55,y,24.2,2.05,1.25,6.0))
for y in [-39,-36.6,-34.2,-31.8,-29.4]:cuts.append(box(67.55,y,14.6,2.05,1.3,5.5))
for y in np.linspace(-9,44,13):
 if y>29:continue
 cuts.append(box(67.55,y,14.1,2.05,2.9,5.7))
for y in np.linspace(-40,44,21):
 if -28<y<-12:continue
 cuts.append(box(67.55,y,4.0,2.05,2.8,5.5))
# Entrance arcade lies along the eastern facade, not on the short D north end.
add(70.6,2,10.1,5.6,91,1.7)
for y in [-40,-32,-11,-3,5,13,21,29,37,45]:add(72.0,y,2.4,1.8,1.8,7.9)
add(70.5,-20,17.5,8.5,17,1.8);hip(70.4,-20,18.9,8.7,18.2,2.8)
for y in [-27.4,-12.6]:add(73.2,y,2.4,2.2,2.2,15.8)
cuts.append(box(67.1,-20,3.0,4.1,11.5,11.9))
# Broad approach remains within the base footprint.
for i in range(3):add(72.4+i*.55,-20,2.4,2.6,21,1.8-i*.5)
# D northern outside, observed in rear 2013 photo: upper broad windows, narrow below.
for x in np.linspace(2,62,12):
 cuts.append(box(x,57.05,33.1,2.9,2.05,5.7))
 for off in [-1.1,1.1]:cuts.append(box(x+off,57.05,24.0,1.3,2.05,6.0))
 cuts.append(box(x,57.05,14.2,2.9,2.05,5.7))
 cuts.append(box(x,57.05,4.1,2.9,2.05,6.0))
# East side approach and projecting low curved stair at southern corner.
# Southeast footprint occupied by the tower; do not add an invented separate drum.
# A inner court has four rows, with a half-drum glazed staircase near middle.
for y in np.arange(-39,36,6.0):
 if abs(y+5)<11:continue
 for z in [4.0,14.0,23.6,33.1]:cuts.append(box(50.4,y,z,2.2,4.2,6.3))
parts.append(cyl(50.1,-5,10.8,6.2,27.8,32))
for a in [120,150,180,210,240]:
 ar=math.radians(a)
 c=box(0,0,12,2.0,1.6,24.7).rotate((0,0,a-90)).translate((50.1+6.0*math.cos(ar),-5+6.0*math.sin(ar),0));cuts.append(c)
# D courtyard side upper broad bays, avoiding overlap with A and tower ends.
for x in np.linspace(3,47,10):
 for z in [4.1,14.0,23.6,33.0]:cuts.append(box(x,38.9,z,3.2,2.1,6.3))
# B outside: 3F west main roof and 4F east roof are visibly different elevations.
for x in np.arange(-60,52,5.5):
 for z in [4.0,13.7,23.1]:cuts.append(box(x,-60.55,z,3.4,2.05,5.8))
 if x>=21:cuts.append(box(x,-60.55,33.1,3.4,2.05,5.7))
# B courtyard tall open balcony recesses, with a thick parapet (backing retained).
for x in np.arange(-59,51,6.8):
 if 7<x<32:continue
 for z in [4.0,13.7,23.1]:
  if x<-34 and z<20:continue
  cuts.append(box(x,-43.5,z,4.6,4.4,6.0))
 if x>=21:cuts.append(box(x,-43.5,33.1,4.6,4.4,5.7))
# Low diagonal C–B gallery spans the courtyard but is open beneath the beam.
p0=(-52,40);p1=(25,-43)
parts.append(beam_between(p0,p1,19.8,8.0,2.2))
for t in np.linspace(0,1,12):
 x=p0[0]+t*(p1[0]-p0[0]);y=p0[1]+t*(p1[1]-p0[1]);add(x,y,2.4,2.1,2.1,17.5)
# Raised northwest triangular landing and short blue truss link to the tower-side arm.
parts.append(poly([(-64,43),(-44,22),(-32,33),(-43,44)],2.4,17.5))
parts.append(beam_between((-43,32),(-12,48),19.8,5.8,2.2))
for t in [0,.33,.66,1]:
 x=-43+31*t;y=32+16*t;add(x,y,21.8,1.8,1.8,6.8)
for off in [-2.2,2.2]:
 parts.append(beam_between((-43,32+off),(-12,48+off),27.2,1.8,1.6))
# Thickened X braces preserve the photographed blue steel bridge identity.
L=math.hypot(31,16);theta=math.degrees(math.atan2(16,31))
for side in [-2.0,2.0]:
 for j in range(2):
  u,v=j*L/2,(j+1)*L/2
  for lo,hi in [(21.8,27.7),(27.7,21.8)]:
   pts=[(u-.7,lo),(u+.7,lo),(v+.7,hi),(v-.7,hi)]
   if hi<lo:pts.reverse()
   brace=CrossSection([pts]).extrude(1.8).rotate((90,0,0)).translate((0,side+.9,0)).rotate((0,0,theta)).translate((-43,32,0));parts.append(brace)
# Court's curved low glass display / memorial library: sloping half-drum and roof terrace.
# Composite two lobes approximates observed S curve; glazing mullions are thick ribs.
for x,y,r in [(15,-37,12),(27,-43,7.0)]:
 cone=Manifold.cylinder(11.3,r,r-1.9,48).translate((x,y,2.4));parts.append(cone)
 parts.append(cyl(x,y,13.4,r-1.6,1.5,48))
for a in [20,45,70,95,120,145]:
 ar=math.radians(a);cuts.append(box(0,0,4,2.3,1.4,8.5).rotate((0,0,a-90)).translate((15+11.2*math.cos(ar),-37+11.2*math.sin(ar),0)))
# C auditorium exposed west wall: two generous rows, not invented five-storey windows.
for y in np.arange(-26,17,6.0):
 for z in [4.3,16.1]:cuts.append(box(-64.05,y,z,2.1,4.0,7.0))
# C court wall upper 10 bays; the diagonal gallery leaves this side partly concealed.
for y in np.linspace(-27,14,10):
 for z in [4.3,16.1]:cuts.append(box(-33.95,y,z,2.1,2.7,7.0))
# A/B cornices terminate at their own levels; a new roof terrace is not flattened to one z.
for z in [11.4,21.2,31.0,40.0]:
 add(31,48,z,73.6,18.6,.9);add(59,-1,z,17.6,104.6,.9)
for z in [11.4,21.2,30.8]:add(-7,-52,z,115.6,17.6,.9)
solid=parts[0]
for p in parts[1:]:solid+=p
for c in cuts:solid-=c
for p in after:solid+=p
assert str(solid.status())=='Error.NoError',solid.status()
assert len(solid.decompose())==1,[(s.volume(),s.bounding_box()) for s in solid.decompose()]
m=solid.simplify(.001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,len(mesh.faces),mesh.is_watertight)
