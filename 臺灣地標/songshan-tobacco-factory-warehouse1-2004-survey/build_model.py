#!/usr/bin/env python3
"""Source-qualified Songshan No1 warehouse exterior study; exact and inferred controls distinguished."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
MODEL_MM_PER_METRE=10/3;INTERNAL=1000.;SCALE=MODEL_MM_PER_METRE/INTERNAL
BASE=.60;L=68.435;W=18.18;FLOOR=.65;EAVE=FLOOR+5.029;RIDGE=FLOOR+10.232
PALETTE=[{'id':str(i),'name':n,'hex':c,'evidence':e}for i,(n,c,e) in enumerate([
('Survey wall proxy','#BDB5A3','PDF108 reinforced brick warehouse and wash-pebble finish; uncalibrated display color'),
('Bands and frame','#D0C6B2','PDF271/272 visible facade courses and framing; approximate sections'),
('Pitched roof proxy','#62675B','PDF270/272 dark roof planes, coarse surface proxy not exact tile inventory'),
('Joinery frame','#625C4F','Survey altered door/window formsPDF108/272; not asserted original intact joinery'),
('Opaque glazing','#83948E','Solid display panes; no full interiors'),
('Dark panel or recess','#343934','Dark lower panels and louver backing, opaque simplified condition'),
('Wood corridor supports','#797262','PDF272 shed and annex roof proxy; material uncertain'),
('Low addition roof','#A8A695','PDF272 pale facade fields; no assumed glazing'),
('Authored display support','#D1CABB','Flat authored base, not surveyed topography'),
('Roof-cap proxy','#858779','Unused neutral accent')])]
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

# Coordinates x north->south; y west->east. All z relative authored exterior ground; floor lift estimated separately.
ev='OfficialJanuary2004 surveyPDF268/270–272/274; No1 only, group1939–1940; floor datum offset0.65m is raster estimate'
bx('Authored flat support',[-14.0,-1.4,-BASE],[L+4.6,W+8.8,0],8,'2mm display base, not surveyed topography or section foundations')
bx('No1 main solid envelope',[0,0,0],[L,W,EAVE],0,ev+'; full interior omitted')
add('No1 single longitudinal gable roof',gable(0,L,-.32,W+.32,EAVE-.04,RIDGE),2,'PDF270/271/272 single dual-pitch roof of detached No1, not four joined gables')
for x in np.arange(.35,L,.48):
 for y in [-.32,W+.32]:add('Coarse fall-line roof seam',beam([float(x),y,EAVE+.02],[float(x),W/2,RIDGE+.02],.032,8),2,'Roof texture proxy; exact tile inventory not modeled')
for side,x in [('N',0),('S',L)]:
 add(side+' main gable wall',gable(x-.085,x+.085,0,W,EAVE-.1,RIDGE-.05),0,'PDF271 one independent gable at each end')
 for y in [-.38,W+.38]:add(side+' sloping gable coping',beam([x,y,EAVE+.02],[x,W/2,RIDGE+.12],.09,8),1,'PDF271 raised gable verge simplified coping')
 bx(side+' gable sill band',[x-.11,-.38,EAVE-.10],[x+.11,W+.38,EAVE+.09],1,'Gable horizontal band from271')
 for k in range(4):win(side+f' gable small sash{k}',side,x,W/2+(k-1.5)*1.39,1.12,FLOOR+6.10,.94,3,3,'PDF271 four gridded rectangular high openings; approximately3x3, opaque proxy')
 # Round opening is an explicitly opaque dark marker, not a claim of full interior aperture.
 add(side+' gable round vent opaque field',beam([x-.14,W/2,FLOOR+7.98],[x+.14,W/2,FLOOR+7.98],.40,48),5,'PDF271 round high gable opening, opaque inset proxy')
 bx(side+' finial base',[x-.15,W/2-.15,RIDGE-.02],[x+.15,W/2+.15,RIDGE+.28],1,'PDF271 pointed ridge-end ornament; no lightning-protection claim')
 add(side+' finial tapered stem',cylinder(x,W/2,RIDGE+.25,.76,.11,.045,24),1,'Pointed ridge-end silhouette approximate and thickened for display')
 add(side+' finial tip',cylinder(x,W/2,RIDGE+.99,.75,.045,.008,20),1,'Fine point enlarged, physically untested')
# Nineteen long bays; normalize endpoint discrepancy to selected elevation total.
raw=[3.308]+[3.636]*17+[3.308];bounds=[0]
for q in raw:bounds.append(bounds[-1]+q*L/sum(raw))
centers=[(a+b)/2 for a,b in zip(bounds[:-1],bounds[1:])]
for side,plane in [('W',0),('E',W)]:
 for i,x in enumerate(centers):
  if side=='E' and i>=16:continue
  panel(side+f' tall wall field{i}',side,plane,x-.56,x+.56,FLOOR+1.30,FLOOR+4.02,.095,7,'PDF272 tall pale field below high sash; not declared complete surviving original window')
  for zz in [1.30,4.02]:panel(side+f' field sill{i}',side,plane,x-.60,x+.60,FLOOR+zz,FLOOR+zz+.055,.105,1,'Narrow blank wall field boundary, no internal glazing invented')
  win(side+f' high sash{i}',side,plane,x,1.12,FLOOR+4.12,.58,3,2,'PDF272 small high multi-pane opening, approximately3x2')
  panel(side+f' base vent{i}',side,plane,x-.32,x+.32,FLOOR+.08,FLOOR+.62,.065,5,'PDF272 low dark square ventilation aperture represented opaque')
 for j,x in enumerate(bounds):
  if side=='E' and j>=16:continue
  panel(side+f' wall upright{j}',side,plane,x-.10,x+.10,FLOOR,EAVE,.08,1,'PDF272 vertical wall/pier rhythm, approximate section')
 for z in [.65,1.35,2.55,3.55]:panel(side+' long course',side,plane,0,L,FLOOR+z,FLOOR+z+.06,.055,1,'272 horizontal facade divisions')
 # Small buttresses only at visible source positions, not every bay.
 for j in [9,11,13]:
  x=bounds[j]
  for zz0,zz1,proj in [(0,FLOOR+1.20,.45),(FLOOR+1.20,FLOOR+2.70,.30),(FLOOR+2.70,FLOOR+3.90,.15)]:
   panel(side+' stepped facade buttress',side,plane,x-.17,x+.17,zz0,zz1,proj,1,'PDF272 three visible stepped buttresses near longitudinal bay boundaries9/11/13; other bands not exaggerated into buttresses')
# South open arcade: only five arched openings within No1 footprint, not six dimensional subspans.
PORCH=3.636;PZ=FLOOR-.05;SPRING=FLOOR+2.30;AR=1.14;TOP=FLOOR+4.20
bx('South porch raised platform',[L-.05,-.45,0],[L+PORCH+.4,W+.45,PZ],1,'Survey raised approach/plinth, height approximately0.6m relative exterior datum')
bx('South arcade front wall',[L+PORCH-.32,0,PZ],[L+PORCH,W,TOP],0,'PDF271 five open rounded arches, confined to No1 width')
def arch_x(name,x0,x1,y,r,ev):
 cut(name+' rectangular void',box([x0,y-r,PZ-.02],[x1,y+r,SPRING]),ev)
 cut(name+' round head',beam([x0,y,SPRING],[x1,y,SPRING],r,64),ev)
for i in range(5):arch_x(f'South arcade arch{i}',L+PORCH-.5,L+PORCH+.2,(i+.5)*W/5,AR,'PDF271 five real through-openings, not opaque painted arches')
# Return arch at west end of porch; east end intentionally open where group corridor continues beyond model boundary.
bx('South arcade western return',[L,-.18,PZ],[L+PORCH,.18,TOP],0,'PDF272 west return with one rounded opening')
cut('West porch return rectangular void',box([L+.52,-.4,PZ-.02],[L+PORCH-.52,.4,SPRING]),'272 open west return')
cut('West porch return round head',beam([L+PORCH/2,-.4,SPRING],[L+PORCH/2,.4,SPRING],(PORCH-1.04)/2,64),'272 open west return arched head')
# Porch lean-to extends only across No1 width; continuation beyond east boundary is intentionally omitted.
add('South porch lean-to roof',hull([[x,y,z] for y in [-.42,W+.10] for x,zs in [(L-.12,[EAVE-.22,EAVE-.10]),(L+PORCH+.24,[TOP-.02,TOP+.10])] for z in zs]),2,'PDF271/272 low south porch roof, terminates at explicit model scope boundary')
# Main south entrance behind arcade, not a reconstructed interior.
recess('South main central doorway','S',L,W/2,4.05,FLOOR,3.5,.28,'PDF268/274 central main-hall opening; opaque authored backing')
for k,y in enumerate([W/2-6.1,W/2-4.2,W/2+4.2,W/2+6.1]):win(f'South main high small sash{k}','S',L,y,1.2,FLOOR+3.13,.70,3,2,'PDF274 four smaller high openings behind porch; simplified')
# Northeast/north shed: irregular end footprint and shallow V roof inferred from visible elevations.
NW=-12.647;NE=-10.85;MID=-7.293;NH=FLOOR+3.30
bx('North shed platform',[NW-.45,-.25,0],[.10,W+.25,FLOOR-.08],1,'PDF268/272 north goods-platform/shed, not rails')
# Trapezoid low enclosure beneath shed, with a front face on the diagonal boundary.
add('North low shed enclosure',hull([[x,y,z] for x,y in [(0,0),(0,W),(NE,W),(NW,0)] for z in [FLOOR-.10,NH]]),0,'PDF268 irregular north appended low enclosure; no internal partitions, extent approximate')
for a,b,za,zb in [(0,MID,EAVE-.08,FLOOR+3.55),(MID,NW,FLOOR+3.55,FLOOR+4.35)]:
 # Outer northern roof edge follows trapezoid by using NE at east edge.
 pts=[]
 for y in [-.25,W+.25]:
  bb=b if b!=NW else (NW if y<0 else NE)
  for x,z in [(a,za),(bb,zb)]:pts += [[x,y,z-.11],[x,y,z+.03]]
 add('North shallow V shed roof',hull(pts),6,'PDF272/274 shallow V-like canopy profile; trapezoid plan268, roof material/profiles approximate')
# North visible end low wall has central rectangular door and two small sashes, set on angled boundary.
# Orient small facade panels to the actual diagonal end plane rather than axis-aligned invented facade.
ang=math.atan2(NE-NW,W)
def northface(name,u,w,z,h,mat,ev,depth=.10):
 yy0=u-w/2;yy1=u+w/2
 x0=NW+(NE-NW)*yy0/W;x1=NW+(NE-NW)*yy1/W
 add(name,hull([[x+dx,y,zz] for x,y in [(x0,yy0),(x1,yy1)] for dx in [-depth,.025] for zz in [z,z+h]]),mat,ev)
for k,u in enumerate([4.35,W-4.35]):
 northface(f'North shed sash field{k}',u,1.865,FLOOR+1.15,1.45,4,'PDF271 No1 far-right northern low facade, two side small sashes')
 for j in range(3):northface(f'North shed sash vertical{k}',u-1.865/2+j*1.865/2,.075,FLOOR+1.15,1.45,3,'Approximate2column sash divisions',.15)
 for j in range(4):northface(f'North shed sash rail{k}',u,1.865,FLOOR+1.15+j*1.45/3,.075,3,'Approximate3row sash divisions',.15)
northface('North shed central door opaque field',W/2,4.048,FLOOR,2.85,5,'PDF271 central404.8cm rectangular opening; opaque display backing, not intact historic leaf')
# An open narrow lattice strip remains above the shed wall and below roof.
for j in range(9):
 y0=j*W/9;y1=(j+1)*W/9;x0=NW+(NE-NW)*y0/W;x1=NW+(NE-NW)*y1/W
 add('North visible canopy diagonal',beam([x0,y0,NH],[x1,y1,FLOOR+4.23],.055,8),3,'271 narrow exposed truss-like strip; schematic visible diagonals only, not No1 hidden steel roof system')
for y in [0,W]:
 x=NW+(NE-NW)*y/W;bx('North canopy end upright',[x-.10,y-.10,FLOOR],[x+.10,y+.10,FLOOR+4.35],1,'Visible thin supports to canopy, schematic section')
panel('West north shed neutral door','W',0,NW+3.2-1.05,NW+3.2+1.05,FLOOR,FLOOR+2.55,.075,7,'PDF272 west shed blank rectangular door silhouette; no invented blue glass, east not mirrored')
# East-south low room: visible footprint/three-panel side silhouette, roofing is deliberately neutral proxy.
AX=L-10.90;AY=W+7.70;AH=FLOOR+3.95
bx('East south low attached room',[AX,W-.05,0],[L,AY,AH],0,'PDF268 room walls and272 east low rectangular facade; interiors/fixtures omitted')
bx('East attached room neutral cap',[AX-.08,W-.05,AH-.02],[L+.08,AY+.08,AH+.10],6,'Roof cap is explicit inference:270 blank roof rectangle does not prove material or RC flat roof')
for j in range(3):
 x=AX+(j+.5)*(L-AX)/3
 panel(f'East attached room panel{j}','E',AY,x-1.48,x+1.48,FLOOR+.18,AH-.15,.045,7,'272 east low annex broad pale panels, not invented glass sash')
for x in [AX,AX+(L-AX)/3,AX+2*(L-AX)/3,L]:panel('East attached room upright','E',AY,x-.075,x+.075,FLOOR,AH,.10,1,'272 panel division rhythm approximately three')

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
o=ET.SubElement(res,E('object'),id='2',type='model',name='Songshan No1 warehouse surveyed exterior study2004-01');me=ET.SubElement(o,E('mesh'));vs=ET.SubElement(me,E('vertices'));ts=ET.SubElement(me,E('triangles'))
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
r={'pre_simplify_components':pre_simplify_components,'simplification_tolerance_model_mm':.5*SCALE,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum())for i,p in enumerate(PALETTE)},'source_metres_to_model_mm':MODEL_MM_PER_METRE,'scope':'2004-01 surveyed exterior No1 warehouse only. Group1939–1940 date, no invented single construction year. North irregular shed/south five-arch porch/east low annex; hidden interiors and steel truss omitted. Plan/elevation length discrepancy disclosed; no trial print.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
