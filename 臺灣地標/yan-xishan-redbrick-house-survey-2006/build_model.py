#!/usr/bin/env python3
"""Original exterior study of Yan Xishan redbrick house, official95-year survey state."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
 ('tar_brick','Blackened survey brick','#493D36','Report3-38/39 black asphalt coating on red bricks; schematic uncalibrated tone, not source-image texture'),
 ('brick','Exposed survey red brick','#78503A','Report3-39/40 exposed red bricks within blackened wall; schematic tonal variation, not mapped damage'),
 ('mortar','Dark joint backing','#6B6558','Illustrative masonry joints, coarse not exact surveyed courses'),
 ('frame','Survey aluminium sash','#ADB4AE','A21/A25 and report3-23/49 existing replacement aluminium sash, not2022 restored timber'),
 ('glass','Opaque glazing proxy','#586862','Opaque closed glazing proxy, no interior or bullet-resistant function'),
 ('wood','Replacement wood door','#784638','Report3-49 replacement single timber entrance leaf and sliding transom; not original double-leaf door'),
 ('roof','Roof waterproof surface','#5B7665','Survey3-39/40 greenish roof waterproofing; uncalibrated and undamaged proxy'),
 ('concrete','Concrete roof edge and guard render','#777568','A25–32 RC slab and3-39 weathered guard-box plaster; simplified intact surface'),
 ('pipe','Ceramic drainage pipes','#555548','Report3-45 exposed ceramic downpipes, segmented silhouette; no moss texture'),
 ('dark','Backed apertures and grilles','#29322D','Dark solid-backed apertures, not functional firing slots or open interior'),
 ('base','Authored flat support','#B0A991','Flat display base; steep terrain and retaining works excluded')]]
SCALE=.10
items=[];ops=[];ids={}
def box(a,b):
 a=np.round(np.array(a)*100);b=np.round(np.array(b)*100);return mf.Manifold.cube((b-a).tolist()).translate(a.tolist())
def add(name,s,mat,evidence):
 s=s.translate([0,0,50]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat,evidence):add(name,box(a,b),mat,evidence)
def bx_halfcm_x(name,a,b,mat,evidence):
 aa=np.round(np.array(a)*100);bb=np.round(np.array(b)*100);aa[0]=round(a[0]*100,1);bb[0]=round(b[0]*100,1)
 add(name,mf.Manifold.cube((bb-aa).tolist()).translate(aa.tolist()),mat,evidence)
def panel(name,side,plane,u0,u1,z0,z1,depth,mat,ev):
 if side in ('F','B'):
  a,b=(plane-depth,plane+.025)if side=='F'else(plane-.025,plane+depth);bx(name,[u0,a,z0],[u1,b,z1],mat,ev)
 else:
  a,b=(plane-depth,plane+.025)if side=='L'else(plane-.025,plane+depth);bx(name,[a,u0,z0],[b,u1,z1],mat,ev)
def window(name,side,plane,u,w,z,h,cols,rows,ev,transom=.25):
 panel(name+' frame',side,plane,u-w/2-.045,u+w/2+.045,z-.045,z+h+.045,.055,3,ev)
 panel(name+' opaque glazing',side,plane,u-w/2,u+w/2,z,z+h,.075,4,'Opaque glazing proxy; no interior modeled')
 top=z+h-transom
 for i in range(cols+1):
  q=u-w/2+i*w/cols;panel(name+' lower stile',side,plane,q-.015,q+.015,z,top,.105,3,ev)
 for j in range(rows+1):
  q=z+(top-z)*j/rows;panel(name+' lower rail',side,plane,u-w/2,u+w/2,q-.015,q+.015,.115,3,ev)
 for i in range(3):
  q=u-w/2+i*w/2;panel(name+' transom stile',side,plane,q-.015,q+.015,top,z+h,.105,3,ev)
 for q in [top,z+h]:panel(name+' transom rail',side,plane,u-w/2,u+w/2,q-.018,q+.018,.115,3,ev)
 # Rectangular brick header with coarse vertical joints; original fan-like splay is not modeled.
 panel(name+' brick header',side,plane,u-w/2-.10,u+w/2+.10,z+h+.07,z+h+.24,.055,1,'A25 brick heads above front openings; coarse soldier-joint proxy, not each brick traced')
 for q in np.arange(u-w/2-.06,u+w/2+.08,.11):panel(name+' header joint',side,plane,float(q)-.008,float(q)+.008,z+h+.075,z+h+.235,.08,2,'Coarse header joint rhythm')
def brickface(name,side,plane,u0,u1,z0,z1,tar=True):
 # Coarsened English-bond rhythm:40cm stretchers and20cm headers in alternating courses; schematic colors.
 h=.10
 for row,z in enumerate(np.arange(z0,z1,h)):
  x=u0;j=0
  while x<u1-.02:
   w=.40 if row%2==0 else (.10 if j==0 else .20);end=min(u1,x+w)
   if end-x>.03:
    mat=(0 if (row*7+j*11)%9<6 else 1)if tar else 1
    panel(name+' coarse brick',side,plane,x+.007,end-.007,float(z)+.008,min(float(z)+h-.008,z1-.002),.025,mat,'A25–28 brick walls; report2-59/60 English bond, coarse alternating stretcher/header courses;3-38/39 black coating. Simplified corner closures and deterministic color variation, not actual damage map')
   x=end;j+=1
W=6.86;D=3.34
EV='Official95-year survey plates A20–32, not2022 restored state; approximate scan registration for secondary details'
bx('Authored flat support',[-.65,-.75,-.50],[W+.65,D+.65,0],10,'Flat display base, not hillside retaining walls or courtyard; no invented upper access stair')
bx('Two-storey solid exterior core',[0,0,0],[W,D,4.77],2,'A21/A25 W686cm D334cm; A25 floor267cm and roof492cm. Solid exterior, internal rooms201–204 and thick-wall construction not reproduced')
for side,pl,u1 in [('F',0,W),('B',D,W),('L',0,D),('R',W,D)]:brickface('Main wall',side,pl,0,u1,0,4.77)
bx_halfcm_x('RC roof overhang',[-.385,-.40,4.77],[W+.385,D+.40,4.92],7,'A22 roof outer763x414cm; longitudinal40+686+40=766 differs3cm from overall763. Model adopts763 overall and symmetric38.5cm end overhang; A25 slab15cm')
bx_halfcm_x('Roof waterproof top',[-.385,-.40,4.915],[W+.385,D+.40,4.93],6,'Survey3-39/40 green waterproofing visible at roof edge; simplified flat intact proxy')
# Complete low parapet plus rear-left rooftop guard box, distinct from redbrick main body.
for name,a,b in [('Front',[0,0,4.92],[W,.12,5.50]),('Rear',[0,D-.12,4.92],[W,D,5.50]),('NW',[0,0,4.92],[.12,D,5.50]),('SE',[W-.12,0,4.92],[W,D,5.50])]:bx('Roof parapet '+name,a,b,2,'A22/A25–32 perimeter parapet58cm above roof492cm, total550cm; small openings are backed proxies')
for side,pl,u1 in [('F',0,W),('B',D,W),('L',0,D),('R',W,D)]:brickface('Roof parapet',side,pl,0,u1,4.92,5.50,False)
for a,b in [([0,-.025,5.48],[W,.145,5.53]),([0,D-.145,5.48],[W,D+.025,5.53]),([-.025,0,5.48],[.145,D,5.53]),([W-.145,0,5.48],[W+.025,D,5.53])]:bx('Parapet thin coping',a,b,7,'Report3-40 visible thin concrete coping; thickness approximated, envelope exceeds550cm parapet brick datum by3cm')
bx('Rooftop guard-box solid envelope',[0,D-1.26,4.92],[1.31,D,6.00],7,'A22 guard box131x126cm, A25/A29 top612cm; plastered brick exterior, solid interior proxy')
bx('Guard-box flat cap',[0,D-1.26,6.00],[1.31,D,6.12],7,'A25/A29 guard-box total120cm above roof492cm; top slab12cm approximate')
panel('Guard-box front aperture','F',D-1.26,.465,.845,4.94,5.95,.04,9,'A22 roof-inward38cm entrance and report3-39 guard box photo; A25 hides lower portion behind front parapet. Low door-like backed proxy from roof level; height estimated')
panel('Guard-box rear paired aperture','B',D,.465,.845,5.65,5.85,.04,9,'A26 small paired rear slit, dimensions scan estimated, solid-backed')
panel('Guard-box rear aperture divider','B',D,.64,.67,5.65,5.85,.06,7,'A26 visible small aperture division')
panel('Guard-box NW paired aperture','L',0,D-.85,D-.47,5.64,5.84,.04,9,'A27 small guard-box side slit, dimensions scan estimated, solid-backed')
panel('Guard-box NW aperture divider','L',0,D-.675,D-.645,5.64,5.84,.06,7,'A27 small aperture division')
for x in [2.25,3.60,5.35]:panel('Rear parapet historic small opening','B',D,x-.045,x+.045,5.18,5.27,.045,9,'A22/A30 and report3-40 small rear parapet openings; locations approximately registered, nonfunctional backed model detail')
# Four upper SW sash; second has undivided lower pane observed in photo3-6-26 and A25.
for i,(c,w,cols) in enumerate([(1.19,.80,2),(2.505,.79,1),(4.39,.80,2),(5.725,.81,2)]):window('Upper SW sash'+str(i+1),'F',0,c,w,3.27,1.25,cols,1,'A21 chained widths79/80/52/79/109/80/53/81/73cm; A25 sill60cm above267cm floor and height125cm; survey3-39 aluminium sashes')
window('Lower right SW sash','F',0,5.87,.88,.84,1.33,2,3,'A20/A25 lower right window, report3-39 survey frame; opening position minor registration estimate')
# Lower grille openings, no through-wall defense geometry.
for side,pl,c,w,z,h in [('F',0,1.92,.70,1.30,.50),('L',0,1.80,.68,1.31,.61)]:
 panel('Lower protective grille dark backing',side,pl,c-w/2,c+w/2,z,z+h,.04,9,'A20/A25/A27 and report3-49 small grille openings; closed-backed illustration, no functional performance')
 for q in np.linspace(c-w/2,c+w/2,6):panel('Lower grille broad slat',side,pl,float(q)-.022,float(q)+.022,z,z+h,.085,3,'Report3-49 metal grille; approximate count and strengthened thickness')
 panel('Lower grille brick header',side,pl,c-w/2-.06,c+w/2+.06,z+h+.01,z+h+.14,.04,1,'A25/A27 small opening brick header, coarse proxy')
# Survey single replacement entrance leaf, not original historic double door.
u=4.375;w=.95
panel('SW single timber entrance frame','F',0,u-w/2-.055,u+w/2+.055,.015,2.22,.055,5,'A20 woodD2 and report3-49 single replacement timber leaf; upper transom modified to sliding type')
panel('SW entrance single closed leaf','F',0,u-w/2,u+w/2,.03,1.85,.075,5,'Report3-49 replacement single timber leaf shown closed; no original two-leaf reconstruction')
panel('SW entrance broad timber panel','F',0,u-w/2+.075,u+w/2-.075,.56,1.75,.095,5,'A25 broad upper door panel and report3-49 single timber replacement leaf. Photo is partly open and does not prove glazed leaf; closed timber panel proxy')
for z in [.52,1.78]:panel('SW door horizontal wood rail','F',0,u-w/2,u+w/2,z-.025,z+.025,.125,5,'Photo3-8-8 single timber leaf simplified rails')
panel('SW two-light transom glazing','F',0,u-w/2,u+w/2,1.89,2.15,.075,4,'Report3-49 replacement sliding two-light transom')
for x in [u-w/2,u,u+w/2]:panel('SW transom wood stile','F',0,x-.02,x+.02,1.86,2.19,.105,5,'Report3-49 sliding transom proxy')
for z in [1.86,2.18]:panel('SW transom wood rail','F',0,u-w/2,u+w/2,z-.02,z+.02,.105,5,'Report3-49 replacement transom frame')
panel('SW door brick header','F',0,u-w/2-.07,u+w/2+.07,2.23,2.40,.04,1,'A25 brick header above main entry, coarse proxy')
for x in np.linspace(u-w/2+.09,u+w/2-.09,6):panel('SW door lower coarse vertical detail','F',0,float(x)-.018,float(x)+.018,.055,.46,.125,5,'A25 lower vertical door detail; coarse count/thickness approximation, not exact replacement-leaf carpentry')
# Existing upper SE wooden door opens toward unmodeled terrain; no future proposed bridge/stair.
panel('SE upper wood door frame','R',W,1.245,2.095,2.67,4.77,.055,5,'A21 southeast木W8 label with door swing absent; A28/A32 and report3-23 upper access door, no access stair at survey date')
panel('SE upper timber door panel','R',W,1.29,2.05,2.72,4.42,.075,5,'A28 vertical-board door proxy, secondary subdivisions estimated')
for u in np.arange(1.31,2.04,.12):panel('SE door vertical plank joint','R',W,float(u),float(u)+.012,2.73,4.42,.105,9,'A28 vertical board rhythm coarse, not exact carpentry')
panel('SE upper-door transom','R',W,1.29,2.05,4.46,4.70,.075,4,'A28/A32 upper door transom, opaque simplified proxy')
panel('SE door transom divider','R',W,1.65,1.68,4.44,4.72,.10,5,'A28 paired transom division')
# Three front exposed ceramic downpipes. Right upper section absent per3-23/45 survey damage.
for x,top in [(.10,4.78),(3.52,4.78),(6.75,2.38)]:
 add('Exposed ceramic drainpipe',mf.Manifold.cylinder(top*100,6.5,6.5,20).translate([x*100,-3,0]),8,'A22/A25 front drainpipe alignment; report3-23/45 ceramic pipes, right upper segment broken; segment lengths approximate')
 for z in np.arange(.4,top,.48):add('Ceramic pipe socket collar',mf.Manifold.cylinder(5,8.0,8.0,20).translate([x*100,-3,float(z)*100]),8,'Report3-45 segmented ceramic pipe collars, coarse interval')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
# Remove only isolated numerical union slivers smaller than 0.001 mm3; actual removed volumes logged.
chunks=s.decompose();removed_slivers=[q.volume()*SCALE**3 for q in chunks if abs(q.volume())<1];s=mf.Manifold.batch_boolean([q for q in chunks if abs(q.volume())>=1],mf.OpType.Add)

m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Yan Xishan redbrick house survey-period exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'removed_numerical_sliver_volumes_mm3':removed_slivers,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Yan Xishan redbrick house with roof parapet and guard box; official95-year survey-period exterior, not2022 restoration. Stone house, attached low kitchen, terrain, exterior access stairs and interiors excluded.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
