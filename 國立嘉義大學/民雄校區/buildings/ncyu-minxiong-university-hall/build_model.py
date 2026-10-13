"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. No survey; public plan used only for exterior arrangement.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def gable(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x,z+h)],y,d))
def arch(x,y,z,w,h,depth):
 r=w/2; spring=z+h-r
 pts=[(x-r,z),(x+r,z),(x+r,spring)]
 pts += [(x+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,25)[1:]]
 return profile(pts,y,depth)
def arch_cut(x,y,z,w,h,depth):cuts.append(arch(x,y,z,w,h,depth))
def arch_trim(x,y,z,w,h):
 # Backed relief ring, fused into the wall, not a separate floating shell.
 details.append(arch(x,y,z,w+1.7,h+.85,1.7)-arch(x,y-.1,z-.2,w,h+.2,2.3))
def hip(x,y,z,w,d,h):parts.append(CrossSection.square((w,d),center=True).extrude(h,scale_top=(.72,.03)).translate((x,y,z)))
def column(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
def step(x,y,w,n=3):
 for i in range(n):add(x,y+i*1.4,2.8,w,1.7,.7*(i+1))
# B02 University Hall. Approximate exterior informed by official first-floor plan,
# official front photographs, Google aerial view, 2011 east/west street imagery.
# Plan coordinates derive visually from the published drawing, NOT a measured CAD trace.
S=.125
def xy(p):return ((p[0]-625)*S,(445-p[1])*S)
def planpoly(points,z,h):
 pts=[xy(p) for p in points][::-1]
 return CrossSection([pts]).extrude(h).translate((0,0,z))
def block(x0,y0,x1,y1,h,z=2.8):
 a,b=xy((x0,y0)),xy((x1,y1));add((a[0]+b[0])/2,(a[1]+b[1])/2,z,abs(b[0]-a[0]),abs(b[1]-a[1]),h)
def edge_windows(p,q,z,h,n,w=None,depth=2.2):
 a=np.array(xy(p));b=np.array(xy(q));v=b-a;L=float(np.linalg.norm(v));u=v/L;ang=math.degrees(math.atan2(v[1],v[0]));gap=L/n
 for k in range(n):
  c=a+u*gap*(k+.5);ww=w if w else gap-1.5
  cuts.append(box(0,0,z,ww,depth,h).rotate((0,0,ang)).translate((c[0],c[1],0)))
def trim(p,q,z,w=1.3,h=1.3):
 a=np.array(xy(p));b=np.array(xy(q));v=b-a;c=(a+b)/2;L=float(np.linalg.norm(v));ang=math.degrees(math.atan2(v[1],v[0]));details.append(box(0,0,z,L+.3,w,h).rotate((0,0,ang)).translate((c[0],c[1],0)))
add(0,0,0,150,118,3)
# Main auditorium and tall backstage volumes, with differently stepped rooflines.
block(575,145,975,445,46)
block(430,60,580,442,53)
block(282,205,435,365,37)
block(570,100,1005,153,41)
block(570,435,1010,490,27)
# Separate lower lecture hall and northern support wing, joined by real corridors.
block(430,486,722,837,33)
block(104,374,215,635,31)
block(207,365,290,418,22)
block(210,540,437,635,23)
block(278,365,432,488,27)
block(278,625,436,715,24)
# South-side exhibition lobby and projecting corner service cores.
block(974,145,1119,432,31)
block(1004,35,1120,151,36)
block(1042,146,1153,205,39)
block(1004,432,1120,495,34)
block(1042,377,1153,436,39)
# Lower chamfered entrance lobby; roofs connect to the auditorium and lecture block.
foyer=[(719,483),(1008,483),(1008,616),(883,752),(720,752)]
parts.append(planpoly(foyer,2.8,17.2))
parts.append(planpoly(foyer,19.5,3.4))
# Low pyramidal daylight lanterns on entrance roof. Coarsened, solid-backed.
for px,py in [(765,523),(818,523),(871,523),(924,523),(765,577),(818,577),(871,577),(924,577),(765,631),(818,631),(871,631),(765,685),(818,685)]:
 x,y=xy((px,py));parts.append(CrossSection.square((5.7,5.7),center=True).extrude(4.8,scale_top=(0,0)).translate((x,y,22.7)))
# The visible front glass enclosure is chamfered and inset below a broad brick fascia.
for p,q,n in [((1008,483),(1008,616),4),((1008,616),(883,752),5),((883,752),(720,752),4)]:
 edge_windows(p,q,4.8,13.4,n,depth=3.4)
 trim(p,q,10.5,1.8,1)
# White entrance portal centered in the angled front face, not a detached surface.
a=np.array(xy((1008,616)));b=np.array(xy((883,752)));c=(a+b)/2;ang=math.degrees(math.atan2((b-a)[1],(b-a)[0]))
portal=box(0,0,3,10,5,12)-box(0,.9,3.1,7.1,6.4,8.6)
parts.append(portal.rotate((0,0,ang)).translate((c[0],c[1],0)))
# Roof parapets keep shallow visible recesses but no sealed cavity or invented courtyard.
for rect,z in [((575,145,975,445),48.5),((430,60,580,442),55.5),((430,486,722,837),35.5),((104,374,215,635),33.5)]:
 x0,y0,x1,y1=rect;a,b=xy((x0,y0)),xy((x1,y1));cx,cy=(a[0]+b[0])/2,(a[1]+b[1])/2;ww,dd=abs(b[0]-a[0]),abs(b[1]-a[1]);parts.append(box(cx,cy,z,ww,dd,1.6)-box(cx,cy,z-.1,ww-2.4,dd-2.4,2.0))
# East street elevation is the plan TOP; west is the plan BOTTOM.
# The plan is rotated about 90 degrees relative to north-up aerial imagery.
for z in [6.8,15.8,24.8]:
 edge_windows((635,100),(985,100),z,6.4,7,depth=2.8)
 edge_windows((104,378),(104,630),z,6.0,5,depth=2.6)
 edge_windows((430,720),(430,825),z,6.4,2,depth=2.5)
for z in [6.8,16,25]:
 edge_windows((440,837),(710,837),z,6.4,5,depth=2.6)
edge_windows((635,100),(985,100),35,5.3,7,depth=2.5)
# Glazed strip between south end cores, and narrow stair lights.
for p,q in [((588,100),(622,100))]:
 edge_windows(p,q,6,27,2,depth=2.6)
for p,q in [((282,207),(282,360)),((430,62),(430,201))]:
 edge_windows(p,q,7,7,3,depth=2.5)
# North support block red panels simplified to solid-backed recess rhythm.
for z in [7,16.2,25.4]:edge_windows((108,374),(207,374),z,6.3,2,depth=2.5)
# Visible north-west entrance stairs and landing, all fused into the building/base.
for i in range(6):
 block(224-i*7,437,278,485,.75*(i+1))
block(272,431,285,492,5)
# Plain areas mark unseen/occluded northern service elevations. No generic windows invented.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
