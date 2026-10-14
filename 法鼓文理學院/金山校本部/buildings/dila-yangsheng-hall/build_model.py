"""法鼓揚生館來源限定外觀近似。單位mm；原創源，不含第三方mesh。
Plan pixels from published 1248x1721 court-level drawing; no official scale bar.
0.0603 m/px reconciles roof lengths with NLSC, NOT an engineering measurement.
"""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection,Mesh64
R=Path(__file__).resolve().parent;S=1.7;P=.0603*S;BASE=1.6;DATUM=4.0
parts=[];cuts=[];late=[]
def xy(x,y):return ((x-550)*P,(850-y)*P)
def z(h):return BASE+h*S
def cs(p):
 if sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))<0:p=p[::-1]
 return CrossSection([p])
def poly(p,lo,hi):return cs([xy(*a) for a in p]).extrude((hi-lo)*S).translate((0,0,z(lo)))
def box(x0,y0,x1,y1,lo,hi):return poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],lo,hi)
def add(*a):parts.append(box(*a))
def cut(*a):cuts.append(box(*a))
# Continuous base, upper arrival datum and deliberately bounded hillside.
parts.append(Manifold.cube((100,150,BASE)).translate((-50,-75,0)))
add(190,270,930,1050,-.05,DATUM)
add(650,1050,930,1410,-.05,DATUM)
add(190,180,940,400,-.05,6.0)
# Main gym upper solid and lower support volume. 7m clear court is NOT 5 equal storeys.
add(220,287,645,1000,-.05,DATUM+8.7)
add(270,287,645,1000,DATUM+8.4,DATUM+17.0)
add(260,282,650,1005,DATUM+16.4,DATUM+17.0)
# Western external strip exists in plan/aerial. Height is conservatively bounded,
# not measured from south projecting-window photographs.
add(210,340,270,1000,DATUM+7.9,DATUM+8.6)
# Low relief roof light/height bands, not asserted saw-tooth engineering sections.
for y in [360,485,610,735,860]:
 pp=[(y-24,DATUM+16.95),(y+24,DATUM+16.95),(y+16,DATUM+17.4),(y-16,DATUM+17.4)]
 q=cs([((850-a)*P,z(b)) for a,b in pp]).extrude((625-285)*P)
 late.append(q.transform(np.array([[0,0,1,(285-550)*P],[1,0,0,0],[0,1,0,0]],dtype=float)))
# Five western U-plan projecting boxes; their outward faces remain opaque.
WEST_BOX_Y=[414,536,658,780,902]
for y in WEST_BOX_Y:
 add(239,y-29,276,y+29,DATUM+8.7,DATUM+16.95)
 for side in [-1,1]:
  edge=y+side*29
  for lo,hi in [(9.15,11.55),(12.25,16.35)]:
   cut(247,edge-7,268,edge+7,DATUM+lo,DATUM+hi)
# One south projecting box: front solid face, glazing on both return faces.
add(315,995,392,1040,DATUM+8.7,DATUM+16.95)
for x in [315,392]:
 for lo,hi in [(9.15,11.55),(12.25,16.35)]:cut(x-7,1005,x+7,1032,DATUM+lo,DATUM+hi)
# Southern lower broad glazing in 3 structural bays, not copied around unseen west.
for a,b in [(280,380),(402,503),(525,625)]:
 for lo,hi in [(.65,3.5),(4.8,7.8)]:cut(a,990,b,1008,DATUM+lo,DATUM+hi)
 for x in np.linspace(a+15,b-15,4):
  for lo,hi in [(.65,3.5),(4.8,7.8)]:late.append(box(x-4,988,x+4,995,DATUM+lo,DATUM+hi))
# Five-storey narrow long block. Upper two floors cantilever past the recessed foot.
FLOORS=[0,4.1,8.6,13.3,17.9,22.7]
add(687,395,895,1330,-.05,DATUM+12.5)
add(687,395,895,1380,DATUM+12.5,DATUM+22.15)
# Broad west open circulation bays with real structural piers and thickened low rails.
BAYS=[395,480,596,718,838,958,1100,1223,1344,1380]
for i,(lo,hi) in enumerate(zip(FLOORS[:-1],FLOORS[1:])):
 end=1330 if i<3 else 1380
 for a,b in zip(BAYS[:-1],BAYS[1:]):
  if a>=end:continue
  b=min(b,end)
  if b-a<35:continue
  cut(680,a+12,735 if i>=3 and a>=1223 else 746,b-12,DATUM+lo+.55,DATUM+hi-.55)
  late.append(box(688,a+6,697,b-6,DATUM+lo+.45,DATUM+lo+1.05))
# South common tall frame: one large recess, with a thin inset intermediate slab.
cut(748,1325,830,1388,DATUM+13.0,DATUM+22.05)
late.append(box(747,1323,831,1377,DATUM+17.6,DATUM+18.15))
# Inset rail tops and a finite central post retain open railing rather than a solid band.
for floor,rail0,rail1 in [(13.0,13.55,14.05),(18.15,18.65,19.15)]:
 late.append(box(747,1368,831,1377,DATUM+rail0,DATUM+rail1))
 late.append(box(784,1367,794,1377,DATUM+floor-.1,DATUM+rail0+.2))
