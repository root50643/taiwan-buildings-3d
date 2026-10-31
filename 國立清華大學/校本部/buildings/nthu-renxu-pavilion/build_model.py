#!/usr/bin/env python3
"""NTHU Renxu pavilion 2016 photograph-based simplified shell; dimensions nominal photo proportions, not measured."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('shell','Off-white underside','#D8D8CD','2016 official photo underside, uncalibrated'),
('rim','Grey rim','#787C74','Visible grey perimeter rim'),
('column','White central column and seat','#D0D1C7','2016 official photo central column and circular seat'),
('plaque','Dark stone plaque','#414A3E','Two official detail photos show dark plaques; lettering omitted'),
('base','Grey circular platform','#B0B1A5','Visible circular platform, proportions approximate'),
('top','Unverified upper shell surface','#B4B8AE','Author thickness offset from known underside; not surveyed roof finish')]]
SCALE=22.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.6]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Visible photo detail, nominal dimensions'):add(name,box(a,b),mat,evidence)
def poly(name,pts,z0,z1,mat,evidence):add(name,mf.CrossSection([pts]).extrude(z1-z0).translate([0,0,z0]),mat,evidence)
import math
N=32
angles=[math.radians(360*i/N+360/N/2)for i in range(N)]
def cyl(name,rad,z0,z1,mat,evidence,n=64):add(name,mf.Manifold.cylinder(z1-z0,rad,rad,n).translate([0,0,z0]),mat,evidence)
cyl('Circular platform',2.85,-.6,-.36,4,'Visible circular pad; thickness and radius normalized, underground foundation not modeled')
cyl('Simplified seat central support',.34,-.38,-.08,2,'Support below circular seat visible; exact block arrangement simplified to connected central bearing')
cyl('Circular seat disc',.96,-.10,.08,2,'Visible circular seat around central column; thickness estimated')
cyl('Central column',.43,.04,1.40,2,'Single near-circular column visible; regular polygon approximation, precise fluting omitted',32)
# Curved inverted umbrella underside: steep near central neck, flattening toward outer rim.
profiles=[(.40,1.34),(.45,1.50),(.54,1.70),(.68,1.91),(.88,2.15),(1.12,2.38),(1.42,2.62),(1.76,2.85),(2.12,3.06),(2.49,3.26),(2.84,3.42),(3.12,3.53)]
v=[]
for top in [0,1]:
 for rad,z in profiles:
  for a in angles:v.append([rad*math.cos(a),rad*math.sin(a),z+top*.16])
f=[];n=len(profiles);off=n*N
for layer in [0,1]:
 for j in range(n-1):
  for i in range(N):
   a=layer*off+j*N+i;b=layer*off+j*N+(i+1)%N;c=layer*off+(j+1)*N+(i+1)%N;d=layer*off+(j+1)*N+i
   f.extend([[a,b,c],[a,c,d]] if layer==0 else [[a,c,b],[a,d,c]])
for j in [0,n-1]:
 for i in range(N):
  a=j*N+i;b=j*N+(i+1)%N;f.extend([[a,b,b+off],[a,b+off,a+off]] if j==n-1 else [[a,b+off,b],[a,a+off,b+off]])
mesh=mf.Manifold(mf.Mesh(np.array(v,dtype=np.float32),np.array(f,dtype=np.uint32)))
add('Curved inverted umbrella shell',mesh,0,'Known curved underside; upper surface is author thickness offset, not observed top geometry')
# Differentiated upper offset surface as thin integrated layer explicitly not observed.
v2=np.array(v,dtype=np.float32).copy();v2[:off,2]=v2[off:,2]-.035;v2[off:,2]+=.02
add('Neutral unverified top surface',mf.Manifold(mf.Mesh(v2,np.array(f,dtype=np.uint32))),5,'Author-neutral top finish, no actual roof waterproofing/drain geometry inferred')
cyl('Authored central top closure',.405,1.34,1.52,5,'Unverified top closure without a speculative drain opening',32)
# Grey peripheral fascia below/above photographed upper edge, regular32 sectors approximate.
ring=mf.Manifold.cylinder(.18,3.13,3.13,N)-mf.Manifold.cylinder(.22,3.055,3.055,N).translate([0,0,-.02])
add('Grey perimeter edge',ring.rotate([0,0,360/N/2]).translate([0,0,3.52]),1,'Grey perimeter edge visible, exact sectional thickness unknown')
# Blank stone inlays on two opposite column sides; no speculative calligraphy.
for side in [-1,1]:
 y=side*.421
 bx('Dark blank stone inlay',[-.13,y-.018,.80],[.13,y+.018,1.34],3,'Official detail photographs show front title and reverse donor plaque; text and exact angular relation omitted')
# No undocumented drain, pipe, roof cavity, site furniture, terrain, weathering or inscriptions.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.01).simplify(.01)
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='NTHU Renxu pavilion');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'2016 official university photograph-informed Renxu inverted umbrella pavilion; underside, column, seat and round pad approximated. Unseen top is thickness offset and hidden radial repetition inferred. No real scale or trial print.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
