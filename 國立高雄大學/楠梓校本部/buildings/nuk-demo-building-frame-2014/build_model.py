#!/usr/bin/env python3
"""NUK Demo Building:2014 erection-stage structural form study, not current complete building."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e} for i,n,c,e in [
('wood','Warm glulam','#AB6C36','2014 contractor photo, uncalibrated'),
('wood_light','Fresh cut timber','#BF864C','Observed timber variation, approximate'),
('metal','Steel connector plates','#7A8180','Visible grey joint plates, simplified'),
('plinth','Concrete pad','#A5A7A0','Observed individual column footings'),
('base','Authored display ground','#C3BDB0','Artificial connecting display support, not surveyed site footprint')]]
SCALE=7.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Visible structural feature; photo-normalized not measured'):add(name,box(a,b),mat,evidence)
def beam(name,a,b,w,d,mat=0,evidence='Observed main structural member, nominal simplified section'):
 a=np.array(a);b=np.array(b);v=b-a;h=np.linalg.norm(v);pitch=math.degrees(math.acos(v[2]/h));yaw=math.degrees(math.atan2(v[1],v[0]));s=mf.Manifold.cube([w,d,h]).translate([-w/2,-d/2,0]).rotate([0,pitch,yaw]).translate(a);add(name,s,mat,evidence)
# Five complete transverse frames, not an arbitrary facade fragment.
# Artificial plate only joins the otherwise isolated erection-stage frames for one-piece display.
bx('Artificial continuous display footing',[-10.5,-9.1,0],[10.0,9.1,.42],4,'Authored support for physically separate erection frames; not actual paved site')
roof=lambda x: 8.4-x*math.tan(math.radians(23.5)) if x<=0 else 8.4+x*.10
for k,y in enumerate([-8,-4,0,4,8],1):
 # Main posts straddle their crossing diagonal, preserving visibly forked paired construction.
 for side,foot,top,diagfoot,diagtop in [('high',-6.2,-8.2,-9.0,-4.8),('low',6.4,8.0,8.8,5.0)]:
  for x in [foot,diagfoot]:
   bx(f'Frame{k} {side} concrete shoe',[x-.45,y-.45,.38],[x+.45,y+.45,.85],3,'Individual pads in contractor photo; dimensions nominal')
  for off in [-.23,.23]:
   beam(f'Frame{k} {side} paired primary post',[foot,y+off,.70],[top,y+off,roof(top)+.08],.36,.20,0)
  beam(f'Frame{k} {side} diagonal',[diagfoot,y,.70],[diagtop,y,roof(diagtop)-.10],.32,.30,1)
  # Spacers connect paired legs without filling the entire fork gap.
  for t in [.12,.48,.80]:
   x=foot+(top-foot)*t;z=.7+(roof(top)-.7)*t
   bx(f'Frame{k} {side} paired-post spacer',[x-.16,y-.30,z-.11],[x+.16,y+.30,z+.11],0,'Photo shows transverse blocking between paired members; reduced count')
  # Simple plate at lower crossing region, not engineered fastener geometry.
  z=4.5 if side=='high' else 4.0
  x=foot+(top-foot)*(z-.7)/(roof(top)-.7)
  bx(f'Frame{k} {side} visible steel plate',[x-.25,y-.355,z-.34],[x+.25,y-.30,z+.34],2,'Grey connector plate observed; bolt pattern omitted, section approximate')
 for wing,xa,xb in [('high',-9.8,0.05),('low',-.05,9.2)]:
  for off in [-.23,.23]:
   beam(f'Frame{k} {wing} paired roof beam',[xa,y+off,roof(xa)],[xb,y+off,roof(xb)],.44,.20,0,'Double glulam beam retained; no roof sheeting in erection-stage source')
  for x in np.linspace(xa+.45,xb-.45,5):
   bx(f'Frame{k} {wing} beam spacer',[x-.12,y-.31,roof(x)-.12],[x+.12,y+.31,roof(x)+.12],0,'Reduced transverse blocking, not bolt-level engineering')
 bx(f'Frame{k} valley metal link',[-.35,y-.32,8.16],[.35,y+.32,8.52],2,'Visible grey valley joint simplified; not certified connection design')
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='NUK Demo Building 2014 erection-stage frame');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'2014 erection-stage five main timber frames only; no roof panels or later infill. Photo-normalized, not engineered dimensions. Artificial unified display footing.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