# Lower three front levels are not equal repeated square openings.
cut(710,1302,825,1338,DATUM+.55,DATUM+3.55)
cut(710,1302,860,1338,DATUM+4.65,DATUM+8.05)
late.append(box(784,1300,796,1330,DATUM+4.55,DATUM+8.15))
cut(710,1302,765,1338,DATUM+9.15,DATUM+12.1)
# North stair/bridge end stays deeply open, not a sealed dark window.
for lo,hi in zip(FLOORS[:-1],FLOORS[1:]):
 cut(740,387,860,458,DATUM+lo+.55,DATUM+hi-.55)
 late.append(box(739,400,861,409,DATUM+lo+.45,DATUM+lo+1.05))
# East-facing fine fenestration is not fully documented; keep plain mass and bridge.
# Third-floor connective platform follows the published court-level plan; keep gap above.
add(640,480,750,840,DATUM+8.05,DATUM+8.6)
# Roof low parapets and five outlined flat zones, no imaginary towers.
add(680,390,900,1385,DATUM+21.95,DATUM+22.7)
cut(690,400,890,1375,DATUM+22.15,DATUM+23.0)
for a,b in [(430,590),(610,770),(790,950),(980,1140),(1160,1330)]:
 late.append(box(715,a,860,b,DATUM+22.1,DATUM+22.45)-box(725,a+10,850,b-10,DATUM+22.18,DATUM+22.6))
# Short north and east bridges terminate at this model scope, not entire dormitory/road.
add(777,180,820,400,DATUM+8.0,DATUM+8.6)
add(895,630,1005,675,DATUM+8.0,DATUM+8.6)
for x0,x1 in [(777,785),(812,820)]:add(x0,180,x1,400,DATUM+8.5,DATUM+9.45)
for y0,y1 in [(630,638),(667,675)]:add(895,y0,1005,y1,DATUM+8.5,DATUM+9.45)
# Rooted model end supports are bounded print simplifications of cut bridge stubs.
add(777,180,820,195,5.9,DATUM+8.1)
add(990,630,1005,675,-.05,DATUM+8.1)
# Stair profiles are single solids, avoiding overlapping near-coincident tread slivers.
def stair(y0,y1,x0,x1,lo,hi,n):
 L=(y0-y1)*P;bottom=-.05 if y0>1000 else lo-.05;profile=[(0,z(bottom)),(L,z(bottom)),(L,z(hi-.01))]
 for i in range(n-1,-1,-1):
  profile.append((L*i/n,z(lo+(hi-lo)*(i+1)/n-.01)))
  if i:profile.append((L*i/n,z(lo+(hi-lo)*i/n-.01)))
 q=cs(profile).extrude((x1-x0)*P)
 late.append(q.transform(np.array([[0,0,1,(x0-550)*P],[1,0,0,(850-y0)*P],[0,1,0,0]],dtype=float)))
stair(1520,1348,218,682,0,2.0,12)
stair(1352,1098,298,682,2.0,6.2,24)
add(300,1000,680,1110,-.05,6.2)
# Retaining flanks follow the stair grade, with finite high-end plateaus.
def flank(x0,x1,yfront,yback,frontheight,backheight):
 profile=[((850-yfront)*P,z(-.05)),((850-yback)*P,z(-.05)),((850-yback)*P,z(backheight)),((850-yback-40)*P,z(backheight)),((850-yfront)*P,z(frontheight))]
 q=cs(profile).extrude((x1-x0)*P)
 parts.append(q.transform(np.array([[0,0,1,(x0-550)*P],[1,0,0,0],[0,1,0,0]],dtype=float)))
flank(205,220,1522,1348,.4,2.2)
flank(285,300,1352,1098,2.2,6.4)
flank(680,700,1522,1098,.4,6.5)
# One north stair run visible behind the bridge landing, simplified backed mass.
stair(450,405,758,840,DATUM+8.6,DATUM+13.3,12)
late.append(box(758,395,840,406,DATUM+8.5,DATUM+13.3))
# Common 0.00001 mm construction grid applied to each authored primitive before CSG.
# Prevents CrossSection axis permutation rounding from creating coincident slivers.
def construction_grid(p):
 m=p.to_mesh64()
 return Manifold(Mesh64(np.ascontiguousarray(np.round(np.asarray(m.vert_properties),5),dtype=np.float64),np.array(m.tri_verts,dtype=np.uint64,order="C",copy=True)))
parts=[construction_grid(p) for p in parts]
cuts=[construction_grid(p) for p in cuts]
late=[construction_grid(p) for p in late]
solid=parts[0]
for p in parts[1:]:solid+=p
for c in cuts:solid-=c
for p in late:solid+=p
print('components',[(s.volume(),s.bounding_box()) for s in solid.decompose()]);assert len(solid.decompose())==1
m=solid.to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True);mesh.export(R/'model.stl');print(mesh.extents,mesh.is_watertight)
