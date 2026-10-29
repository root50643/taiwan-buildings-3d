#!/usr/bin/env python3
"""Source-qualified Songshan office exterior study; exact and inferred controls distinguished."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
MODEL_MM_PER_METRE=10/3;INTERNAL=1000.;SCALE=MODEL_MM_PER_METRE/INTERNAL
BASE=.60;L=64.17;F2=5.23;CORNICE=10.40;RIDGE=12.82;SHOULDER=14.88;TOWER=16.87;POLE=20.98
PALETTE=[{'id':str(i),'name':n,'hex':c,'evidence':e}for i,(n,c,e) in enumerate([
('RC facade proxy','#C2C0B3','PDF54/55 RC office1940; display color uncalibrated'),
('Bands and coping','#D4D0C2','PDF256/257 light horizontal facade bands, approximate'),
('Hipped roof proxy','#58645D','PDF255/256 pitched hipped roof planes, not exact tile material inventory'),
('Frames and accents','#55564D','PDF256/257 dark joinery and facade details; approximate enlarged members'),
('Opaque glazing','#829897','Solid display panes, no interior or transparent-glass restoration'),
('Dark recess','#333D3B','Authored opaque doorway backing, not complete interior'),
('Neutral auxiliary','#A3A69B','Approximate flat roof/secondary material'),
('Pale wall field','#B5B9AC','Uncalibrated neutral wall variation'),
('Authored support','#D1CABB','2mm display base, not surveyed terrain'),
('Neutral detail','#858779','Authored accent')])]
items=[];ops=[];cut_items=[];cut_ops=[];ids={}
def box(a,b):
 a=np.round(np.array(a)*INTERNAL);b=np.round(np.array(b)*INTERNAL)
 return mf.Manifold.cube((b-a).tolist()).translate(a.tolist())
def add(name,s,mat,ev):
 s=s.translate([0,0,BASE*INTERNAL]).as_original(); ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':ev})
def bx(name,a,b,mat,ev):add(name,box(a,b),mat,ev)
def cut(name,s,ev):
 s=s.translate([0,0,BASE*INTERNAL]).as_original();ids[int(s.original_id())]=5;cut_items.append(s);cut_ops.append({'name':name,'material':5,'operation':'subtract','evidence':ev})
def hull(pts):return mf.Manifold.hull_points((np.array(pts)*INTERNAL).tolist())
def beam(a,b,r,seg=12):
 a=np.array(a);b=np.array(b);d=b-a;le=np.linalg.norm(d);z=d/le;h=np.array([0,0,1.])if abs(z[2])<.9 else np.array([1.,0,0]);x=np.cross(h,z);x/=np.linalg.norm(x);y=np.cross(z,x)
 return mf.Manifold.cylinder(le*INTERNAL,r*INTERNAL,r*INTERNAL,seg).transform(np.column_stack([x,y,z,a*INTERNAL]))
def cylinder(x,y,z,h,r1,r2=None,seg=64):return mf.Manifold.cylinder(h*INTERNAL,r1*INTERNAL,(r1 if r2 is None else r2)*INTERNAL,seg).translate([x*INTERNAL,y*INTERNAL,z*INTERNAL])
def gable(x0,x1,y0,y1,z0,z1):return hull([[x0,y0,z0],[x1,y0,z0],[x0,y1,z0],[x1,y1,z0],[x0,(y0+y1)/2,z1],[x1,(y0+y1)/2,z1]])
def panel(name,side,plane,u0,u1,z0,z1,depth,mat,ev):
 if side in ('W','E'):
  a,b=(plane-depth,plane+.03)if side=='W'else(plane-.03,plane+depth);bx(name,[u0,a,z0],[u1,b,z1],mat,ev)
 else:
  a,b=(plane-depth,plane+.03)if side=='N'else(plane-.03,plane+depth);bx(name,[a,u0,z0],[b,u1,z1],mat,ev)
def recess(name,side,plane,u,w,z,h,depth,ev):
 # Real 3D recess with explicit author-added blind backing, never closed leaf.
 if side=='W': aa,bb=[u-w/2,plane-.4,z],[u+w/2,plane+depth,z+h]
 elif side=='E': aa,bb=[u-w/2,plane-depth,z],[u+w/2,plane+.4,z+h]
 elif side=='N': aa,bb=[plane-.4,u-w/2,z],[plane+depth,u+w/2,z+h]
 else: aa,bb=[plane-depth,u-w/2,z],[plane+.4,u+w/2,z+h]
 cut(name+' recess cutter',box(aa,bb),ev+'; depth is authored blind-recess proxy, not measured room depth')
 # backing placed deeper than the cutter, intersecting original mass
 backplane=plane+depth+.01 if side in ('W','N')else plane-depth-.01
 panel(name+' dark back surface',side,backplane,u-w/2+.01,u+w/2-.01,z+.01,z+h-.01,.025,5,'Authored dark blind-recess backing, not a door or complete interior; visible depth '+str(depth)+'m')
def win(name,side,plane,u,w,z,h,cols,rows,ev):
 panel(name+' surround',side,plane,u-w/2-.075,u+w/2+.075,z-.075,z+h+.075,.085,3,ev)
 panel(name+' opaque pane',side,plane,u-w/2,u+w/2,z,z+h,.105,4,'Opaque glazing proxy; not restored transparent glass or full interior')
 for i in range(cols+1):
  q=u-w/2+i*w/cols;panel(name+' mullion',side,plane,q-.034,q+.034,z,z+h,.165,3,ev+'; enlarged member width for legibility')
 for i in range(rows+1):
  q=z+i*h/rows;panel(name+' rail',side,plane,u-w/2,u+w/2,q-.034,q+.034,.17,3,ev+'; enlarged member width for legibility')

# Local x north->south, y west->east. Raster-controlled exterior only.
def rounded(a,b,r,steps=6):
 pts=[]
 for cx,cy,start in [(a[0]+r,a[1]+r,180),(b[0]-r,a[1]+r,270),(b[0]-r,b[1]-r,0),(a[0]+r,b[1]-r,90)]:
  for ang in np.linspace(start,start+90,steps+1):
   for z in [a[2],b[2]]:pts.append([cx+r*math.cos(math.radians(ang)),cy+r*math.sin(math.radians(ang)),z])
 return hull(pts)
def hip(x0,x1,y0,y1,z0,z1):
 d=min(x1-x0,y1-y0)/2
 if x1-x0>=y1-y0:return hull([[x,y,z0] for x in [x0,x1] for y in [y0,y1]]+[[x0+d,(y0+y1)/2,z1],[x1-d,(y0+y1)/2,z1]])
 return hull([[x,y,z0] for x in [x0,x1] for y in [y0,y1]]+[[(x0+x1)/2,y0+d,z1],[(x0+x1)/2,y1-d,z1]])
ev='OfficialJanuary2004 PDF253–259;1940 RC office; per-page8m graph scale, approximate±3%, not exact dimensioned survey'
bx('Authored display base',[-5.9,-9.3,-BASE],[L+5.9,40.2,0],8,'2mm flat display support at1:300, not historic ground/foundation')
for name,a,b in [('West U crossbar',[0,0,0],[L,11.96,CORNICE-.30]),('North U arm',[0,11.8,0],[12.53,26.34,CORNICE-.30]),('South U arm',[L-12.62,11.8,0],[L,26.34,CORNICE-.30])]:add(name,rounded(a,b,.28),0,ev+'; solid wall-mass proxy, courtyard stays empty')
# Flat outer gallery/eaves strips and hipped inner pitched roof; do not fill U courtyard.
for name,a,b in [('West flat eave',[0,-.12,CORNICE-.30],[L,3.35,CORNICE]),('North flat eave',[-.12,0,CORNICE-.30],[3.35,26.34,CORNICE]),('South flat eave',[L-3.35,0,CORNICE-.30],[L+.12,26.34,CORNICE])]:bx(name,a,b,1,'PDF255 narrow exterior flat roof/eave strip around inner pitched roof')
for name,rect in [('West inner hipped roof',(3.25,L-3.25,3.25,12.12)),('North inner hipped roof',(3.25,12.65,3.25,26.40)),('South inner hipped roof',(L-12.75,L-3.25,3.25,26.40))]:add(name,hip(*rect,CORNICE-.02,RIDGE),2,'PDF255 U-shaped pitched/hipped roof, approx footprint; not a flat whole building')
# Fine tile texture omitted to avoid unsupported ridges across hipped roof joins.
# Side service projections remain one storey, rounded source corners.
for name,a,b in [('North service pod',[-4.59,18.83,0],[.08,26.34,5.75]),('South service pod',[L-.08,18.83,0],[L+4.42,26.34,5.75])]:
 add(name,rounded(a,b,.55),0,'PDF253 rounded one-storey service projection; lower than two-storey U wing')
 bx(name+' roof band',[a[0]-.08,a[1]-.08,5.60],[b[0]+.08,b[1]+.08,5.83],1,'Low service-pod parapet/cap approximate')
# Central three-storey hall and stepped forward stair/clock tower.
add('Central three-storey hall',rounded([25.10,-3.45,0],[38.90,12.40,SHOULDER],.25),0,'PDF255 central3F block, rear room fromy5to12.4 and front hall; not isolated courtyard structure')
add('Central high stair-clock tower',rounded([28.4,-6.50,0],[35.5,.65,TOWER],.35),0,'PDF255/256 forward high tower, flat top, source proportions approximate')
for name,a,b in [('Three-storey cap',[24.98,-3.57,SHOULDER-.17],[39.02,12.52,SHOULDER+.06]),('Tall tower cap',[28.25,-6.65,TOWER-.14],[35.65,.78,TOWER+.06])]:bx(name,a,b,1,'Thin flat coping at stepped central heights, estimate from256')
# Source-visible flagpole, approximate round section; no flag or safety claim.
add('Central roof pole',cylinder(31.95,-4.6,TOWER,POLE-TOWER,.075,.045,24),3,'PDF256 rooftop vertical pole toapprox20.98m, no invented flag')
# Ground entrance/landing with steps and canopy, source-defined only approximate detail dimensions.
for i in range(5):bx('West entry step',[28.1,-8.50+i*.36,0],[35.8,-6.42,(i+1)*.13],1,'PDF253/256 broad centered entrance stair, simplified count/profile')
recess('West main doorway','W',-6.50,31.95,3.70,.65,2.60,.36,'PDF256 central west entrance; blind display backing, no interior circulation')
bx('West entry canopy',[27.75,-7.0,4.0],[36.15,-6.35,4.22],1,'PDF256 thin canopy below tall stair glazing')
# Large vertical stair glazing, clock-like dial indicated without inventing time.
win('West tower tall glazing','W',-6.50,31.95,2.65,5.25,8.15,3,4,'PDF256 tall central glazed/grille field; grid approximate, opaque')
add('Clock dial marker',beam([31.95,-6.62,15.28],[31.95,-6.54,15.28],.54,48),1,'PDF256 circular clock/dial symbol, time unreadable, no hands invented')
for j in range(12):
 t=j*math.pi/6;x=31.95+math.sin(t)*.43;z=15.28+math.cos(t)*.43
 panel('Clock tick','W',-6.50,x-.025,x+.025,z-.055,z+.055,.15,3,'Twelve schematic tick marks, not asserted exact dial or displayed time')
for xx in [28.4,35.5]:
 for z in np.arange(4.6,TOWER-.3,.66):panel('Tower edge horizontal tick','W',-6.50,xx-.05 if xx<30 else xx-.50,xx+.50 if xx<30 else xx+.05,float(z),float(z)+.07,.14,1,'PDF256 stepped facade horizontal edge accents, approximate spacing')
for x in [26.6,37.4]:
 for z in [1.20,5.78,10.35]:win('West shoulder narrow sash','W',-3.45,x,.90,z,2.35,1,3 if z<2 else 4,'PDF256 three narrow vertical windows on each shoulder, ground/middle/upper levels')
for side,plane in [('N',25.10),('S',38.90)]:
 for z in [1.20,5.78,10.35]:win(side+' shoulder side narrow sash',side,plane,-1.8,.90,z,2.35,1,3 if z<2 else 4,'PDF257 shoulder-side three stacked narrow windows; approximate dimensions, not front-tower side')
for side,plane in [('N',28.4),('S',35.5)]:
 win(side+' front tower base grille',side,plane,-5.1,.60,1.8,.80,4,3,'PDF257 lower grille on forward entrance-tower side; approximate enlarged bars, exact fine pattern omitted')
win('High tower east small sash','E',.65,31.95,1.8,15.25,1.15,2,1,'PDF256 small high opening above central east3F parapet')
# West front window sequences: eight large sashes on each side, each level.
westxs=list(np.linspace(1.85,23.6,8))+list(np.linspace(40.5,L-1.85,8))
for i,x in enumerate(westxs):
 for floor,z in enumerate([1.35,5.90]):win(f'West main sash{i} level{floor}','W',0,float(x),1.36,z,2.75,2,5,'PDF256 west16sashes per level, two-column five-row approximate divisions')
# Central courtyard-facing block, four-window wings each side plus central three-window upper floors.
for i,x in enumerate([14.15,17.45,20.75,24.05,40.15,43.45,46.75,50.05]):
 for floor,z in enumerate([1.35,5.90]):win(f'East crossbar sash{i} level{floor}','E',11.96,x,1.38,z,2.75,2,5,'PDF256 courtyard-facing crossbar opening rhythm, central block separate plane')
for floor,z in enumerate([5.90,10.43]):
 for x in [27.55,32.0,36.45]:win(f'East central level{floor} sash','E',12.40,x,1.42,z,2.80,2,5,'PDF256 three central sash groups per upper level')
for x in [27.55,36.45]:win('East central ground flank sash','E',12.40,x,1.42,1.35,2.75,2,5,'PDF256 ground central door flanked by two sash groups')
recess('East central doorway','E',12.40,32,2.75,.32,3.10,.30,'PDF256 courtyard entrance; opaque backing not interior')
for i in range(3):bx('East entry step',[30.35,12.35,0],[33.65,13.45-i*.25,(i+1)*.12],1,'Courtyard entrance short step proxy')
bx('East entry canopy',[29.5,12.3,3.85],[34.5,13.05,4.0],1,'PDF256 central courtyard door shallow canopy')
# North and south outer wing faces. Ground service pod masks eastern bays.
for side,x in [('N',0),('S',L)]:
 for i,y in enumerate([2.1,5.3,8.5,11.7,14.9,18.1,21.3,24.1]):
  for floor,z in enumerate([1.35,5.90]):
   if floor==0 and y>=18.8:continue
   win(f'{side} outer wing sash{i} level{floor}',side,x,y,1.40,z,2.20 if i==6 else 2.75,2,4 if i==6 else 5,'PDF257 outer wing repeated sash; ground eastern bays obscured by low service projection')
# Low side-pod visible windows, not repeated full-height main sashes.
for side,x in [('N',-4.59),('S',L+4.42)]:
 for y in [20.4,23.8]:win(side+' service pod sash',side,x,y,1.25,1.30,2.2,2,4,'PDF257 low service projection two visible openings, approximate')
for side,y in [('W',18.83),('E',26.34)]:
 for x in [-2.25,L+2.15]:win(side+' pod end sash',side,y,x,1.15,1.45,2.05,2,4,'PDF256 projecting low end shows one sash each side; approximate')
# Plan-confirmed courtyard-side opening positions; unknown height/grid are explicit display proxies.
for side,plane in [('S',12.53),('N',L-12.62)]:
 for floor,z in enumerate([1.6,6.25]):
  for i,y in enumerate([13.8,17.3,20.6,23.6]):
   win(f'{side} inner courtyard neutral opening{i} level{floor}',side,plane,y,1.5,z,1.8,1,1,'PDF253/254 plan marks four openings per level; position approx±0.5m,width1.4–1.6m; height1.8m and plain1x1 pane AUTHOR DISPLAY PROXY, true sill height/leaf-grid unknown')
# East-facing wing-end service fields are not transplanted to the courtyard side planes.
for mirror in [False,True]:
 for level in [0,1]:
  specs=[(4.3,1.35,2.60 if level==0 else 5.90,1.25 if level==0 else 1.0,3),(6.8,1.10,1.45 if level==0 else 5.90,1.65 if level==0 else 1.4,2),(9.5,.70,2.55 if level==0 else 6.40,1.20 if level==0 else 1.3,1),(10.8,.70,2.55 if level==0 else 6.40,1.20 if level==0 else 1.3,1)]
  for i,(x,w,z,h,c) in enumerate(specs):
   win(f'East wing-end service{mirror} field{i} level{level}','E',26.34,L-x if mirror else x,w,z,h,c,3,'PDF256 four service fields outer-to-inner3x3,2x3,1x3,1x3 with staggered sill heights; graphical approximation')
# Two3m-wide12m-long raised connecting galleries, open below, ends intentionally uncapped.
for side,x0 in [('North',0),('South',L-3.0)]:
 x1=x0+3.0;y0=26.34;y1=y0+12.0
 bx(side+' gallery ground platform',[x0-2.0,y0,0],[x1+2.3,y1+.4,.15],1,'PDF253 broad ground platform NOT width of upper gallery')
 for y in [y0+3.0,y0+7.0,y0+11.0]:
  for x in [x0+.14,x1-.14]:add(side+' gallery ground pillar',cylinder(x,y,.12,F2-.12,.15,seg=20),1,'PDF253 three pairs of columns;55 open lower passage')
 bx(side+' gallery upper floor',[x0,y0-.10,F2-.25],[x1,y1,F2],1,'PDF55 upper enclosed gallery3x12m; lower remains open')
 bx(side+' gallery north side wall',[x0,y0-.10,F2],[x0+.20,y1,CORNICE-.2],0,'Upper gallery wall only, no terminal end wall')
 bx(side+' gallery south side wall',[x1-.20,y0-.10,F2],[x1,y1,CORNICE-.2],0,'Upper gallery opposite wall, source55 windows both sides')
 bx(side+' gallery roof slab',[x0-.14,y0-.1,CORNICE-.2],[x1+.14,y1,CORNICE],1,'PDF255 narrow flat covered gallery; east continuation cropped, no fabricated end facade')
 for j,y in enumerate([y0+2.0,y0+6.0,y0+10.0]):
  for s,x in [('N',x0),('S',x1)]:win(side+f' gallery upper sash{j} '+s,s,x,y,1.75 if j==1 else 1.35,6.60,1.8,3 if j==1 else 2,4,'PDF257 three upper-gallery windows2x4/3x4/2x4; paired sides from55')
# Exterior horizontal bands and base rustication. Upper windows stand proud of bands.
for side,plane,u0,u1 in [('W',0,0,25.1),('W',0,38.9,L),('E',11.96,12.53,25.1),('E',11.96,38.9,L-12.62),('N',0,0,26.34),('S',L,0,26.34),('S',12.53,12,26.34),('N',L-12.62,12,26.34)]:
 for z in [1.0,1.65,2.35,3.05,3.75,4.45,5.1,5.45,6.1,6.8,7.5,8.2,8.9,9.65]:panel('Facade horizontal band',side,plane,u0,u1,z,z+.05,.055,1,'PDF256/257 horizontally banded facade, approximate spacing')
 for z in [.20,.55,.90]:panel('Base horizontal rustication',side,plane,u0,u1,z,z+.035,.075,1,'Low block-texture base simplified courses, not exact stone inventory')
 for u in np.arange(u0+.45,u1,.90):panel('Base short vertical joint',side,plane,float(u),float(u)+.025,.10,1.05,.085,3,'Coarse authored block-joint texture at base')
# Central shoulders/thirdfloor east horizontal lines, separate from forward tower.
for side,plane in [('E',12.4)]:
 for z in np.arange(.7,SHOULDER-.4,.7):panel('Central east course',side,plane,25.10,38.90,float(z),float(z)+.045,.055,1,'PDF256 central east horizontal bands')

# All boolean cuts preserve missing apertures; no detailed interior room layout is implied.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
if cut_items:s=s-mf.Manifold.batch_boolean(cut_items,mf.OpType.Add)
pre_simplify_components=[{'volume_mm3':q.volume()*SCALE**3,'bounds_internal':q.bounding_box()}for q in s.decompose()]
s=s.set_tolerance(.5).simplify(.5)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda x:'{'+ns+'}'+x
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Songshan office surveyed exterior study2004-01');me=ET.SubElement(o,E('mesh'));vs=ET.SubElement(me,E('vertices'));ts=ET.SubElement(me,E('triangles'))
for row in v:ET.SubElement(vs,E('vertex'),**{k:f'{float(a):.8f}'for k,a in zip('xyz',row)})
for row,c in zip(f,mi):ET.SubElement(ts,E('triangle'),v1=str(row[0]),v2=str(row[1]),v3=str(row[2]),pid='1',p1=str(c),p2=str(c),p3=str(c))
b=ET.SubElement(root,E('build'));ET.SubElement(b,E('item'),objectid='2')
files={'[Content_Types].xml':'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>','3D/3dmodel.model':ET.tostring(root,encoding='utf-8',xml_declaration=True)}
with zipfile.ZipFile(ROOT/'model.3mf','w',zipfile.ZIP_DEFLATED)as z:
 for name,blob in files.items():
  zi=zipfile.ZipInfo(name,(1980,1,1,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,blob)
parts=[]
for op,item in zip(ops+cut_ops,items+cut_items):
 q=item.to_mesh64();parts.append({**op,'vertices':(np.asarray(q.vert_properties)[:,:3]*SCALE).tolist(),'faces':np.asarray(q.tri_verts).tolist()})
(ROOT/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':')));(ROOT/'editable-parts.json').write_text(json.dumps({'palette':PALETTE,'features':ops+cut_ops},indent=2))
r={'pre_simplify_components':pre_simplify_components,'simplification_tolerance_model_mm':.5*SCALE,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum())for i,p in enumerate(PALETTE)},'source_metres_to_model_mm':MODEL_MM_PER_METRE,'scope':'January2004 surveyed Songshan office exterior;1940 RC U-plan central3floors/two2floorwings, upper enclosed/lower open3x12m galleries truncated at depicted boundary. All graph-scale dimensions approximate±3%; no courtyard buildings from separated roof diagrams, no interiors, trial print or safety claim.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
