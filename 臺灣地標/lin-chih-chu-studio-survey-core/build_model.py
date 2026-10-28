#!/usr/bin/env python3
"""Lin Chih Chu studio survey-core exterior study; source-supported exterior study."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [('plaster','Neutral study cutoff','#C1C0B8','Authored capped study boundary, not an existing rear wall'),('wood','Survey timber siding','#9C784D','Survey-period timber wall photographs; uncalibrated color'),('frame','Survey timber frames','#815B34','Survey plan and door/window photos, coarse proxy'),('glass','Opaque glass proxy','#7A9597','Opaque proxy, no reconstructed interior'),('roof','Survey tiled roof','#727571','Official survey roof diagrams and photographs; coarse tile rhythm'),('base','Authored support','#B8B3A5','Display support only, not actual site terrain'),('white','Survey rendered details','#D6D3C7','Survey structure details, color approximated'),('dark','Recess backing','#4E493C','Solid-backed recess and grille proxy'),('brick','Survey brick base','#806354','Survey brick foundation photographs; simplified joints')]]
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
 return hull([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0+d,(y0+y1)/2,z1],[x1-d,(y0+y1)/2,z1]])
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
# Approximate traced scale: source third chapter room grid12shaku=3.636m.
K=3.636/144
W=505*K;D=290*K
bx('Authored base',[-3.5,-1.5,-.6],[W+4.8,D+.9,0],5,'Authored display support; not surveyed terrain')
add('Historic west core raised base',box([0,0,0],[W/2,D,.60])-box([0,-.01,.30],[1.82,.28,.66]),8,'Survey west raised floor with depressed entrance step, no modern ramp')
bx('West core walls',[0,0,.60],[W/2,D,3.25],1,'Western survey-period timber walls; inferred height, not modern asbuilt')
bx('East altered residence base',[W/2,0,0],[W,D,.20],0,'Survey east residence has lowered floors after alteration, not copied western raised level')
bx('East altered residence walls',[W/2,0,.20],[W,D,3.25],1,'East residence kept distinct, not mirrored western historic room arrangement; interior omitted')
bx('West service wing base',[-105*K,145*K,0],[.05,D+.88,.27],8,'Original west service wing selected from survey plan, later outer addition omitted')
bx('West service wing walls',[-105*K,145*K,.27],[.05,D+.88,2.65],1,'Survey low west kitchen/bath wing; far north later additions excluded')
bx('Southeast artist studio base',[W,-30*K,0],[W+170*K,145*K,.27],0,'Artist studio southeast projection retained from survey, not deleted as generic annex')
bx('Southeast artist studio walls',[W,-30*K,.27],[W+170*K,145*K,2.85],1,'Survey period artist studio wall envelope; later courtyard additions excluded')
add('Main duplex gable roof',(gable(-.45,W+.45,-.6,D+.6,3.25,5.05)-gable(-.60,W+.60,-.6,D+.6,3.06,4.86)),4,'Survey roof is two-slope; seven roof frames span7.15m rise1.80m; traced walls/overhang differ from structural endpoint')
add('West low service roof',(gable(-105*K-.35,.18,145*K-.35,D+1.2,2.70,3.55)-gable(-105*K-.5,.3,145*K-.35,D+1.2,2.53,3.38)),4,'Survey exploded roof diagram supports lower side gable mass; exact pitch approximated')
add('Artist studio low roof',shed(W-.1,W+170*K+.35,-30*K-.35,145*K+.2,2.9,3.2),4,'Studio appended low roof proxy based on survey massing; concealed junction and pitch approximate')
# Gable timber fields and visible coarse roof courses.
for x,side in [(0,'L'),(W,'R')]:
 add('Main timber gable field',gable(x-.04,x+.04,0,D,3.24,5.03),1,'Survey main gable retains timber face; not a hipped roof')
 window('Gable ventilating panel'if side=='L'else'Gable fixed light',side,x,D/2,1.35,3.6,.72,4,2,'Survey chapter4 gable photos show western louver and other fixed glazing; positions proportioned')
 if side=='L':
  for z in [3.65+i*.11 for i in range(6)]:panel('West gable louver',side,x,D/2-.68,D/2+.68,z,z+.045,.17,2,'Coarse louver blades from survey photo')
for y in [-.6,D+.6]:add('Main eave beam',beam([-.45,y,3.25],[W+.45,y,3.25],.06),2,'Simplified eave/fascia from survey photos')
add('Main ridge',beam([-.45,D/2,5.08],[W+.45,D/2,5.08],.075),4,'Survey main straight ridge, tile finials omitted')
for z in __import__('numpy').arange(3.42,5.03,.18):
 q=(z-3.25)/1.8
 for y in [-.6+(D/2+.6)*q,D+.6-(D/2+.6)*q]:add('Coarse roof tile course',beam([-.42,float(y),float(z)+.02],[W+.42,float(y),float(z)+.01],.04),4,'Coarse roof-course rhythm, individual tile profiles omitted')
# South-facing main entries and different west/east fenestration from survey plan.
# Entrance tread/proxy follows survey depressed entrance rather than modern ramp.
for j in range(3):bx('West entry survey steps',[.02,-.66+j*.22,0],[1.82,.03,.10+j*.10],0,'Survey entrance floor sequence simplified; not later modern ramp')
window('West entrance glazed door','F',0,.91,1.60,.30,2.12,4,4,'Survey west entrance opening at original6shaku bay; sash pattern approximate')
panel('West entrance lower panels','F',0,.11,1.71,.30,.95,.18,1,'Survey door lower timber panels; not modern courtyard door')
panel('West entrance central stile','F',0,.88,.94,.30,2.43,.21,2,'Coarse double-leaf separation')
window('West seated room front window','F',0,3.75,2.72,1.12,1.32,6,3,'Survey western front9shaku opening from room-grid drawing; coarse protective grid from window-type survey, not measured individual bars')
window('West window upper transom','F',0,3.75,2.72,2.52,.28,6,1,'Generic upper light proxy based on survey traditional window family, not exact measured transom')
shutter('West window outer bars','F',0,3.75,2.72,1.12,1.32,19,'Survey timber protective lattice retained as coarse solid-backed bars')
add('West window hood',shed(2.23,5.27,-.42,.06,2.89,3.02),2,'Survey projecting window rain hood')
window('East residence south room window','F',0,8.35,2.4,1.0,1.45,4,4,'East survey plan south bedroom opening; not mirrored western lattice')
window('East residence entrance','F',0,11.75,1.55,.23,2.12,4,4,'East survey entrance at southeast side of original core')
# West side and original service wing windows from survey boundaries.
window('West exposed side window','L',0,1.4,1.6,1.15,1.25,4,3,'Survey western main wall opening; coarse estimate')
window('West service south door','F',145*K,-1.30,1.25,.28,1.95,2,3,'Survey kitchen access; approximate leaf widths')
add('West service timber gable',gable(-105*K-.04,-105*K+.04,145*K,D+.88,2.64,3.52),1,'Survey lower service wing gable silhouette; facade at cropped outer addition interface remains authored cutoff')
# Studio differentiated from timber original core; its north face is an authored cut boundary.
window('Artist studio south glazing','F',-30*K,W+85*K,3.20,.52,2.06,6,4,'Survey plan southeast studio south opening location estimated; generic coarse glazing grid, not verified individual panes')
panel('West service authored cutoff','L',-105*K,145*K,D+.88,.27,2.65,.04,0,'Artificial interface toward excluded western addition, NOT original exterior fenestration')
# North boundary: intentional neutral capped interface, not invented rear facade.
panel('Core north authored cutoff','B',D,0,W,.6,3.25,.04,0,'Neutral capped study interface to omitted northern rooms; NOT a reconstructed existing rear wall')
panel('Studio north authored cutoff','B',145*K,W,W+170*K,.27,2.85,.04,0,'Artificial study boundary toward omitted kitchen and rear additions; no invented openings')
for x in [1.7,4.,7.2,9.5,11.4]:panel('South foundation vent','F',0,x-.18,x+.18,.12,.38,.04,7,'Survey brick foundation vents, approximate spacing and solid-backed')
for z in __import__('numpy').arange(.8,3.2,.20):
 panel('South coarse rainboard joint','F',0,0,W,float(z),float(z)+.015,.025,2,'Survey timber rainboard joints, coarsened not literal assembly')
for z in __import__('numpy').arange(.8,3.2,.20):panel('West coarse rainboard joint','L',0,0,145*K,float(z),float(z)+.015,.025,2,'Survey side weatherboards')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
# Remove only isolated numerical union slivers smaller than 0.000125 mm3.
chunks=s.decompose();removed_slivers=[q.volume()*SCALE**3 for q in chunks if abs(q.volume())<1];s=mf.Manifold.batch_boolean([q for q in chunks if abs(q.volume())>=1],mf.OpType.Add)

m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Lin Chih Chu studio survey-core exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'removed_numerical_sliver_volumes_mm3':removed_slivers,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Survey-period selected duplex core, west service wing and southeast studio only. North additions excluded by authored study boundary, not claimed demolished. No modern ramp, reconstructed former veranda, interior, garden or trialprint.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
