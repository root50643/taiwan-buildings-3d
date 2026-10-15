"""CYCU Chang Ching Yu library1985: original source-bounded exterior, nominal metres.
7.8m structural grid; section-supported18.85m interpreted1F-to-main-roof, not tower top.
"""
from pathlib import Path
import numpy as np,json,trimesh
from manifold3d import Manifold,CrossSection,OpType
from shapely.geometry import Polygon
O=Path(__file__).parent;P=[];C=[];D=[]
def sec(p):return CrossSection([p if Polygon(p).exterior.is_ccw else p[::-1]])
def poly(p,z,h):return sec(list(map(list,p))).extrude(h).translate((0,0,z))
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
W=59.8;H=36.7;BASE=1.2
# B1 bottom=0,1F=4.0; main roof=22.85, saw peak26.2, core29.2.
P += [box(0,0,0,W-2,H-2,19.4),box(0,0,19.3,W,H,3.55),box(0,0,22.45,W+.6,H+.6,.65)]
# Main terrace and lower conference volume, direction/irregular boundary read from plans.
plaza=[(-11,-17.0),(14,-17.0),(14,-29),(19,-40.5),(-9,-41.3),(-14,-32)]
P.append(poly(plaza,0,8.2))
# Staggered broad flights descend to1F outdoor ground; no full-site or adjacent Huai En hall.
y=-53.2;top=4.0
for flight,(width,cx) in enumerate([(34,2),(29,1),(23,0)]):
 for k in range(5):
  top+=.28
  # Angled short returns broaden towards lower front, not a uniform rectangle.
  footprint=[(cx-width/2,y),(cx+width/2,y),(cx+width/2,y+.48),(cx-width/2,y+.48)]
  P.append(poly(footprint,0,top));y+=.45
 if flight<2:
  P.append(box(cx,y+1.2,0,width-1,2.44,top));y+=2.4
P.append(box(0,-40.95,0,23,1.6,8.2))
# Sloping solid parapet/planter shoulders along side flights, broad rooted abstraction.
for xx in [-17.8,17.8]:
 shoulder=sec([(-52.9,0),(-52.9,4.25),(-40.4,8.5),(-40.4,0)]).extrude(1.2).transform(np.array([[0,0,1,xx-.6],[1,0,0,0],[0,1,0,0]]));shoulder=shoulder^box(xx,-46,0,2,30,8.0);P.append(shoulder)
# Outer1F ground strips and retained sunken basement gardens.
P += [box(-32,0,0,5,52,4),box(32,0,0,5,52,4),box(0,-50,0,68,5,4),box(0,28,0,68,2,4)]
# Front1F terrain buries lower conference basement: only2F-to1F rise exposed.
P.append(box(0,-35.7,0,68,35.1,4.0))
# Rear garden low paving, true solid bottom, outside base does not simulate a through hole.
P += [box(0,23,0,59,10,.7),box(28.8,23,0,1.2,11,4),box(-28.8,23,0,1.2,11,4)]
# Rear bridge at1F, visibly over the lower garden.
P.append(box(14,23,3.4,7,11,.7))
for x in [11.1,16.9]:D.append(box(x,23,0,1.2,1.2,3.6))
# facade tools with face-parallel coordinates; all glazing backed.
def cutface(side,x,z,w,h,depth=.4,offset=0):
 if side=='S' and -21<x<-10:return
 if side=='N' and 10<x<21:return
 if side=='S':C.append(box(x,-H/2+depth/2+offset-.03,z,w,depth+.06,h))
 if side=='N':C.append(box(x,H/2-depth/2-offset+.03,z,w,depth+.06,h))
 if side=='E':C.append(box(W/2-depth/2-offset+.03,x,z,depth+.06,w,h))
 if side=='W':C.append(box(-W/2+depth/2+offset-.03,x,z,depth+.06,w,h))
