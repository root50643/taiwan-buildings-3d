#!/usr/bin/env python3
"""NCU Ju De visible-front segment. Dimensions are photo proportions, not surveyed."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('wall','Gray blue wall','#9EAEB7','Official lower exterior photo; uncalibrated color'),
('frame','Pale gray window frame','#C9CBC3','Visible frames, thickness normalized'),
('glass','Muted window shadow','#69787A','Visible glass and curtains abstracted'),
('base','Authored support base','#9A9C96','Manufacturing support, not actual stairs or ground'),
('cut','Artificial cut back','#ADB0AC','Unobserved backing, not actual rear facade')]]
SCALE=6.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.6]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Observed visible feature; photo normalized, not measured'):add(name,box(a,b),mat,evidence)
def frontcyl(rad,depth,x,y,z,n=24):return mf.Manifold.cylinder(depth,rad,rad,n).rotate([90,0,0]).translate([x,y,z])
bx('Author connected footing',[-3.9,-1.1,-.6],[3.9,1.5,-.15],3,'Authored support, not actual staircase or ground')
bx('Tall recessed two-window wall',[-3.25,-.10,-.2],[.65,1.00,11.45],0,'Visible recessed panel; windows are nominal proportion, not measured')
bx('Right blank name wall',[.65,-.30,-.2],[3.5,1.00,10.8],0,'Observed tall plain wall; lettering intentionally omitted')
bx('Left high frame pier',[-3.5,-.42,-.2],[-3.10,1.00,13.0],0,'Visible high frame left pier; nominal depth')
bx('Right high frame pier',[.40,-.42,-.2],[.82,1.00,13.0],0,'Visible high frame right pier; nominal depth')
bx('Upper cross member',[-3.5,-.42,12.40],[.82,1.00,13.0],0,'Top horizontal frame; visible narrow opening retained below, no roof added')
# Back closure remains BELOW the opening: the upper slot is genuinely open.
bx('Artificial panel back',[-3.25,.93,-.18],[.65,1.10,11.45],4,'Author rear closure, not actual rear')
bx('Artificial namewall back',[.65,.93,-.18],[3.5,1.10,10.8],4,'Author rear closure, not actual rear')
for z in [3.15,7.50]:
 x0=-2.65;x1=-.18;h=1.95
 bx('Window shadow',[x0,-.15,z],[x1,-.08,z+h],2,'One of two photograph-visible windows, no interior reconstruction')
 for x in [x0,x1]:bx('Window outer jamb',[x-.05,-.25,z-.05],[x+.05,-.07,z+h+.05],1)
 for zz in [z,z+1.30,z+h]:bx('Window horizontal frame',[x0-.05,-.25,zz-.05],[x1+.05,-.07,zz+.05],1)
 bx('Upper window divider',[-1.46,-.25,z+1.30],[-1.38,-.07,z+h],1)
 for x in [-1.85,-1.02]:bx('Lower window divider',[x-.04,-.25,z],[x+.04,-.07,z+1.30],1)
 bx('Simple sill',[x0-.09,-.35,z-.12],[x1+.09,-.07,z-.03],1)
# Foreground white objects are benches, not columns; omitted entirely.
# No speculative upper roof, unseen side wings, whole-building plan, wiring, names or furniture.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.001).simplify(.001)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
v=np.round(v,2) # 0.01mm export grid prevents float32 STL sliver collapse
v,inv=np.unique(v,axis=0,return_inverse=True);f=inv[f]
area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)*.5
keep=area>1e-9;f=f[keep];mi=mi[keep]
used,inv=np.unique(f,return_inverse=True);v=v[used];f=inv.reshape(-1,3)
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NCU Ju De facade');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Photo-informed Ju De stair-side two-window high-frame and blank namewall segment ONLY; no stairs, benches, wings or roof plan.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
