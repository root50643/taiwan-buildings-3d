#!/usr/bin/env python3
"""Zhongneng stone house: official95-year report survey-period simplified exterior, not2022 restoration."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
 ('stone','Survey local stone masonry','#8A8A76','Report3-32 stone交丁砌 and survey elevations A14–17; illustrative uncalibrated color'),
 ('wood','Survey boarded sash','#776A52','Report3-22 text says all rear windows boarded;3-34 photo corroborates against falling rock; boards proxy'),
 ('frame','Survey metal sash','#B3B7A6','Report3-32/34 existing replacement metal sash, not original restored wood'),
 ('glass','Opaque glazing','#5C706B','Opaque glass proxy; no transparent interiors'),
 ('roof','Survey green concrete roof','#668B75','Report3-42 photograph green painted RC roof and inner low parapets; schematic uncalibrated color'),
 ('base','Authored display base','#B3B0A1','Flat support not actual hillside, retaining walls or measured terrain'),
 ('metal','Old canopy sheet','#929C91','Report3-32/42 photo old sheet canopy; not2022 bamboo canopy'),
 ('dark','Dark aperture backing','#303A34','Solid-backed recess proxy, not open void'),
 ('brick','Low brick annex and porch columns','#967563','A14 low side service annex and porch supports; brick joint relief coarse'),
 ('mortar','Masonry joint backing','#B2B2A0','Coarse representative masonry joints, not each original stone surveyed')]]
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

# x along southwest front from NW to SE; y towards northeast rear.
EV='Official95-year report A11–19 measured survey plates; approximate registration across differing control endpoints, not2022 condition'
W=18.42;D=10.25
bx('Flat display support',[-.65,-.65,-.6],[22.32,11.73,0],5,'Authored flat base; stepped natural hillside and compound retaining walls excluded')
bx('Main stone core',[0,2.25,0],[W,D,3.80],9,EV+'; exterior solid study, rooms not modeled')
bx('Central projecting entrance volume',[7.30,0,0],[10.70,2.29,4.04],9,EV+'; side arched entries, front paired windows')
bx('Rear central toilet projection',[7.30,D-.03,0],[10.70,D+.83,3.80],9,EV+'; rear projection83cm control')
bx('Right low service annex',[W,2.25,0],[21.67,D,3.40],8,EV+'; low rooms106/107 retained, upper redbrick building excluded')
# 15 coarse courses on the body; openings overlaid with solid-backed glazing/boards.
def stoneface(name,side,p,u0,u1,z0,z1):
 h=(z1-z0)/15
 for row in range(15):
  z=z0+row*h+.018; x=u0; j=0
  while x<u1-.03:
   wid=.78 if row%2==0 else (.39 if j%3==0 else .78)
   if row%2 and j==0:wid=.38
   end=min(u1,x+wid)
   if end-x>.035:panel(name+' coarse stone',side,p,x+.012,end-.012,z,z+h-.035,.045,0,'Report3-32交丁 stone courses, A14–17; coarse alternating block joints, not individual stone tracing')
   x=end;j+=1
for side,p,a,b,hi in [('F',2.25,0,7.3,3.8),('F',2.25,10.7,W,3.8),('F',0,7.3,10.7,4.04),('B',D,0,7.3,3.8),('B',D,10.7,W,3.8),('B',D+.83,7.3,10.7,3.8),('L',0,2.25,D,3.8),('R',W,2.25,D,3.8),('L',7.3,0,2.25,4.04),('R',10.7,0,2.25,4.04)]:stoneface('Stone wall',side,p,a,b,0,hi)
# RC roof slab thickness .24m report3-42. Height uses front datum A14 approximately.
bx('Main RC roof slab',[-.25,1.90,3.80],[W+.25,D+.35,4.04],4,'Report3-42 slab24cm; A12/A14 plan slab/eave, datum reconciliation approximate')
bx('Rear projection roof',[7.05,D-.05,3.80],[10.95,D+1.08,4.04],4,EV)
bx('Central entrance roof',[7.05,-.25,4.04],[10.95,2.30,4.28],4,'A12/A14 central projecting roof ledge; levels estimated from scan')
bx('Annex flat low roof',[W-.02,2.05,3.40],[21.92,D+.25,3.64],4,'A14 low service roof, schematic height against front ground datum')
# Two U-shaped low inner roof walls interrupted at side midpoints, A12.
for a,b in [([3.8,2.90,4.03],[14.3,3.20,4.59]),([3.8,9.30,4.03],[14.3,9.60,4.59]),([3.8,2.90,4.03],[4.1,5.80,4.59]),([3.8,6.70,4.03],[4.1,9.60,4.59]),([14.,2.90,4.03],[14.3,5.80,4.59]),([14.,6.70,4.03],[14.3,9.60,4.59])]:bx('Interrupted low inner roof parapet',a,b,4,'A12 1050cm width, longitudinal100+290+90+290+100cm chain gives670cm parapet depth and90cm side gaps; A19 55cm height; photo3-7-1 green low walls')
# Entrance parapet with round openings represented as closed dark recesses.
bx('Entrance high perforated parapet',[7.30,-.02,4.27],[10.70,.24,4.75],4,'A14 highest475cm front datum; row round parapet openings, solid-backed print approximation')
for x in np.linspace(7.56,10.44,9):
 add('Parapet round recess',mf.Manifold.cylinder(8,9,9,24).rotate([90,0,0]).translate([x*100,-1,451]),7,'A14 nine circular parapet apertures, backed circular recess proxy')
# Side returns confirmed in A12 and six round apertures in each A16/A17 side view.
for side,x0,x1 in [('NW',7.30,7.54),('SE',10.46,10.70)]:
 bx('Entrance perforated parapet '+side+' return',[x0,.20,4.27],[x1,2.25,4.75],4,'A12 U-shaped entry parapet; A16/A17 six apertures along each return; closed-backed aperture proxy, secondary dimensions estimated')
 for y in np.linspace(.42,2.05,6):
  ang=-90 if side=='NW' else 90; xx=731 if side=='NW' else 1069
  add('Entrance parapet '+side+' circular aperture proxy',mf.Manifold.cylinder(8,9,9,24).rotate([0,ang,0]).translate([xx,y*100,451]),7,'A16/A17 six side circular openings; dark backed proxy not through holes')
# Front porch floor, brick supports and old sheet lean-to roof.
for x0,x1 in [(0,7.30),(10.70,W)]:
 bx('Raised porch floor',[x0,0,0],[x1,2.30,.80],0,'A14 front floor80cm; underside solid support, terrain simplified')
 for x in [x0+.14,(x0+x1)/2,x1-.14]:
  bx('Brick porch column',[x-.11,-.05,.78],[x+.11,.18,3.07],8,'A11/A14 survey porch support positions approximate')
  for z in np.arange(.92,3.0,.22):bx('Column mortar course',[x-.115,-.061,float(z)],[x+.115,.19,float(z)+.025],9,'Coarse brick course relief')
 add('Survey sheet canopy',shed(x0-.07,x1+.07,-.12,2.30,3.08,3.48),6,'A14/A19 and report3-32 old lean-to sheet canopy; intact simplified proxy omits local damage/sag')
 for x in np.arange(x0+.05,x1,.18):add('Canopy coarse corrugation',beam([float(x),-.10,3.092],[float(x),2.28,3.492],.018),6,'Sparse coarse sheet ribs, not bamboo of2022 photographs')
 bx('Canopy front fascia',[x0-.07,-.16,2.92],[x1+.07,-.08,3.09],6,'A14 vertical sheet fascia; approximate depth')
# Paired narrow windows and upper vents; component placement from plan A11/elevations A14/A15.
centers=[2.0,5.60,9.0,12.65,16.25]
for k,c in enumerate(centers):
 front=0 if k==2 else 2.25
 for dx in [-.60,.60]:
  window('Front narrow metal sash','F',front,c+dx,.65,1.09,1.60,1,2,'A11 paired65cm openings and A14 160cm height; report3-32 existing metal replacement sash')
  back=D+.83 if k==2 else D
  # Show original survey opening grid rather than universal contemporary glass; old boarded condition explicit.
  panel('Rear temporary boarded window','B',back,c+dx-.325,c+dx+.325,1.25,2.65,.09,1,'Report3-22 states all rear openings temporarily boarded against rockfall;3-34 photo corroborates; placement followsA15, panel simplification not restored sash')
  for z in [1.25,1.95,2.65]:panel('Rear board crosspiece','B',back,c+dx-.34,c+dx+.34,z-.035,z+.035,.14,1,'Coarse boarding crosspiece estimated from survey photo')
 if k!=2:
  for dx in [-.60,.60]:window('Front high small paired vents','F',2.25,c+dx,.75,3.56,.27,2,1,'A14 high small paired openings above canopy; size/position scan estimate')
 for dx in [-.60,.60]:window('Rear high small paired vents','B',D+.83 if k==2 else D,c+dx,.75,3.56,.27,2,1,'A15 high paired vents; estimated registration')
# Central front circular sash and sill herringbone relief.
add('Circular front stone surround',mf.Manifold.cylinder(12,43,43,48).rotate([90,0,0]).translate([900,1,342]),0,'A14/report3-34 central round window stone ring; radius estimated')
add('Circular opaque front glass',mf.Manifold.cylinder(9,32,32,48).rotate([90,0,0]).translate([900,-10,342]),3,'Survey photo3-6-5 round metal framed glazing, opaque proxy')
for x in np.arange(7.48,10.6,.35):
 add('Front herringbone masonry relief',beam([float(x),-.065,.43],[float(x)+.18,-.065,.67],.035),0,'Report3-32 photo3-6-3 entrance base人字砌, coarse relief not individual stones')
 add('Front herringbone masonry relief',beam([float(x)+.18,-.065,.67],[float(x)+.35,-.065,.43],.035),0,'Report3-32 coarse herringbone base pattern')
# Side arched door fronts on entrance projection; inlay on side faces avoids front-door invention.
for side,p,rot in [('L',7.3,90),('R',10.7,-90)]:
 door=arch(1.2,.80,2.42,.60).scale([1,.1,1]).rotate([0,0,rot]).translate([p*100,125,0])
 add('Entrance side arched metal door',door,2,'A11 side doors and A19 arched fanlight, report3-26 aluminium-door caption and3-32 photo; solid-backed side door rather than invented front door')
 panel('Entry side dark rectangular glazing',side,p,.76,1.74,1.15,2.40,.12,3,'Coarse door glass below arch; no interior transparency')
 for u in [.76,1.25,1.74]:panel('Entry side door stile',side,p,u-.025,u+.025,.82,2.45,.15,2,'A19 two door leaves, coarse metal stiles')
 for z in [1.15,1.85,2.42]:panel('Entry side door rail',side,p,.76,1.74,z-.025,z+.025,.15,2,'A19 door rails approximate')

 for theta in [0,math.pi/4,math.pi/2,3*math.pi/4,math.pi]:
  xx=p+(-.17 if side=='L' else .17)
  add('Arched fanlight radial bar',beam([xx,1.25,2.42],[xx,1.25+.54*math.cos(theta),2.42+.54*math.sin(theta)],.022),2,'A19 arched fanlight radial divisions, coarse proxy')
 # Landing to porch connects side entry.
 bx('Entrance side landing',[p-.65,.65,.76],[p+.65,1.95,.82],0,'A11 front side doorway threshold, coarse level connection')
# Annex front/rear door/window and small roof vent, survey A14/A15.
window('Annex front window','F',2.25,20.25,1.15,1.05,.88,2,1,'A14 annex front window, scan-derived placement')
window('Annex front door','F',2.25,18.90,.70,.15,1.85,1,2,'A14 right low service door, approximate')
window('Annex rear door','B',D,19.20,.70,.55,1.65,1,2,'A15 low annex rear door, approximate datum')
window('Annex rear upper vent','B',D,19.20,.85,2.65,.30,2,1,'A15 low annex high window')
bx('Annex roof vent curb',[19.75,2.95,3.60],[20.35,3.55,3.85],4,'A12/A14 low annex roof vent curb near front eave; position and size registered approximately from scan')
bx('Annex roof vent cap',[19.65,2.85,3.84],[20.45,3.65,3.94],4,'A14 small roof vent cap silhouette')
# Two front access breaks in porch plinth, simplified steps at plan gaps.
for x in [5.65,12.55]:
 for i in range(4):bx('Front porch approach step',[x-.45,-.75+i*.18,0],[x+.45,-.55+i*.18,.20*(i+1)],0,'A11 porch approach opening approximate steps; site topography not surveyed in model')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
# Remove only isolated numerical union slivers smaller than 0.001 mm3; actual removed volumes logged.
chunks=s.decompose();removed_slivers=[q.volume()*SCALE**3 for q in chunks if abs(q.volume())<1];s=mf.Manifold.batch_boolean([q for q in chunks if abs(q.volume())>=1],mf.OpType.Add)

m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Zhongneng stone house survey-period exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'removed_numerical_sliver_volumes_mm3':removed_slivers,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Zhongneng stone house and low service annex; official95-year survey-period exterior study, not2022 restored condition. Redbrick house, hillside, interiors excluded; flat display terrain.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