# Upper narrow row wraps all sides; deep solid header and lower spandrel.
for side,length,count in [('S',W,24),('N',W,24),('E',H,15),('W',H,15)]:
 for x in np.linspace(-length/2+1.4,length/2-1.4,count):cutface(side,x,20.1,.95,2.1,.5)
#4F continuous recessed long glass with subdivision, opposite side walls solid.
for side in ['S','N']:
 for lo,hi in ([(-27.3,-21),(-10,27.3)] if side=='S' else [(-27.3,10),(21,27.3)]):cutface(side,(lo+hi)/2,16.15,hi-lo,2.45,1.35)
 # Deep continuous glass band with backed substantial mullions, not isolated small boxes.
 yy=-17.04 if side=='S' else 17.04
 for x in np.linspace(-26,26,21):D.append(box(x,yy,16.1,.38,.23,2.6))
 for z,h in [(12.0,.8),(15.25,.85)]:D.append(box(0,-17.85 if side=='S' else 17.85,z,56.5,2.7,h))
#3F long glazing band with shallow backed pane divisions, no projecting teeth.
for side in ['S','N']:
 for lo,hi in ([(-27.3,-21),(-10,27.3)] if side=='S' else [(-27.3,10),(21,27.3)]):cutface(side,(lo+hi)/2,12.55,hi-lo,2.55,1.4)
 for x in np.linspace(-26,26,21):D.append(box(x,-16.99 if side=='S' else 16.99,12.5,.38,.23,2.65))
# North1F/2F and basement reveals; west/east upper blank wall retained.
for side in ['N','S']:
 for z,h in [(0.8,2.5),(4.5,2.9),(8.7,2.7)]:
  for j in range(7):
   x=-23.4+j*7.8
   if side=='S' and z<8.2 and -14<x<19:continue
   cutface(side,x,z,6.1,h,1.25)
for side in ['E','W']:
 for z,h in [(0.7,2.6),(4.5,2.7),(8.7,2.7)]:
  for j in range(12):cutface(side,-16.0+(j+.5)*32/12,z,2.0,h,1.2)
# Main2F deep open portico, rear glazing etched into actual back wall.
C.append(box(-1,-17.2,8.2,23,6.0,3.7))
for x in [-11,-3.2,4.6,12.4]:D.append(Manifold.cylinder(3.9,.65,.65,32).translate((x,-17.0,8.2)))
for j in range(8):C.append(box(-10+(j+.5)*20/8,-14.05,8.6,2, .4,2.9))
# Side mid-wall shallow vertical grooves, not invented windows.
for side in ['E','W']:
 for j in range(8):cutface(side,-15+j*4.2,12.2,.45,6.8,.16)
# Broad side ribs return into the observed blank middle wall; no invented upper windows.
for xx in [-29.15,29.15]:
 for yy in np.linspace(-14.7,14.7,8):D.append(box(xx,yy,12.0,1.2,.85,7.35))
# Traced offset windmill cores from official5F plan; no mirror duplication.
pix=lambda p:((p[0]-459.5)*7.8/112,(397-p[1])*7.8/112)
southpx=[(178,644),(220,644),(220,628),(239,628),(239,648),(298,648),(298,774),(239,754),(239,737),(178,718)]
northpx=[(620,23),(679,42),(679,57),(697,57),(697,47),(741,61),(741,148),(700,148),(700,165),(681,165),(681,139),(620,125)]
for pixels in [southpx,northpx]:P.append(poly([pix(q) for q in pixels],0,29.2))
# Adjacent blade steps and narrow recessed seams, solid-backed.
P.append(poly([pix(q) for q in [(239,648),(298,648),(298,774),(239,754)]],0,28.35))
C.append(poly([pix(q) for q in [(239,648),(298,648),(298,774),(239,754)]],28.35,1.2))
C.append(poly([pix(q) for q in [(697,47),(741,61),(741,148),(697,148)]],28.35,1.2))
# Above roof core seam cuts provide split blades without a disconnected sliver.
# Decorative core seam omitted: source notch met slanted outline as continuous thin skin.
#3 sawtooth caps: low south slope, finite-width high north ridge, never symmetric gables.
for y in [-9.2,-3.2,2.8]:
 profile=[(y,22.8),(y,23.13),(y+4.7,26.2),(y+5.5,26.2),(y+5.5,22.8)]
 roof=sec(profile).extrude(42.8).transform(np.array([[0,0,1,-21.4],[1,0,0,0],[0,1,0,0]]));P.append(roof)
 for j in range(16):C.append(box(-20.1+j*2.68,y+5.3,23.6,1.4 if j in [0,15] else 2.1,.5,1.9))
 # round side holes are shallow recesses with broad backing, not through holes.
 for x,rot in [(-21.42,90),(21.42,-90)]:
  disc=Manifold.cylinder(.32,.65,.65,32).rotate((0,rot,0)).translate((x,y+3.6,24.05));C.append(disc)
