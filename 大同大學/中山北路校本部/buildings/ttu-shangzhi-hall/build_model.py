"""大同大學尚志教育研究館：原創有界照片比例外觀模型，非測量BIM。
Local X=east entrance, Y=north low wing. Published photos + plan topology +
NLSC image measures. Height is an adjustable photo approximation, not official.
"""
from pathlib import Path
import numpy as np, math, json
import trimesh
from manifold3d import Manifold, CrossSection, Mesh, OpType
OUT=Path(__file__).resolve().parent
S=150/68;B=2.4;R=11.5;LOW=5.0;DRUM=22.1;APEX=25.5
parts=[];cuts=[];frontframes=[]
def box(x1,x2,y1,y2,z1,z2):return Manifold.cube(((x2-x1)*S,(y2-y1)*S,(z2-z1)*S)).translate((x1*S,y1*S,B+z1*S))
def cyl(x,y,z,h,r,r2=None,n=96):return Manifold.cylinder(h*S,r*S,(r if r2 is None else r2)*S,circular_segments=n).translate((x*S,y*S,B+z*S))
def add(*v):parts.append(box(*v))
def cut(*v):cuts.append(box(*v))
def arch(width,height,depth):
 r=width/2;spring=height-r
 p=[[-r,0],[r,0],[r,spring]]+[[r*math.cos(t),spring+r*math.sin(t)] for t in np.linspace(0,math.pi,21)[1:]]
 return CrossSection([np.asarray(p)*S]).extrude(depth*S).rotate((90,0,0))
def gable(xa,xb,half,zbase,zpeak):
 # Triangular end in YZ extruded along +X.
 p=[[-half,zbase],[half,zbase],[0,zpeak]]
 return CrossSection([np.asarray(p)*S]).extrude((xb-xa)*S).rotate((90,0,90)).translate((xa*S,0,B))
def band_box(xa,xb,ya,yb,z):
 add(xa,xb,ya,yb,z,z+.45)
# Display base with narrow margin, 150mm longest including all exterior stairs.
parts.append(Manifold.cube((58*S,150,B)).translate((-29*S,-75,0)))
# One-storey outer room/terrace wings, surrounding two genuinely open courts.
for xa,xb in [(-19,-9.5),(9.5,19)]:add(xa,xb,-31,31,-.04,LOW)
for ya,yb in [(-31,-26),(26,31)]:add(-19,19,ya,yb,-.04,LOW)
# Roof cornices retain open courtyard topology, rather than a filled rectangle.
for xa,xb in [(-19.3,-9.2),(9.2,19.3)]:add(xa,xb,-31.2,31.2,4.6,5.15)
for ya,yb in [(-31.2,-25.7),(25.7,31.2)]:add(-19.3,19.3,ya,yb,4.6,5.15)
# Main full rotunda, including its upper drum.
parts.append(cyl(0,0,-.03,DRUM+.18,R,n=160))
for z,r,h in [(4.65,11.65,.45),(16.55,11.85,.65),(20.65,11.75,.60)]:parts.append(cyl(0,0,z,h,r,n=160))
# Shallow external cap, independently adjustable rise; not a hemisphere.
# Profile z=DRUM+rise*(1-(r/R)^2)^0.80. Original triangle mesh, solid to drum.
DOME_R=11.72
profile=[[0,DRUM-.45],[DOME_R,DRUM-.45],[DOME_R,DRUM]]
for rr in np.linspace(DOME_R,0,44)[1:]:
 profile.append([rr,DRUM+(APEX-DRUM)*max(0,1-(rr/DOME_R)**2)**.80])
dome=CrossSection([np.asarray(profile)*S]).revolve(circular_segments=160).translate((0,0,B))
parts.append(dome)
# Small roof-top collar, thick rooted annulus; fine antenna omitted.
parts.append(cyl(0,0,25.15,.85,1.55,n=72).rotate((0,0,1.7)));cuts.append(cyl(0,0,25.55,1.0,.86,n=72).rotate((0,0,1.7)))
# Rotunda's three photographed window rows, restricted to exposed north/south arcs.
# Two portico backing blocks obscure east/west arcs; never duplicate five floors.
for center in [math.pi/2,3*math.pi/2]:
 for off in [-.72,-.36,0,.36,.72]:
  a=center+off;angle=math.degrees(a)
  for z,h in [(.65,3.15),(6.15,3.35),(11.8,3.8)]:
   q=box(R-.38,R+.25,-.85,.85,z,z+h).rotate((0,0,angle));cuts.append(q)
  # Simplified middle-row pediment relief, backed by the rotunda.
  q=gable(R-.15,R+.16,1.12,9.7,10.4).rotate((0,0,angle));parts.append(q)
