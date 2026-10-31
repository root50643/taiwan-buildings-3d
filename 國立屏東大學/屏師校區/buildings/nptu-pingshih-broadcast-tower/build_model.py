#!/usr/bin/env python3
"""NPTU Pingshih broadcast memorial tower; photo-normalized complete main form."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e} for i,n,c,e in [
('ivory','Aged pale tower finish','#DDDCCB','Official two public photos, uncalibrated approximate ivory'),
('green','Green recessed shaft panels','#547D65','Visible green panels and plinth bands'),
('dark','Speaker recess','#202724','Observed dark circular speaker mouths; simplified closed recess'),
('trim','Outline and base shadows','#929B86','Observed box trim and base bands, nominal simplification'),
('badge','Plain surrogate crest roundel','#9BB7A8','Original papaya-leaf crest intentionally omitted; not an actual blank emblem')]]
SCALE=1.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Visible main-form feature; photo-normalized not surveyed'):add(name,box(a,b),mat,evidence)
def cyl_y(radius,depth,center):return mf.Manifold.cylinder(depth,radius,radius,64,True).rotate([90,0,0]).translate(center)
# Layered existing plinth; no guessed landscaped plot or separate site base.
for name,w,z0,z1,mat in [('bottom block',34,0,4.5,0),('lower green band',33.2,4.4,5.9,1),('middle white step',34,5.8,8,0),('upper green band',32.5,7.9,9.8,1),('upper slab',34,9.7,13.2,0)]:
 bx(name,[-w/2,-w/2,z0],[w/2,w/2,z1],mat)
bx('Green central shaft',[-7,-7,13],[7,7,107],1)
# Four flared corner ribs. Curvature reduced to several clearly declared straight segments.
profile=[(4.6,13),(16,13),(13.8,14.1),(11.5,15.7),(9.6,18.5),(8.3,22.5),(7.8,29),(7.8,107),(4.6,107)]
# Polygon lies in x,z; extrude then rotate so depth becomes y.
for sx in [-1,1]:
 for sy in [-1,1]:
  # Corner fin as intersecting face ribs, joined to green core.
  shape=mf.CrossSection([profile]).extrude(2.4).rotate([90,0,0]).translate([0,7,0])
  if sx<0:shape=shape.mirror([1,0,0])
  if sy<0:shape=shape.mirror([0,1,0])
  add(f'Corner rib {sx} {sy} x-facing',shape,0,'White corner pilaster flare, segmented photo-normalized curve')
  add(f'Corner rib {sx} {sy} y-facing',shape.rotate([0,0,90*sx*sy]),0,'White corner pilaster flare, segmented photo-normalized curve')
bx('Small neck under speaker head',[-9,-9,104.8],[9,9,108],0)
# Only the two faces actually visible in reference have mouths. Unseen back/left are neutral closures.
head=box([-13,-13,107],[13,13,126])
front=cyl_y(7,5,(0,-12,116.5))
right=mf.Manifold.cylinder(5,7,7,64,True).rotate([0,90,0]).translate([12,0,116.5])
head=head-front-right
add('Speaker box, two observed apertures only',head,0,'Front and right mouths from double-face official photo; unseen faces closed neutral, not claimed actual')
add('Front dark speaker recess',cyl_y(6.9,1.1,(0,-9.4,116.5)),2,'Shallow closed dark recess, no interior equipment reconstruction')
add('Right dark speaker recess',mf.Manifold.cylinder(1.1,6.9,6.9,64,True).rotate([0,90,0]).translate([9.4,0,116.5]),2,'Shallow closed dark recess, no interior equipment reconstruction')
# Thin rectangular trim strokes on the two observed speaker faces.
for z in [108.2,124.8]:
 bx('Front trim horizontal',[-11.8,-13.18,z-.17],[11.8,-12.8,z+.17],3)
 bx('Right trim horizontal',[12.8,-11.8,z-.17],[13.18,11.8,z+.17],3)
for x in [-11.8,11.8]:bx('Front trim vertical',[x-.17,-13.18,108.2],[x+.17,-12.8,124.8],3)
for y in [-11.8,11.8]:bx('Right trim vertical',[12.8,y-.17,108.2],[13.18,y+.17,124.8],3)
# Top emblem board silhouette: flattened approximation, crest artwork is NOT reproduced.
bx('Emblem neck',[-10,-2.2,125.5],[10,2.2,133],0,'Nominal connecting neck; emblem thickness not measurable in sources')
add('Rounded emblem board',cyl_y(10,4.4,(0,0,134)),0,'Rounded top plaque silhouette simplified; rear plain because unseen')
add('Plain surrogate emblem disk',cyl_y(7.8,.5,(0,-2.3,134)),4,'Papaya-leaf original artwork omitted; plain color placeholder is declared nonliteral')
# Base inscription slab seen on the right, without illegible miniature lettering.
bx('Side inscription slab',[16.8,-7,1],[17.6,-3,10.8],0,'Visible stone plaque, text omitted rather than invented')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.001).simplify(.001)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
v=np.round(v,4) # 0.0001mm export grid; STL reload verified independently
v,inv=np.unique(v,axis=0,return_inverse=True);f=inv[f]
area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)*.5
keep=area>1e-9;f=f[keep];mi=mi[keep]
used,inv=np.unique(f,return_inverse=True);v=v[used];f=inv.reshape(-1,3)
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NPTU Pingshih broadcast memorial tower');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Complete visible tower mass, two observed speaker faces only; unseen faces neutral closures. Photo-normalized display model, not surveyed dimensions. Crest motif and tiny ladder rungs omitted.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