#4 low square roof covers with backed grid lines, not open courts.
for x in [-24,24]:
 for y in [-13.3,13.3]:
  P.append(box(x,y,23.0,4.4,4.4,.8))
  for t in [-1.1,0,1.1]:C.append(box(x+t,y,23.65,.3,3.2,.3));C.append(box(x,y+t,23.65,3.2,.3,.3))
# Southern conference skylight: four pinwheel triangles verified on2024 ortho.
# Broad solid-backed tilted glass facets; finite ridge face, no free sharp tips.
for angle in [0,90,180,270]:
 rawpts=np.array([(.5,.5),(5.4,.5),(.5,5.4)])
 pts=[]
 for i,v in enumerate(rawpts):
  prev=rawpts[(i-1)%3];nxt=rawpts[(i+1)%3];pts.extend([(v+(prev-v)/np.linalg.norm(prev-v)*.7).tolist(),(v+(nxt-v)/np.linalg.norm(nxt-v)*.7).tolist()])
 cap=poly(pts,8.1,2.4).warp(lambda q:(q[0],q[1],q[2]-max(0,q[2]-8.1)*max(0,min(1,(q[0]-.5)/4.9))*.62)).rotate((0,0,angle)).translate((4,-33,0))
 cap=cap^box(4,-33,8.05,25,25,1.95);P.append(cap)
# Ground/terrace windows of low conference volume only where public old photo shows frontage.
# Window row under exterior stair enclosure omitted rather than creating sealed slots.
solid=Manifold.batch_boolean(P,OpType.Add)-Manifold.batch_boolean(C,OpType.Add)
solid=solid+Manifold.batch_boolean(D,OpType.Add)
solid=solid+box(0,-11.75,-BASE,71,83.5,BASE)
s=150/83.5;solid=solid.scale((s,s,s)).translate((0,0,BASE*s));m=solid.to_mesh64();mesh=trimesh.Trimesh(vertices=np.asarray(m.vert_properties[:,:3],dtype=np.float32),faces=np.asarray(m.tri_verts),process=False);mesh.export(O/'model.stl')
(O/'draft-parameters.json').write_text(json.dumps({'status':'Source-bounded candidate; independent review pending','scale_mm_per_m':s,'main_body_plan_m':[W,H],'official_grid_m':7.8,'official_height_text_m':18.85,'height_interpretation':'Provisional1Fground to main roof from1985sections; not highest tower','source_levels_relative_B1_m':{'B1':0,'1F':4,'2F':8.2,'3F':12.1,'4F':15.7,'5F':19.3,'roof':22.85,'saw_peak':26.2,'core_peak':29.2},'limitations':['Section height reference point requires cross-check; no measured ground elevations','Garden and conference hall depth bounded by sections/photos','Core footprints traced from official diagram; no hidden interior reproduction','Only this library plaza, excluding Huai En hall','Four square roof caps and central hall covered,not open courtyards']},ensure_ascii=False,indent=2));print(mesh.bounds,len(mesh.faces))
