#!/usr/bin/env python3
"""Wisteria House pre-restoration surveyed exterior study, drawings2001/2003, not present-day restoration."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
 ('plaster','Washed-stone and plaster proxy','#B9B8AF','Survey266–268 washed-stone/plaster annotations; color illustrative, aggregate not modeled'),
 ('wood','Horizontal timber boards','#A7A195','Survey timber wall white paint annotations; weathering omitted'),
 ('frame','Painted timber frames','#D4D4C8','Survey painted timber window frames; schematic offwhite'),
 ('glass','Opaque glazing proxy','#7F9293','Solid-backed glass surrogate; no full transparent interior'),
 ('roof','Japanese cement cultural tiles','#66716C','Survey272 roof material map: Japanese cultural tiles; approximate uncalibrated grey'),
 ('base','Display base','#B9B6A9','Authored flat support, not sloped garden'),
 ('metal','Corrugated metal proxy','#8C8379','Survey272 metal/corrugated roof annotations; varied old sheets simplified'),
 ('dark','Dark aperture backing','#383A34','Solid-backed recess/vent surrogate'),
 ('brick','Foundation and exposed brick','#8E7A64','Survey plinth and wall footing types; schematic color'),
 ('screen','Pergola and screens','#746C56','Survey272 timber/bamboo canopy screen structure; coarse spacing')]]
SCALE=.10
items=[];ops=[];ids={}
def box(a,b):
 a=np.round(np.array(a)*100);b=np.round(np.array(b)*100);return mf.Manifold.cube((b-a).tolist()).translate(a.tolist())
def add(name,s,mat,evidence):
 s=s.translate([0,0,60]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat,evidence):add(name,box(a,b),mat,evidence)
def arch(w,bottom,spring,rise):
 pts=[(-w/2,bottom),(w/2,bottom),(w/2,spring)]+[(w/2*math.cos(t),spring+rise*math.sin(t))for t in np.linspace(0,math.pi,17)[1:]]
 return mf.CrossSection([(np.array(pts)*100).tolist()]).extrude(120).rotate([90,0,0]).translate([0,60,0])
def hull(pts):return mf.Manifold.hull_points((np.array(pts)*100).tolist())
def hip(x0,x1,y0,y1,z0,z1):
 d=min((y1-y0)/2,(x1-x0)/2)
 rid=([[x0+d,(y0+y1)/2,z1],[x1-d,(y0+y1)/2,z1]] if x1-x0>=y1-y0 else [[(x0+x1)/2,y0+d,z1],[(x0+x1)/2,y1-d,z1]])
 return hull([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0]]+rid)
def beam(a,b,r):
 a=np.array(a);b=np.array(b);d=b-a;L=np.linalg.norm(d);z=d/L;h=np.array([0,0,1.])if abs(z[2])<.9 else np.array([1.,0,0]);x=np.cross(h,z);x/=np.linalg.norm(x);y=np.cross(z,x);return mf.Manifold.cylinder(L*100,r*100,r*100,12).transform(np.column_stack([x,y,z,a*100]))



def gable(x0,x1,y0,y1,z0,z1,axis='y'):
 pts=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0]]
 pts+=([[x0,(y0+y1)/2,z1],[x1,(y0+y1)/2,z1]]if axis=='y'else[[(x0+x1)/2,y0,z1],[(x0+x1)/2,y1,z1]])
 return hull(pts)
def shed(x0,x1,y0,y1,zlo,zhi,axis='y'):
 pts=[[x0,y0,min(zlo,zhi)-.13],[x1,y0,min(zlo,zhi)-.13],[x1,y1,min(zlo,zhi)-.13],[x0,y1,min(zlo,zhi)-.13]]
 pts+=([[x0,y0,zlo],[x1,y0,zlo],[x0,y1,zhi],[x1,y1,zhi]]if axis=='y'else[[x0,y0,zlo],[x0,y1,zlo],[x1,y0,zhi],[x1,y1,zhi]])
 return hull(pts)
def panel(name,side,plane,u0,u1,z0,z1,depth,mat,ev):
 if side in ('F','B'):
  a,b=(plane-depth,plane+.025)if side=='F'else(plane-.025,plane+depth);bx(name,[u0,a,z0],[u1,b,z1],mat,ev)
 else:
  a,b=(plane-depth,plane+.025)if side=='L'else(plane-.025,plane+depth);bx(name,[a,u0,z0],[b,u1,z1],mat,ev)
def window(name,side,plane,u,w,z,h,cols,rows,ev):
 panel(name+' frame',side,plane,u-w/2-.055,u+w/2+.055,z-.055,z+h+.055,.06,2,ev)
 panel(name+' opaque glass',side,plane,u-w/2,u+w/2,z,z+h,.085,3,'Opaque glass proxy; no interior modeled')
 for i in range(cols+1):
  q=u-w/2+i*w/cols;panel(name+' mullion',side,plane,q-.018,q+.018,z,z+h,.13,2,ev)
 for i in range(rows+1):
  q=z+i*h/rows;panel(name+' rail',side,plane,u-w/2,u+w/2,q-.018,q+.018,.15,2,ev)
def shutter(name,side,plane,u,w,z,h,n,ev):
 panel(name+' dark back',side,plane,u-w/2,u+w/2,z,z+h,.09,7,'Solid-backed security grille, not full opening')
 for i in range(n):
  q=u-w/2+.025+(w-.05)*i/(n-1);panel(name+' bar',side,plane,q-.018,q+.018,z,z+h,.15,2,ev)

# Local x west-east / y south-north aligned with survey263–272.
ev='Official survey263–272 dimensioned plans, elevations and roof map, dated2001/06 and2003/03; scan registration approximate'
bx('Authored support',[-.8,-4.2,-.6],[31.2,14.4,0],5,'Author flat display support; garden terrain and perimeter walls omitted')
# West timber wing / connector / raised eastern reinforced-brick addition.
for name,x0,x1,y0,y1,z0,z1,mat in [
 ('West timber main',2.90,11.45,0,5.45,.55,3.45,1),
 ('Central old projecting room',11.45,14.45,0,4.46,.55,3.45,1),
 ('Old central hall and corridor',10.45,17.30,4.46,10.0,.55,3.55,1),
 ('Eastern two-storey hall',17.30,24.75,3.45,9.10,.55,7.25,0),
 ('Eastern entrance and upper room',24.75,29.90,1.35,6.65,.55,7.15,0),
 ('Northern small tea alcove',17.85,21.50,9.10,11.65,.59,3.85,1),
 ('Flower hall east annex',24.75,29.90,6.65,13.45,.59,3.10,1),
 ('West kitchen',1.10,4.15,7.30,13.10,.20,2.65,1),
 ('Staff and service range',4.15,10.45,5.45,13.10,.20,3.05,1),
 ('Northern tea room',10.45,12.95,10.0,13.25,.59,3.55,1),
 ('Northern connector lower',12.95,17.30,10.0,13.45,.59,3.15,1)]:
 bx(name,[x0,y0,z0],[x1,y1,z1],mat,ev+'; interior represented by solid exterior mass')
 for x in [x0+.14,(x0+x1)/2,x1-.14]:
  for y in [y0+.14,y1-.14]:bx(name+' footing',[x-.14,y-.14,0],[x+.14,y+.14,z0+.03],8,'Survey269–271 raised floor/footing principles; pier locations coarse not measured individually')
# Reinforced-brick eastern mass has a continuous plinth, not exposed timber stilts.
for x0,x1,y0,y1 in [(17.30,24.75,3.45,9.10),(24.75,29.90,1.35,6.65)]:bx('Eastern continuous masonry plinth',[x0,y0,0],[x1,y1,.56],0,'Survey266–268 masonry addition reaches base; not copied wooden underfloor piers')
# West main intersecting hip roofs: north-south old roof with south and east returns.
for name,x0,x1,y0,y1,ze,zr in [
 ('West long hip',2.35,11.95,-.45,10.80,3.45,5.17),
 ('West south cross hip',2.35,14.85,-.45,5.70,3.45,5.17),
 ('Central cross hip',10.70,17.55,3.95,10.35,3.55,5.17)]:
 add(name,hip(x0,x1,y0,y1,ze,zr),4,'Survey272 intersecting western hipped roofs, survey266/268 low ridge reference5.17m; valleys/intersections coarse')
# Upper roofs use separate gables, not another hipped volume.
add('Upper hall gable',gable(17.05,25.10,3.15,9.40,7.20,8.56,axis='y'),4,'Survey268 long upper ridge +8.56m and272 E-W roof run; slope estimated')
add('Upper east cross gable',gable(24.35,30.15,1.05,6.95,7.15,8.56,axis='x'),4,'Survey266/268 east cross gable and272 turn, estimated junction')
# Gable infill placed beyond roof solid edge to preserve visible stone/plain triangle.
add('South upper gable face',gable(24.75,29.90,1.00,1.07,7.15,8.50,axis='x'),0,'Survey268 south upper gable infill; material plain washed-stone proxy')
add('West upper gable face',gable(17.00,17.07,3.45,9.10,7.20,8.50,axis='y'),0,'Survey266 blank west upper gable, no fabricated large window')
# Low service, flower-room and northern connecting roofs retained as drawn.
for name,bounds,axis,mat in [
 ('Kitchen metal roof',(.55,4.25,6.65,13.40,2.85,3.12),'x',6),
 ('Service north sheets',(4.20,10.60,9.20,13.40,3.35,3.05),'y',6),
 ('Service middle sheets',(.70,4.20,4.70,7.10,2.45,2.80),'y',6),
 ('North connector sheets',(10.35,17.35,10.0,13.60,3.75,3.25),'y',6),
 ('North alcove roof',(17.60,21.65,8.95,11.85,4.10,4.30),'y',6)]:
 add(name,shed(*bounds,axis=axis),mat,'Survey272 mapped low sheet/translucent roof; slope/end seam estimated')

# Flower hall northern paired folded-gable covers, not a single broad shed.
for x0,x1 in [(24.60,27.35),(27.35,30.10)]:
 add('Flower hall folded roof',gable(x0,x1,6.60,13.62,3.10,4.25,axis='x'),6,'Survey267 north paired triangular folded covers and272 segmented light-sheet roofs; coarse slope registration')
 add('Flower hall north gable infill',gable(x0+.06,x1-.06,13.59,13.67,3.10,4.16,axis='x'),1,'Survey267 timber vertical-board gable end of low flower hall')
 window('Flower hall north high sash','B',13.67,(x0+x1)/2,.92,2.92,.66,2,1,'Survey267 small high windows in folded low roof faces, opaque simplified panes')
 for u in np.arange(x0+.12,x1-.12,.16):
  top=3.1+(4.16-3.1)*max(0,1-abs(float(u)-(x0+x1)/2)/((x1-x0)/2))
  if top>3.13:panel('Flower gable vertical board','B',13.67,float(u),float(u)+.025,3.1,top,.035,1,'Survey267 vertical boards on paired gables; coarse spacing')
# Main brick chimney, evidenced on northern/eastern elevations and roof/plan fireplace position.
bx('Masonry chimney shaft',[24.30,8.55,.55],[24.95,9.18,8.70],8,'Survey266/267 tall brick chimney adjacent to main upper roof; scan-estimated section/height')
bx('Chimney cap',[24.22,8.48,8.67],[25.03,9.26,8.82],8,'Survey chimney simple cap; coarse profile, no flue interior')
for z in np.arange(7.15,8.62,.20):
 panel('Chimney brick course','B',9.18,24.30,24.95,float(z),float(z)+.018,.035,2,'Coarse visible chimney masonry joints, not individual bricks')
# Major facade sash rhythms from four surveyed elevations; frame depths enlarged for printable relief.
# South low timber rooms: one large multipane window, small pair, projecting bay and diamond sash.
window('South west multipane','F',0,4.25,2.05,1.20,1.55,4,4,'Survey268 south low west broad sash; approximate registration')
window('South small sash','F',0,6.55,.82,1.70,1.02,2,2,'Survey268 small intermediate wood sash')
bx('Projected bay solid back',[7.68,-.14,1.60],[9.42,.05,3.13],1,'Survey268 shallow projecting timber bay, depth approximated')
window('South projecting bay','F',-.12,8.55,1.62,1.65,1.42,3,3,'Survey268 projected central wood sash; simplified bay depth')
for x in [10.80,13.20]:
 window('South diamond sash','F',0,x,1.20,1.35,1.45,1,1,'Survey268 diamond wood grille opening, position estimated')
 for a,b in [((x-.56,-.09,2.07),(x,-.09,2.75)),((x,-.09,2.75),(x+.56,-.09,2.07)),((x+.56,-.09,2.07),(x,-.09,1.40)),((x,-.09,1.40),(x-.56,-.09,2.07))]:add('Diamond sash diagonal',beam(a,b,.025),2,'Survey268 diamond grille coarse relief')
# Stone lower east facade: two sets of fullheight doors and three upper windows.
for x in [19.15,22.60]:
 window('South main folding glass doors','F',3.45,x,2.50,.70,2.48,3,1,'Survey268 large lower glass folding doors, opaque surrogate')
for x,w in [(18.85,2.30),(22.10,2.30)]:window('Upper south hall window','F',3.45,x,w,5.02,1.74,2,3,'Survey268 upper south two hall windows with horizontal rails')
window('Upper south end window','F',1.35,27.30,2.05,5.02,1.74,2,3,'Survey268 upper cross-gable sash')
shutter('Upper gable vent','F',1.00,27.33,.30,7.74,.35,3,'Survey268 small gable vent; coarse grille')
# Entry glass field and distinct door beside lower two-storey hall.
window('Entrance timber glazed door','F',1.35,25.52,1.05,.63,2.38,2,4,'Survey268 south main entrance leaf with rails; backing closed')
window('Entrance broad window','F',1.35,27.95,3.10,1.18,1.55,3,1,'Survey268 entrance reception front broad sash')
for i in range(3):bx('Entrance threshold step',[24.90,.75+i*.20,0],[26.20,.97+i*.20,.18+i*.15],0,'Coarse entry threshold transition from survey floor levels; not individually measured step')
# Main-hall outside terrace and two separate pergola fields; no garden planting or perimeter walls.
bx('Hall veranda slab',[17.30,2.0,.10],[24.75,3.55,.72],0,'Survey263 south hall terrace; depth estimated')
for x0,x1,y0,y1,z in [(17.30,24.70,-.10,3.40,3.45),(25.00,29.90,-1.70,1.35,3.10)]:
 for x in [x0,x1]:
  bx('Pergola front post',[x-.07,y0-.07,0],[x+.07,y0+.07,z+.10],9,'Survey272 garden-edge pergola structure adjacent to building, coarse post placement')
 bx('Pergola front beam',[x0-.12,y0-.08,z],[x1+.12,y0+.08,z+.12],9,'Survey272 exposed pergola beam')
 for x in np.arange(x0,x1+.01,.55):bx('Pergola rafters',[float(x)-.035,y0-.12,z+.09],[float(x)+.035,y1+.12,z+.19],9,'Survey272 pergola coarse rafter spacing, not every actual member')
# West timber exposed end, based266; service openings not copied from main rooms.
window('West end double door','L',2.90,1.18,1.05,.58,2.02,2,3,'Survey266 west low entrance, simplified opaque glazed door')
window('West end paired sash','L',2.90,3.55,1.85,1.25,1.65,4,3,'Survey266 west low large sash pair')
window('West service window','L',1.10,9.70,1.18,1.16,.95,2,2,'Survey266 separate low service opening')
# Eastern elevation upper end side windows; lower flower room fronts a boundary and opaque screening.
window('Upper east side window','E',29.90,4.65,1.70,5.0,1.75,2,3,'Survey266 east upper facade visible tall window')
for y in np.arange(6.95,13.20,1.20):
 panel('Flower room east clerestory','E',29.90,float(y),float(y)+.90,2.35,3.00,.08,3,'Survey266 east low clerestory band behind garden/boundary; coarse opaque panes')
# Northern main hall facade: broad horizontal sash and smaller left window; side upper door.
window('North upper hall large sash','B',9.10,21.45,2.50,4.92,1.78,2,3,'Survey267 north upper broad sash')
window('North upper hall small sash','B',9.10,18.65,1.18,5.0,1.70,2,3,'Survey267 north upper narrow sash')
window('North upper end sash','B',6.65,27.30,2.00,5.0,1.72,2,3,'Survey267 northern upper cross wing sash')
# Roof stair head and terrace at north midbody, visible in265/267/272.
bx('Northern stair head',[10.65,10.30,3.55],[14.25,13.30,4.90],1,'Survey265/272 low north stair-head enclosure, not a new main storey')
add('Stair head shallow sheet',shed(10.50,14.40,10.15,13.45,5.02,5.20),6,'Survey267 stair head shallow roof profile')
window('Stair-head northern door','B',13.30,12.85,.90,3.57,1.22,1,1,'Survey267 stair-head door, coarse shortened opening below low roof')
for x in [15.0,16.8]:
 bx('Terrace rail post',[x-.035,13.3,3.2],[x+.035,13.42,4.10],2,'Survey265 north small terrace railing approximate')
bx('Terrace top rail',[14.4,13.3,4.04],[17.1,13.42,4.12],2,'Survey north terrace horizontal railing')
# Northern low hall six-point circular grille and adjacent unequal sash, survey267.
cx,cz,rad=14.85,1.82,.34
circle=mf.CrossSection.circle(rad*100,32).extrude(19).rotate([-90,0,0]).translate([cx*100,13.42*100,cz*100])
add('North hall circular dark window',circle,7,'Survey267 circular northern low hall aperture, location registered to263 north connector; opaque backing')
for t in np.linspace(0,2*math.pi,25)[:-1]:
 add('North round window rim',beam([cx+rad*math.cos(t),13.61,cz+rad*math.sin(t)],[cx+rad*math.cos(t+math.pi/12),13.61,cz+rad*math.sin(t+math.pi/12)],.028),2,'Survey267 round frame coarse segmented rim')
for start in [math.pi/2,-math.pi/2]:
 pts=[[cx+.29*math.cos(start+i*2*math.pi/3),13.62,cz+.29*math.sin(start+i*2*math.pi/3)]for i in range(3)]
 for i in range(3):add('North six-point window grille',beam(pts[i],pts[(i+1)%3],.022),2,'Survey267 six-point star coarse grille, not later alteration')
window('North low narrow sash','B',13.45,13.85,.67,1.50,.92,1,3,'Survey267 small narrow sash next to round window')
window('North low diamond sash','B',13.25,12.10,1.20,1.15,1.35,1,1,'Survey267 northern low diamond sash')
for a,b in [([11.53,13.35,1.18],[12.67,13.35,2.48]),([11.53,13.35,2.48],[12.67,13.35,1.18])]:add('North diamond diagonal',beam(a,b,.025),2,'Survey267 crossing diagonal sash')
add('North low projecting gable awning',gable(11.30,15.65,13.25,13.95,2.88,3.34,axis='x'),6,'Survey267 low small gabled rain cover, horizontal extent/height estimated')
# North upper access door and its short sheet awning.
window('North upper access door','B',9.10,23.60,1.13,4.15,2.12,2,3,'Survey267 high north door right of broad sash; not visible interior landing')
add('North upper door sheet awning',shed(22.94,24.28,9.02,9.80,6.48,6.31),6,'Survey267 short sloping sheet above upper north access, dimensions approximate')

# Northern lower alcove windows and service passages at source elevations.
window('North alcove window','B',11.65,19.0,1.25,1.25,1.3,2,2,'Survey267 low north alcove window')
window('North service double door','B',13.10,5.65,1.60,.23,1.95,2,3,'Survey267 north service doorway, coarse frame')
window('North service small window','B',13.10,8.60,1.20,1.20,.90,2,2,'Survey267 north low service window')
# Coarse horizontal clapboards and washed-stone belt courses distinguish main material zones.
for z in np.arange(.72,3.30,.18):
 panel('South timber weatherboard','F',0,2.91,14.44,float(z),float(z)+.02,.025,1,'Survey268 horizontal timber boards; coarse relief, no peeling paint')
for side,plane,u0,u1 in [('F',3.45,17.30,24.75),('F',1.35,24.75,29.9),('E',29.90,1.35,6.65),('B',9.1,17.3,24.75)]:
 for z in [3.55,4.13,6.82]:panel('Washed-stone level band',side,plane,u0,u1,z,z+.05,.055,0,'Survey266–268 stone facade horizontal division, relief approximate')
# Simple roof tile rows; dense individual scallops and sheet ripples deliberately not reproduced.
for x0,x1,y0,y1,ze,zr in [(2.35,11.95,-.45,10.80,3.45,5.17),(2.35,14.85,-.45,5.70,3.45,5.17),(10.70,17.55,3.95,10.35,3.55,5.17),(17.05,25.10,3.15,9.40,7.20,8.56)]:
 # Fine strips on the front roof pitch, shortened towards hipped corners where applicable.
 for t in [.15,.32,.49,.66,.83]:
  y=y0+(y1-y0)/2*t;zz=ze+(zr-ze)*t+.018;inset=(y1-y0)/2*t if ze<4 else .05
  if x1-x0>2*inset:add('Coarse tile course',beam([x0+inset,y,zz],[x1-inset,y,zz],.018),4,'Roof tiling indicated by sparse relief rows; not full tile geometry')

s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
# Remove only isolated numerical union slivers smaller than 0.001 mm3; actual removed volumes logged.
chunks=s.decompose();removed_slivers=[q.volume()*SCALE**3 for q in chunks if abs(q.volume())<1];s=mf.Manifold.batch_boolean([q for q in chunks if abs(q.volume())>=1],mf.OpType.Add)

m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Wisteria House pre-restoration surveyed exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
for row in v:ET.SubElement(vs,E('vertex'),**{k:f'{float(a):.7f}' for k,a in zip('xyz',row)})
for row,c in zip(f,mi):ET.SubElement(ts,E('triangle'),v1=str(row[0]),v2=str(row[1]),v3=str(row[2]),pid='1',p1=str(c),p2=str(c),p3=str(c))
b=ET.SubElement(root,E('build'));ET.SubElement(b,E('item'),objectid='2')
with zipfile.ZipFile(ROOT/'model.3mf','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
 z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
 z.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))
parts=[]
for op,item in zip(ops,items):
 q=item.to_mesh();parts.append({**op,'vertices':(np.asarray(q.vert_properties)[:,:3]*SCALE).tolist(),'faces':np.asarray(q.tri_verts).tolist()})
(ROOT/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':')));(ROOT/'editable-parts.json').write_text(json.dumps({'palette':PALETTE,'features':ops},indent=2))
r={'removed_numerical_sliver_volumes_mm3':removed_slivers,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Pre-restoration exterior envelope study from surveyed plans2001/2003, including service roofs and raised two-storey eastern section. Garden trees, perimeter walls and interiors excluded. Not present-day restoration or trial print.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