# Opposite east/west six-column porticos with full-depth voids between columns.
COL_Y=np.linspace(-6.55,6.55,6).tolist()
for side in [-1,1]:
 xa,xb=(9.0,14.05) if side>0 else (-14.05,-9.0)
 add(xa,xb,-7.4,7.4,-.03,16.85)
 xa,xb=(10.0,19.0) if side>0 else (-19.0,-10.0)
 add(xa,xb,-7.7,7.7,4.7,5.25)
 # Six true columns are connected at both lower platform and entablature.
 for y in COL_Y:
  x=side*17.65
  parts.append(cyl(x,y,5.16,10.75,.62,.52,n=48))
  parts.append(cyl(x,y,5.15,.36,.83,n=48))
  add(x-.90,x+.90,y-.90,y+.90,15.7,16.65)
 add(xa-.15,xb+.15,-7.9,7.9,16.4,18.8)
 add(xa-.3,xb+.3,-8.15,8.15,18.35,18.95)
 parts.append(gable(xa-.25,xb+.25,8.05,18.85,22.15))
 # Front cornice follows gable; a shallow triangular inset preserves border.
 front=side*19.25
 inset=gable(front-.16 if side>0 else front-.32,front+.32 if side>0 else front+.16,6.8,19.15,21.65)
 cuts.append(inset)
 # Clock face is a round recess in each pediment, not a floating disk.
 disc=Manifold.cylinder(.45*S,.70*S,.70*S,circular_segments=48).rotate((0,90,0)).translate(((front-.25 if side>0 else front-.20)*S,0,B+20.22*S));cuts.append(disc)
 # Portico rear facade: two visible rows, central door below.
 for y in [-4.1,0,4.1]:
  for z,h in [(5.65,3.1),(11.1,3.6)]:
   if side>0:cut(13.65,14.4,y-.9,y+.9,z,z+h)
   else:cut(-14.4,-13.65,y-.9,y+.9,z,z+h)
 # Backed glazing grid on each portico facade, simplified to major divisions.
 for y in [-4.1,0,4.1]:
  for z,h in [(5.65,3.1),(11.1,3.6)]:
   if y==0 and z<6:continue  # central entrance is a door, not a repeated window
   xx=(13.38,14.22) if side>0 else (-14.22,-13.38)
   frontframes.append(box(*xx,y-.20,y+.20,z-.06,z+h+.06))
   frontframes.append(box(*xx,y-.96,y+.96,z+h*.47-.19,z+h*.47+.19))
 # Broad exterior staircase, 24 coarsened rises. Both ends, no copied front pool.
 for i in range(24):
  inner=18.65+i*9.0/24;outer=18.65+(i+1)*9.0/24+.015;top=5.2*(24-i)/24
  if side>0:add(inner,outer,-8.1,8.1,-.03,top)
  else:add(-outer,-inner,-8.1,8.1,-.03,top)
 # Side stepped cheek walls are source-observed, thickened continuously.
 for i in range(12):
  x0=18.65+i*.75;x1=x0+.77;top=5.35*(12-i)/12+.4
  for ya,yb in [(-9,-8.2),(8.2,9)]:
   if side>0:add(x0,x1,ya,yb,-.03,top)
   else:add(-x1,-x0,ya,yb,-.03,top)
# Low-wing outside arches, inner court arches; backed recesses avoid paper frames.
for side in [-1,1]:
 for y in [-27,-22,-17,-12,12,17,22,27]:
  q=arch(2.65,3.75,.5).rotate((0,0,90)).translate(((18.65 if side>0 else -19.15)*S,y*S,B+.35*S));cuts.append(q)
 # Inner court facade: recessed arched windows + genuinely open end colonnade.
 for y in [-23,-18,-13,13,18,23]:
  q=arch(2.5,3.7,.5).rotate((0,0,90)).translate(((9.2 if side>0 else -9.7)*S,y*S,B+.25*S));cuts.append(q)
