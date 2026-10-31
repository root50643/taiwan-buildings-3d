#!/usr/bin/env python3
"""TKU Shaomo memorial swimming hall N: bounded front facade from undated official photos. Not whole building."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
 ('wall','Warm white piers','#DEDCD0','Official exterior photos; uncalibrated'),
 ('metal','Silver gray cladding','#AEB7B8','Visible upper fascia and central curved crown'),
 ('glass','Turquoise glazing abstraction','#4D9C99','Opaque color block; no reflection or transparency claim'),
 ('recess','Blue gray entrance glazing','#4E676F','Darker recessed entrance glazing'),
 ('frame','Pale gray metal frames','#B7C4BD','Visible metal surrounds; repeated spacing regularized'),
 ('base','Authored neutral display base','#A5A69C','Display support not real site footprint'),
 ('cut','Authored rear cut face','#B6BAC0','Neutral cutoff plane, not building rear')]]
SCALE=6.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.6]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Photo-proportioned visible feature; nominal dimensions'):add(name,box(a,b),mat,evidence)
def poly(name,pts,z0,z1,mat,evidence):
 if sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))<0:pts=list(reversed(pts))
 add(name,mf.CrossSection([pts]).extrude(z1-z0).translate([0,0,z0]),mat,evidence)
# Nominal 24-unit width. All dimensions photo-proportioned, not surveyed.
bx('Authored support base',[-.5,-2.4,-.6],[24.5,2.65,0],5,'Display support only, not site footprint')
bx('Retained neutral facade backing',[0,.78,0],[24,2.45,7.75],6,'Authored shallow closure, not actual building interior or rear')
bx('Neutral rear section face',[0,2.43,0],[24,2.5,7.75],6,'Flat modeled cutoff plane; roof and rear building excluded')
# Full-height broad outer piers and narrow turquoise end strips.
for x0,x1 in [(0,.55),(23.45,24)]:
 bx('Narrow outer glass strip',[x0,-.02,.2],[x1,.85,6.8],2,'Visible narrow glazed strips beyond the broad end piers')
 for j in range(1,11):bx('Regularized end-strip transom',[x0,-.06,.2+j*.6],[x1,.03,.245+j*.6],4,'Coarse repetitive frame pattern, not surveyed count')
for x0,x1 in [(.55,2.65),(21.35,23.45)]:bx('Broad white end pier',[x0,-.1,0],[x1,.9,8.25],0,'Broad pale end supports visible in frontal photograph')
# Four folding glass bays per side; opaque faceted blocks, not hollow glazed rooms.
for side,xstart in [('Left',2.65),('Right',15.85)]:
 width=5.5;step=width/4
 for j in range(4):
  x=xstart+j*step;ridge=x+step*.5
  pts=[(x,.35),(ridge,-.46),(x+step,.35),(x+step,1.05),(x,1.05)]
  poly(side+' folded glass bay '+str(j+1),pts,.15,6.85,2,'Four principal front glass folds per side read from main photo; precise depth inferred')
  # Face frame rails follow the two fold planes.
  for k,(u,w) in enumerate([((x,.35),(ridge,-.46)),((ridge,-.46),(x+step,.35))]):
   dx=w[0]-u[0];dy=w[1]-u[1];ln=math.hypot(dx,dy);nx=-dy/ln*.025;ny=dx/ln*.025
   strip=[(u[0]+nx,u[1]+ny),(w[0]+nx,w[1]+ny),(w[0]-nx,w[1]-ny),(u[0]-nx,u[1]-ny)]
   for h in range(1,13):poly(side+' simplified transom',strip,.15+h*.51,.195+h*.51,4,'12 evenly spaced model transoms; source grid simplified, exact count not asserted')
  for u,w in [(x,.35),(ridge,-.46),(x+step,.35)]:bx(side+' vertical fold mullion',[u-.028,w-.03,.15],[u+.028,w+.05,6.87],4,'Visible vertical joints at folded glazing edges')
# Recessed central entrance and two tall cylindrical columns.
bx('Central entrance opaque glazing',[8.13,.68,.15],[15.87,.86,6.85],3,'Continuous recessed blue-gray glazed front, no interior reconstruction')
for i in range(7):
 x=8.2+i*1.27;bx('Regularized entrance mullion',[x-.035,.60,.15],[x+.035,.84,6.85],4,'Simplified central vertical grid; spacing approximate')
for i in range(1,13):
 z=.15+i*.51;bx('Regularized entrance transom',[8.13,.59,z],[15.87,.83,z+.045],4,'Simplified repetitive entrance grid, not exact framing count')
for x in [10.65,13.35]:
 add('Tall round entrance column',mf.Manifold.cylinder(6.75,.16,.16,48).translate([x,-.35,.12]),1,'Two cylindrical columns directly visible; diameters and depth photo-proportioned')
# Door group remains a coarse 4-panel abstraction, not precise door joinery.
bx('Door group surround',[10.9,.54,.12],[13.1,.81,1.45],4,'Entrance door group visible below center glazing')
for i in range(4):
 x=10.98+i*.52;bx('Door opaque panel',[x,.50,.19],[x+.44,.60,1.35],3,'Four simplified door panels; exact leaf arrangement not asserted')
# Straight side fascia with distinct higher central crown curved in PLAN.
for x0,x1 in [(0,8.18),(15.82,24)]:bx('Straight silver fascia',[x0,-.6,6.8],[x1,1.2,8.25],1,'Silver upper horizontal fascia flanking central crown')
def curve(n=48):return [(8.15+7.7*i/n,-.62-.72*math.sin(math.pi*i/n)) for i in range(n+1)]
poly('Forward-curved central silver crown',curve()+[(15.85,1.25),(8.15,1.25)],6.8,9.15,1,'Central crown top is level; convex front edge approximated in plan, not an elevation arch')
# Panel joints: coarse thin color strips, no copied gold signage.
for i in range(25):
 x=i;zmax=8.25
 if 8.15<x<15.85:
  y=-.62-.72*math.sin(math.pi*(x-8.15)/7.7);zmax=9.15
 else:y=-.6
 bx('Regularized fascia vertical panel joint',[x-.016,y-.018,6.81],[x+.016,y+.04,zmax-.03],4,'Authored regularized panel seams; exact panel count unverified')
# Simple approach steps; landscape fence and site paving explicitly omitted.
for j in range(3):
 bx('Simplified entrance step '+str(j+1),[8.25,-2.1+j*.45,0],[15.75,.9,.08+j*.08],0,'Three coarse approach levels represent visible steps; count and risers not surveyed')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
v, inv=np.unique(v,axis=0,return_inverse=True);f=inv[f]
area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)*.5
keep=area>1e-9;f=f[keep];mi=mi[keep]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='TKU Shaomo memorial swimming hall bounded front facade');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Undated official-photo source-state front facade only; not a 2026 as-built record. Rear, whole roof and interiors excluded. Nominal dimensions, glazing and panel grid regularized; no trial print.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
