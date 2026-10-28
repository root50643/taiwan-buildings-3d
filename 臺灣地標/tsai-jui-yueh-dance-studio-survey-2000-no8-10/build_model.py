#!/usr/bin/env python3
"""Tsai Jui-Yueh Dance Studio no8/10 survey-form reconstruction study,2000,not restored current condition."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
 ('plaster','Survey plaster wall','#D4D0BC','Report wall survey and drawings193–194; uncalibrated illustrative color'),
 ('wood','Painted timber boards','#9B8D71','Report timber walls and surviving fragments; coarse board relief'),
 ('frame','Timber frames','#C2B79A','Survey window schedule212 old sash not proposed W2 prime grille'),
 ('glass','Opaque glass','#758B87','Closed-backed glass proxy; no interior or transparency'),
 ('roof','Japanese black tile proxy','#565D56','Report94 inferred prefire tiled B-C/C-D roof from surviving tiles and adjacent12; not intact postfire observation'),
 ('base','Display base and research cut','#BAB8AD','Authored display/cut closure, not historic terrain or true no12 endwall'),
 ('metal','Corrugated sheet proxy','#8F9690','Report94 A-B old corrugated asbestos sheets represented only as inert digital geometry; not restoration proposal'),
 ('dark','Aperture backing','#343B33','Opaque recess proxy'),
 ('brick','Brick plinth','#897461','Report foundations/brick walls; coarse representative color'),
 ('screen','Coarse timber grille','#86785B','Survey original door/window/frame relief, not later replacement')]]
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

# Local x follows survey axes1–5; y goes from source north/street towards source south/back.
W=16.18
EV='Official report drawings189–212 dated2000-04-30, cm dimensions; no8/10 axes1–5 only; scan registration estimated'
bx('Authored base',[-.7,-.7,-.6],[W+.7,17.45,0],5,'Flat display base not historic site slope')
# Original B-C range and unequal later front/back additions, not entire four-unit row.
for name,x0,x1,y0,y1,z0,z1 in [
 ('Original main range',0,W,3.89,9.29,.40,3.55),
 ('No8 rear cafe addition',0,7.98,9.29,16.72,.31,3.03),
 ('No10 rear dance addition',7.98,W,7.49,16.72,.40,3.42),
 ('No8 front rooms',0,7.98,0,3.89,.15,2.82),
 ('No10 front kitchen room',7.98,11.10,0,3.89,.20,2.82),
 ('No10 recessed entrance side room',11.10,W,2.75,3.89,.27,2.82)]:
 bx(name,[x0,y0,z0],[x1,y1,z1],0,EV+'; solid exterior study, interior omitted')
 for x in [x0+.12,(x0+x1)/2,x1-.12]:
  for y in [y0+.12,y1-.12]:bx(name+' brick pier',[x-.13,y-.13,0],[x+.13,y+.13,z0+.02],8,'Report foundation survey; sparse supporting piers estimated not individually measured')
# Low floors and entry apron remain connected to authored support.
bx('Recessed no10 entrance apron',[11.1,0,0],[W,3.92,.16],8,'Plan205 stone entry ground+16/+27/+29cm; coarse flat transitions')
# Asymmetric original gable profile with later front roof continuation, sourced section195.
add('Main tiled long roof',hull([[-.25,-.15,2.90],[W,-.15,2.90],[-.25,6.59,4.95],[W,6.59,4.95],[-.25,9.62,3.38],[W,9.62,3.38],[-.25,-.15,2.77],[W,-.15,2.77],[-.25,9.62,3.25],[W,9.62,3.25]]),4,'Report94 complete roof form inferred from surviving tiles/adjacent12, section195 ridge4.95m; not observed intact postfire roof')
# Trim the open entry court from the broad front pitch so front notch is not roofed over.
# Roof eave above entry is retained at y2.6; source plan190 entrance courtyard remains open.
items[-1]=(items[-1]-box([11.10,-.3,-.6],[W+.02,2.60,3.65]).translate([0,0,60])).as_original();ids[int(items[-1].original_id())]=4
# Original gable infill visible outside the roof edge on no8 side.
add('No8 end gable infill',hull([[-.29,0,2.78],[-.29,9.29,3.3],[-.29,6.59,4.86],[-.23,0,2.78],[-.23,9.29,3.3],[-.23,6.59,4.86]]),1,'Section195 and wall survey reconstructed gable wood face; thin outward relief')
add('No8 rear low sheet pitch',shed(-.20,7.99,9.25,16.95,3.58,3.09),6,'Section195 lower rear cafe addition roof, complete roof inferred; coarse sheet relief')
add('No10 rear corrugated double pitch',gable(7.96,W,9.05,16.98,3.44,4.80),6,'Roof plan189 ridge and west194 A-B double pitch ridge480cm; section195 supports independent gable, eave/registration approximate; not proposal109')
add('No10 exposed rear gable timber',gable(7.91,7.965,9.10,16.93,3.43,4.75),1,'West194 horizontal-board rear gable visible above low addition, coarse infill')
# Report77/78 second classroom is the low shed with upper-light wall, not high first-room gable.
for x in [2.15,5.45]:
 z=3.58+(3.09-3.58)*(12.25-9.25)/(16.95-9.25)
 bx('Estimated second-classroom roof light backing',[x-.48,11.8,z-.06],[x+.48,12.75,z+.065],2,'Report77 two rooflights andphoto78 low single-slope second classroom; registered to low rear upper-light area; exact positions/sizes estimated')
 bx('Estimated second-classroom opaque roof light',[x-.41,11.86,z+.06],[x+.41,12.69,z+.10],3,'Opaque skylight proxy in low shed; exact plan placement unmeasured')
# Low rear toilet projections in plan190, kept as modest attached boxes.
for x0,x1,y1 in [(6.55,8.0,17.25),(8.02,10.35,17.08)]:
 bx('Rear toilet small projection',[x0,15.65,.2],[x1,y1,2.85],0,EV+'; projection depth approximate')
 add('Rear toilet shed',shed(x0-.06,x1+.06,15.65,y1+.05,3.06,2.96),6,'Survey190 small rear toilet projections; roof junction schematic')
# North street facade: old cafe doorway and unequal small original sash. Front wall is not a new curtainwall.
window('No8 street double door','F',0,.90,1.40,.16,2.05,2,2,'North elevation193 original cafe entrance old double-leaf arrangement; opaque glazing')
window('Front small clerestory','F',0,4.14,.90,1.78,.44,1,1,'North193 narrow high opening, approximate registered placement')
window('Front long small window','F',0,6.40,1.45,1.20,.75,2,2,'North193 low small wall window, coarse panes')
window('Front kitchen W7','F',0,8.75,1.76,.95,.86,4,3,'Plan190 andschedule212 W7 same W6 old window86x176cm; position estimate')
window('Front room W8','F',0,10.25,1.20,1.02,.80,3,3,'Plan190/schedule212 W8 old window80x120cm; original panes not proposed grille')
# Recessed entry double door at +27cm, connected to upper threshold by shallow steps.
window('No10 recessed double door','F',2.75,13.12,1.48,.27,2.05,2,3,'Plan205 D2 recessed entrance, leaf dimensions approximate; no invented inscription')
window('Entry side W9','F',2.75,11.85,1.00,.78,1.30,2,3,'Plan205 W9 beside entry; visible portion simplified, not exact window assembly')
for i in range(2):bx('No10 entry step',[12.28,2.15+i*.25,.15],[13.97,2.42+i*.25,.21+i*.06],8,'Plan205 entry levels+16/+27/+29, step runs estimated')
# Rear old dance windows W2/W3 have lower dense panes plus independent upper lights.
for u,w in [(10.60,1.945),(13.56,3.23)]:
 window('Rear original dance sash','B',16.72,u,w,1.20,1.51,5 if w<2 else 8,4,'Plan190 W2/W3 andschedule212 original old sash151cmhigh,323/194.5wide, not proposed W2 prime replacement')
 window('Rear sash upper light','B',16.72,u,w,2.74,.30,5 if w<2 else 8,1,'Schedule212 independent original upper-light row; approximate total integration')
window('Rear original door','B',17.08,8.60,.80,.49,1.95,1,3,'Plan190 D3 near rear toilets; size from coarse doorway estimate')
window('Rear toilet W4','B',17.25,7.20,.80,1.45,.59,3,1,'Schedule212 W4 old upper small sash59x80cm; plane registered to toilet projection')
window('No8 rear service door','B',16.72,1.60,.9,.31,1.96,1,2,'South193 cafe-side service door approximate relative position')
window('No8 rear high sash','B',16.72,4.60,4.2,2.22,.52,5,1,'South193 continuous small upper windows in cafe addition, width estimated not exact measured count')
# No8 exposed side wall, drawn west194 partly behind boundary: lower aperture details not invented.
for y in [2.2,5.2,8.0]:
 window('No8 side high opening','L',0,y,.90,2.10,.42,2,1,'West194 partial high strip apertures visible above boundary; approximate limited relief')
# Blank gray east cap marks attached no12 interface, NOT east end elevation194.
for y0,y1,z in [(2.75,7.49,3.48),(7.49,16.72,3.40)]:
 panel('Research no12 junction cap','E',W,y0,y1,.0,z,.04,5,'Authored cut closure within existing room silhouette ataxes5; adjacent no12 excluded, NOT true east elevation194')
# Coarse boards on available faces; no fire char texture or fine aggregate.
for z in np.arange(.55,2.80,.19):
 panel('Cafe side horizontal board','L',0,0,9.29,float(z),float(z)+.025,.028,1,'Report wood wall fragments/section; coarse horizontal weatherboards')
for x in np.arange(8.05,W,.18):
 for a,b in [([float(x),9.05,3.445],[float(x),13.015,4.805]),([float(x),13.015,4.805],[float(x),16.98,3.445])]:
  add('Rear double-pitch corrugated rib',beam(a,b,.018),6,'Coarse source189/194 A-B double-pitch sheet roof corrugations; not actual asbestos fabrication')
for y in np.arange(.3,6.5,.45):
 z=2.90+(4.95-2.90)*(float(y)+.15)/(6.59+.15)
 end=11.08 if y<2.6 else W-.04
 add('Main sparse tile course',beam([-.2,float(y),z+.012],[end,float(y),z+.012],.018),4,'Sparse tile course relief; individual tile waves omitted')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
# Remove only isolated numerical union slivers smaller than 0.001 mm3; actual removed volumes logged.
chunks=s.decompose();removed_slivers=[q.volume()*SCALE**3 for q in chunks if abs(q.volume())<1];s=mf.Manifold.batch_boolean([q for q in chunks if abs(q.volume())>=1],mf.OpType.Add)

m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Tsai Jui-Yueh Dance Studio no8/10 survey-form study2000');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'removed_numerical_sliver_volumes_mm3':removed_slivers,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'No8/10 axes1–5,2000 survey-form reconstruction including inferred complete roofs, not postfire ruin or restored current condition. Attached no12/garden/perimeter/interiors excluded; authored cut closure.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