# End-gallery openings across the short north/south side of each court.
for side in [-1,1]:
 y=side*26
 for x in [-6,-3,0,3,6]:
  # 2m-clear square colonnade bays through 5m-wide end gallery, open to court.
  if side>0:cut(x-.95,x+.95,25.5,29.5,.05,4.3)
  else:cut(x-.95,x+.95,-29.5,-25.5,.05,4.3)
# Continuous miniature parapets with backed baluster recesses: root >=1.3mm.
# Do not model tiny free balusters which would disappear under erosion.
for xa,xb in [(-19.2,-18.55),(18.55,19.2),(-9.85,-9.2),(9.2,9.85)]:
 for ya,yb in [(-31,-8.2),(8.2,31)]:add(xa,xb,ya,yb,5.05,6.25)
for ya,yb in [(-31.05,-30.4),(-26.35,-25.7),(25.7,26.35),(30.4,31.05)]:add(-19.2,19.2,ya,yb,5.05,6.25)
# Backed baluster rhythm: 0.12m-deep relief, leaving >=0.53m solid rail web.
for side in [-1,1]:
 for y in np.arange(-29.5,30,1.6):
  if abs(y)<8.7:continue
  if side>0:cut(19.08,19.3,y-.42,y+.42,5.30,6.0)
  else:cut(-19.3,-19.08,y-.42,y+.42,5.30,6.0)
for side in [-1,1]:
 for x in np.arange(-17.7,18,1.6):
  if side>0:cut(x-.42,x+.42,30.93,31.15,5.30,6.0)
  else:cut(x-.42,x+.42,-31.15,-30.93,5.30,6.0)
# Pond basins in each open courtyard are low rooted rings, 0.8m wall.
for y in [-20.2,20.2]:
 parts.append(cyl(0,y,-.02,.55,2.7,n=64));cuts.append(cyl(0,y,.20,1,1.9,n=64))
# Western bell, connected with a robust ceiling stem. No narrow dangling wire.
parts.append(cyl(-16.3,0,14.8,1.65,.55,n=48))
parts.append(cyl(-16.3,0,14.1,.9,.82,.55,n=48))
solid=Manifold.batch_boolean(parts,OpType.Add)-Manifold.batch_boolean(cuts,OpType.Add)
solid=solid+Manifold.batch_boolean(frontframes,OpType.Add)
assert solid.status()==__import__('manifold3d').Error.NoError,solid.status()
m=solid.to_mesh();tm=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=False)
assert tm.is_watertight and tm.is_winding_consistent and tm.volume>0
raw=trimesh.exchange.stl.export_stl(tm)
rt=np.frombuffer(raw,offset=84,dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]))['v'].astype(float)
assert (np.linalg.norm(np.cross(rt[:,1]-rt[:,0],rt[:,2]-rt[:,0]),axis=1)>1e-9).all(),'Reject degenerate original binary triangles; change source geometry, never repair'
(OUT/'model.stl').write_bytes(raw)
params={'unit':'mm','scale_mm_per_m':S,'base_mm':B,'outer_low_roof_m':[38,62],'nominal_dome_plan_diameter_m':23,'modeled_dome_eave_diameter_m':2*DOME_R,'height_working_m':26,'height_assumed_range_m':[21,32],'height_is_official':False,'low_terrace_m':5,'column_platform_m':5.2,'column_top_m':16.65,'portico_entablature_top_m':18.95,'pediment_peak_m':22.15,'upper_drum_top_m':DRUM,'dome_apex_m':APEX,'top_collar_m':26,'portico_column_centers_y_m':COL_Y,'courtyard_topology':'two open courts north and south; porticos east and west','window_evidence':'three visible cylinder rows; two rows above raised portico platform; low-wing arches simplified','dimensions_mm':tm.extents.tolist(),'triangles':len(tm.faces),'limits':['水平值為NLSC影像人工取點，非地籍或測量。','26m是照片起始工作值；21–32m是寬假設區間，不是統計信賴界限。','非萬神殿或美國原館尺寸。','北低翼部分窗洞未知；外圈窗與階數作有界簡化。']}
(OUT/'parameters.json').write_text(json.dumps(params,ensure_ascii=False,indent=2));print(params)
