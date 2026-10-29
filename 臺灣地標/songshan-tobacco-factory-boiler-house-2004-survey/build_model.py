#!/usr/bin/env python3
"""Source-qualified 2004-01 surveyed-envelope study of the Songshan boiler house."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
MODEL_MM_PER_METRE=5.0; INTERNAL=1000.0; SCALE=MODEL_MM_PER_METRE/INTERNAL
BASE=.55; L=23.32; W=14.53; XJ=16.67; XH=20.64; WB=9.965; EAVE=9.68; RIDGE=13.15; LOW=4.77
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('plaster','Survey washed-stone concrete proxy','#B4AA91','PDF101 washed-stone finish; monochrome source, warm gray is uncalibrated illustrative palette, not restored/current color'),
('trim','Raised concrete bands','#C5BEA9','PDF279–280 concrete bands, cornices and rounded pilaster terminations; approximate relief'),
('roof','Survey sheet roof proxy','#656B61','PDF278 striped roof and279–280 silhouette; seam count coarse and finish not color calibrated'),
('frame','Timber window frames','#554F42','PDF339 lower timber joinery; upper joinery material approximated, no original color claim'),
('glass','Opaque glazing proxy','#7D9291','Solid opaque glazing; no optical transparency or detailed interiors'),
('dark','Recessed aperture backing','#2D302E','Dark depth proxy at back of missing-leaf openings; not a fabricated door leaf, not full interior'),
('metal','Iron doors and chimney metalwork','#555A53','PDF339 north iron door20 good;279–280 ladder and guard platform, member thickness simplified/enlarged'),
('chimney','Concrete chimney proxy','#AAA58F','PDF104 documented severe cracking; intact outer silhouette only, fine damage omitted and no safety certification'),
('base','Authored display base','#CBC6B4','Flat authored support, not surveyed terrain'),
('stain','Schematic weathering indication','#898571','Known weathering fromPDF101–104, neutral sparse relief not a measured damage map')]]
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
def roundvent(name,side,plane,u,z,r=.50):
 # Embossed ring around solid dark inset: not a full through-wall vent.
 if side in ('W','E'):
  a=[u,plane+(.06 if side=='E'else-.06),z];b=[u,plane+(.19 if side=='E'else-.19),z]
 else:a=[plane+(.06 if side=='S'else-.06),u,z];b=[plane+(.19 if side=='S'else-.19),u,z]
 add(name+' concrete ring',beam(a,b,r+.11,48),1,'PDF279–280 circular upper ventilation pattern; diameter raster-estimated, not table339 timber-window value')
 aa=np.array(a);bb=np.array(b);direction=(bb-aa)/np.linalg.norm(bb-aa);aa=bb-direction*.01;bb=bb+direction*.028
 add(name+' dark inset',beam(aa,bb,r,48),5,'Solid-backed dark circular vent proxy, no detailed interior')
# x increases north-to-south; y west-to-east. Coordinate frame follows north arrowPDF278/338.
ev='Official2004-01 survey reportPDF278–280;1939 boiler building, not a restored/current or exact original1939 model'
bx('Authored flat support',[-.90,-.90,-BASE],[24.22,21.90,0],8,'Authored display base connects building and chimney; not surveyed topography')
# Ground plan rectangular, upper form L-shaped: eastern last high bay is set back.
bx('Full lower footprint',[0,0,0],[L,W,LOW],0,ev+';2332x1453cm overall plan control;1450cm south-elevation alternative retained in documentation')
bx('Northern high block',[0,0,LOW-.05],[XJ,W,EAVE],0,'PDF278 roof L shape and279–280 projection: first four bays full width; inferred upper setback registration to floor column chain')
bx('Southwestern high return',[XJ-.03,0,LOW-.05],[XH,WB,EAVE],0,'PDF278 stepped roof: fifth high bay west portion; east high wall is set back, not a full-width high rectangle; WB9.965m raster registration')
# Main full-width roof and narrower lower gable at southern high return.
add('Main northern gable roof',gable(-.25,XJ+.20,-.28,W+.28,EAVE-.05,RIDGE),2,'PDF278–280 full-width north gable; ridge13.15m raster-derived below ventilator top14.12m')
add('Southwest narrower gable roof',gable(XJ-.25,XH+.25,-.28,WB+.28,EAVE-.05,12.10),2,'PDF279 south view two offset gables; lower forward gable over west return,12.10m estimated not dimension label')
# Explicit low L-shaped flat roof around eastern notch and south end.
bx('Eastern low annex roof',[XJ-.06,WB-.03,LOW-.03],[L+.24,W+.28,LOW+.15],1,'PDF278 unhatched low roof and279 canopy over final two east bays; eastern notch low not missing roof')
bx('Southern low annex roof',[XH-.05,-.25,LOW-.03],[L+.24,WB+.06,LOW+.15],1,'PDF279–280 southern268cm one-storey annex, distinct from high upper return')
# Concrete corner/gable wall caps, beams, cornices and horizontal joints.
for plane,side,end in [(0,'W',XH),(W,'E',XJ),(WB,'E',XH)]:
 start=XJ if plane==WB else 0
 for z in [1.12,2.48,4.00,4.76,6.02,8.10,9.10]:panel('High-wall horizontal band',side,plane,start,end,z,z+.065,.075,1,'PDF279–280 horizontal washed-stone/concrete facade joints; spacing visually registered, not calibrated all measurements')
 panel('High-wall projecting cornice',side,plane,start-.10,end+.10,9.12,9.68,.20,1,'PDF279–280 strong eave band, estimated profile')
for side,plane,u0,u1 in [('N',0,0,W),('S',XH,0,WB),('S',XJ,WB,W)]:
 for z in [1.12,2.48,4.,4.76,6.02,8.10,9.10]:panel('End horizontal band',side,plane,u0,u1,z,z+.065,.075,1,'PDF279–280 end facade horizontal bands; source projection not interior floor division')
 panel('End cornice',side,plane,u0-.16,u1+.16,9.12,9.68,.20,1,'PDF279–280 broad cornice below triangular gable')
# Thin gable outlines sit on roof outer ends, retain rear full gable and forward narrower gable.
for plane,side,width,zz in [(0,'N',W,RIDGE),(XJ,'S',W,RIDGE),(XH,'S',WB,12.10)]:
 xx=plane+(-.29 if side=='N'else .29)
 add('Gable edge slope',beam([xx,-.27,EAVE],[xx,width/2,zz+.08],.08),1,'PDF279–280 gable perimeter; small trim thickness increased')
 add('Gable edge slope',beam([xx,width/2,zz+.08],[xx,width+.27,EAVE],.08),1,'PDF279–280 gable perimeter; small trim thickness increased')
# Vertical gable ends are washed-stone/concrete, not roof sheet material.
for side,plane,width,crest in [('N',-.26,W,RIDGE),('S',XJ+.21,W,RIDGE),('S',XH+.26,WB,12.10)]:
 xx0,xx1=(plane-.065,plane+.025)if side=='N'else(plane-.025,plane+.065)
 tri=hull([[xx0,-.25,EAVE],[xx0,width+.25,EAVE],[xx0,width/2,crest-.02],[xx1,-.25,EAVE],[xx1,width+.25,EAVE],[xx1,width/2,crest-.02]])
 add('Concrete gable end face',tri,0,'PDF279–280 plaster/concrete triangular end gables, distinct from sloping roof sheets')
 for z in [10.22,10.97,11.72,12.47]:
  if z>=crest-.15:continue
  half=(width+.5)/2*(crest-z-.10)/(crest-EAVE)-.16
  panel('Gable horizontal band',side,plane,width/2-half,width/2+half,z,z+.06,.075,1,'PDF279–280 horizontal gable joints; approximate heights')
# Roof monitor/ventilator centered along main ridge, not a skylight.
bx('Ridge monitor backing',[4.30,W/2-.53,12.90],[12.68,W/2+.53,13.84],5,'PDF278 monitor extends about second/third bays; dark closed-backed louvres, length/section raster-estimated')
add('Ridge monitor gable cap',gable(4.17,12.81,W/2-.72,W/2+.72,13.78,14.12),2,'PDF279 total1412cm chooses top of monitor; section1411cm retained as source discrepancy')
for x in np.arange(4.36,12.67,.30):
 for yy in [W/2-.55,W/2+.55]:bx('Monitor vertical louvre',[x-.035,yy-.035,13.14],[x+.035,yy+.035,13.85],6,'PDF279–280 monitor vertical slats; count simplified')
# Coarse sheet seams aligned with pitches, not exact corrugation count.
for x in np.arange(.3,XJ,.62):
 for yy in [-.25,W+.25]:add('Main roof coarse seam',beam([float(x),yy,EAVE+.015],[float(x),W/2,RIDGE+.028],.028),2,'PDF278 striped roof; coarse seams, not individual sheet survey')
for x in np.arange(XJ+.15,XH,.62):
 for yy in [-.25,WB+.25]:add('Return roof coarse seam',beam([float(x),yy,EAVE+.015],[float(x),WB/2,12.125],.028),2,'PDF278 narrower southern roof; coarse seams')
# Explicit upper window and round ventilation rhythm, dimensions raster-estimated separately from339.
bay=[0,4.19,8.385,12.57,16.67,20.64];centers=[(a+b)/2 for a,b in zip(bay[:-1],bay[1:])]
for j,x in enumerate(centers):
 for side,yy in [('W',0),('E',W if j<4 else WB)]:
  win(f'{side} upper sash bay{j+1}',side,yy,x,1.85,5.05,1.90,2,2,'PDF279–280 five upper sashes per long elevation; fifth east sash is on recessed return, sizes inferred from drawing')
  roundvent(f'{side} upper vent bay{j+1}',side,yy,x,8.05)
for side,xx,cent in [('N',0,[2.42,7.265,12.10]),('S',XH,[1.64,4.92,8.20]),('S',XJ,[12.10])]:
 for j,y in enumerate(cent):
  win(f'{side} upper end sash{xx}-{j+1}',side,xx,y,1.85,5.05,1.90,2,2,'PDF279–280 end upper sash groups; three north, forward-south three plus recessed eastern rear-south one')
  roundvent(f'{side} upper end vent{xx}-{j+1}',side,xx,y,8.05,.47)
# Gable louvers, no invention of transparent interior.
for side,xx,y,zh in [('N',-.33,W/2,11.14),('S',XH+.33,WB/2,10.78)]:
 panel('End gable louvre backing',side,xx,y-.80,y+.80,zh,zh+.58,.12,5,'PDF279–280 dark rectangular gable louvres; dimensions inferred')
 for z in np.arange(zh+.05,zh+.58,.12):panel('End gable louvre blade',side,xx,y-.79,y+.79,float(z),float(z)+.045,.17,6,'Simplified louvre relief')
# Ground-level joinery table339: heights x widths, unitsmm; missing leaves are never restored.
for side,plane,u,nu in [('N',0,2.42,1),('N',0,12.1,10),('W',0,centers[0],2),('W',0,centers[3],3),('E',W,centers[0],9),('E',W,22.,8),('W',0,21.98,4),('S',L,1.64,5),('S',L,4.91,6),('S',L,12.1,7)]:
 win(f'Ground timber sash{nu}',side,plane,u,1.80,1.18,2.10,4,5,'PDF338 index and339 Nos1–10:2100x1800mm; local placement raster registered')
# North iron20 present, closed horizontal slats.
panel('North iron door20 leaf','N',0,W/2-1.55,W/2+1.55,0,3.30,.14,6,'PDF339 north door20 iron3300x3100mm markedgood; retained closed')
for z in np.arange(.15,3.28,.15):panel('North door20 slat','N',0,W/2-1.52,W/2+1.52,float(z),float(z)+.042,.21,1,'PDF280 horizontal iron door slats; count simplified')
panel('North door20 central seam','N',0,W/2-.035,W/2+.035,0,3.30,.24,6,'PDF280 double-leaf center')
# Missing west iron leaves21/22/23. Surrounds remain; opening has explicit depth and blind backing.
for nu,x in [(21,centers[1]),(22,centers[2]),(23,centers[4])]:
 recess(f'West missing iron leaf{nu}','W',0,x,3.10,.02,3.30,1.20,'PDF338 west positions and339 explicitlymissing;279/280 drawn outlines not taken as surviving leaves')
 panel(f'West doorway{nu} lintel','W',0,x-1.63,x+1.63,3.33,3.50,.14,1,'PDF280 remaining doorway lintel, dimensions approximate')
recess('South missing door11','S',L,8.0,1.80,.02,2.55,1.05,'PDF339 explicitlymissing overrides279 apparent drawn leaf;2550x1800mm')
# Low east door12 is documentedgood. Internal14/13 are omitted, not falsely moved onto facade.
panel('East low wood door12','E',W,18.65-.90,18.65+.90,0,2.55,.10,3,'PDF338/339 door12 timber2550x1800mm markedgood; in low eastern annex')
win('East door12 upper glazing','E',W,18.65,1.62,1.1,1.35,3,3,'PDF279 glazed upper timber leaf12; lower plain field retained')
# Small door16 and three irregular-use perforations17/18/19 at north side of flue.
panel('East door16','E',W,7.8-.45,7.8+.45,0,2.0,.11,3,'PDF338/339 timber16 2000x900mm markedgood; placement near flue scan estimated')
for nu,x,z,w,h in [(19,4.19,.45,.40,1.80),(18,5.43,.52,.50,.80),(17,6.40,1.35,.50,.80)]:
 recess(f'East later pipe hole{nu}','E',W,x,w,z,h,.75,'PDF338/339 hole, not window; dimensions height x width table. Exact irregular damaged edge simplified rectangular')
# Canopies at lower facade band, not a full extra floor.
for side,plane,start,end in [('W',0,0,XH),('E',W,0,XJ),('N',0,0,W),('S',L,0,W)]:panel('Midheight canopy band',side,plane,start,end,4.69,4.82,.60,1,'PDF279–280 shallow projecting canopy near477cm lower control; projection estimated')
# Pilasters/drainpipes are rounded at their tops, long elevation vertical division rhythm.
for side,plane,start,end in [('W',0,0,XH),('E',W,0,XJ),('E',WB,XJ,XH)]:
 for x in bay:
  if x<start-.01 or x>end+.01:continue
  yy=plane+(-.17 if side=='W'else .17)
  bx('High wall pilaster',[x-.19,yy-.13,0],[x+.19,yy+.13,7.80],1,'PDF279–280 vertical rounded-end facade pilasters; approximate section')
  add('Rounded pilaster top',beam([x,yy-.13,7.80],[x,yy+.13,7.80],.19,24),1,'PDF279–280 rounded termination')
  add('Exposed vertical pipe',beam([x+.06,yy+(-.14 if side=='W'else .14),.1],[x+.06,yy+(-.14 if side=='W'else .14),7.78],.055),6,'Facade vertical pipe schematic; course and section enlarged, not all working plant pipework')
for side,xx,ys in [('N',0,[0,4.59,9.95,W]),('S',XH,[0,3.27,6.55,9.965]),('S',XJ,[W])]:
 for y in ys:
  px=xx+(-.17 if side=='N'else .17);bx('End facade pilaster',[px-.13,y-.16,0],[px+.13,y+.16,7.85],1,'PDF279–280 end vertical pilaster pattern, registered separately from window centers')
  add('End rounded pilaster top',beam([px-.13,y,7.85],[px+.13,y,7.85],.16,24),1,'Rounded ends visible in facade drawing')
# Base-level small ventilation grilles seen in elevations; solid-backed, approximate.
for side,plane,u in [('N',0,2.42),('N',0,12.1),('W',0,centers[0]),('W',0,centers[3]),('E',W,2.42)]:
 panel('Small foundation vent',side,plane,u-.33,u+.33,.22,.69,.10,5,'PDF279–280 small base vents, size raster-estimated; blind-backed')
# Chimney and low exposed flue; source349? correct source104,278–280/338 only.
CX=10.05;CY=W+5.175;CH=36.06
bx('Exposed low flue shell',[CX-.62,W-.05,0],[CX+.62,CY,1.82],7,'PDF278/338 low east flue to chimney;517.5cm wall-to-center offset; flue size approximate')
bx('Flue cap',[CX-.69,W-.08,1.75],[CX+.69,CY,1.93],1,'PDF279–280 low flue cap visible, not an overhead industrial pipe')
recess('Flue side access','N',CX-.62,CY-2.4,.80,.05,1.28,.4,'PDF280 arched low flue access simplified rectangular recess, not a fabricated door')
add('Tapered concrete chimney',cylinder(CX,CY,0,CH,1.25,.70,96),7,'PDF278–280/338 surveyed tapered chimney;36.06m north-label control,35.96m south alternative not averaged;2.50m base diameter and1.40m mouth outer diameter are scan estimates')
# Hollow top mouth recess, not capped solid. No invented full internal shaft.
cut('Chimney top-mouth recess',cylinder(CX,CY,CH-2.50,2.60,.49,.49,96),'Authored2.5m blind depth for mouth readability; not measured internal shaft. Full interior excluded')
add('Chimney mouth dark backing',cylinder(CX,CY,CH-2.53,.035,.48,.48,64),5,'Dark blind mouth backing, not full height interior or artificial exterior cap')
# Upper circular platform and rail joins deliberately thickened; no assertion safe to print.
platform= cylinder(CX,CY,34.92,.18,1.08,1.08,64)-cylinder(CX,CY,34.89,.25,.66,.66,64)
add('Chimney top access platform ring',platform,6,'PDF279–280 upper platform below mouth; heights/diameters scan-estimated, not pipe mouth height')
for a in np.linspace(0,2*math.pi,12,endpoint=False):
 xx=CX+1.0*math.cos(a);yy=CY+1.0*math.sin(a);add('Platform guard post',beam([xx,yy,34.98],[xx,yy,35.67],.055),6,'PDF279–280 top guardrail, simplified12posts and enlarged members')
for z in [35.27,35.67]:
 ring=cylinder(CX,CY,z-.045,.09,1.055,1.055,64)-cylinder(CX,CY,z-.06,.12,.945,.945,64)
 add('Platform circular guard rail',ring,6,'Upper rail levels schematic and below36.06m mouth; guardrail not mistaken for height datum')
# Ladder on east face, supported against tapered chimney; avoid floating rungs.
for z in np.arange(2.6,35.15,.40):
 rad=1.25+(.70-1.25)*(z/CH);yy=CY+rad+.045
 add('Chimney ladder rung',beam([CX-.21,yy,float(z)],[CX+.21,yy,float(z)],.045),6,'PDF279 east-facing chimney ladder; count coarse and member diameter enlarged')
for dx in [-.23,.23]:add('Chimney ladder stringer',beam([CX+dx,CY+1.25+.035,2.45],[CX+dx,CY+.70+.035,35.18],.055),6,'PDF279–280 ladder side strings follow taper; offset approximate')
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='Songshan boiler house surveyed-envelope study2004-01');me=ET.SubElement(o,E('mesh'));vs=ET.SubElement(me,E('vertices'));ts=ET.SubElement(me,E('triangles'))
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
r={'pre_simplify_components':pre_simplify_components,'simplification_tolerance_model_mm':.5*SCALE,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum())for i,p in enumerate(PALETTE)},'source_metres_to_model_mm':MODEL_MM_PER_METRE,'scope':'1939 boiler house as described in2004-01 report, surveyed-envelope study: stepped high roof, low annex, flue, chimney. Unknown interior omitted; blind recess backing and model support authored. Fine cracks/decay not replicated. No trial print.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
