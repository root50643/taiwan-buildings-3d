#!/usr/bin/env python3
"""DYU Design Curved Bridge upper span; photo-normalized complete main form."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e} for i,n,c,e in [
('yellow','Yellow bridge frame','#C8A925','Official external collage and internal panorama, uncalibrated'),
('green','Green deck','#397C62','Official panorama walking surface'),
('edge','Neutral underside edge surrogate','#858B84','Underside edge not visible in panorama; neutral nonliteral closure, not old collage color'),
('metal','Pale grey metal railing','#A5ACA7','Official panorama lattice and handrail'),
('neutral','Nominal neutral underside','#797D76','Not a claim about real underside structure')]]
SCALE=1.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Visible main-form feature; photo-normalized not surveyed'):add(name,box(a,b),mat,evidence)
def cyl_y(radius,depth,center):return mf.Manifold.cylinder(depth,radius,radius,64,True).rotate([90,0,0]).translate(center)
# Entire visible upper bridge span. Flat deck is nominal, not surveyed slope.
bx('Neutral nominal deck underside',[-15,-80,0],[15,80,1.5],4,'Nominal structural closure only; real supports and school connections excluded')
bx('Green walking surface',[-14.2,-80,1.4],[14.2,80,1.9],1,'Green surface from official 360-degree scene')
for side in [-1,1]:
 bx('Nominal neutral edge girder '+str(side),[side*14.5-.5,-80,.4],[side*14.5+.5,80,2.3],2,'Neutral nonliteral underside edge closure; older collage only consulted for main topology, not current color')
# Smooth photo-normalized longitudinal arch. Do not infer plan curvature from Chinese name.
y=np.linspace(-80,80,81);z=3.5+29*(1-(y/80)**2)
profile=list(zip(y,z))+list(zip(y[::-1],(z-2.2)[::-1]))
for side in [-1,1]:
 a=mf.CrossSection([profile[::-1]]).extrude(1.9).rotate([90,0,90]).translate([side*13.8-.95,0,0])
 add('Yellow side arch '+str(side),a,0,'Twin side arch silhouette from four official external views; smooth analytic approximation, nominal box section instead of engineering I section')
for j,y0 in enumerate([-60,-40,-20,0,20,40,60]):
 z0=3.5+29*(1-(y0/80)**2)
 if abs(y0)<=40:bx('Yellow overhead transverse tie '+str(j),[-14.4,y0-.5,z0-1.5],[14.4,y0+.5,z0-.4],0,'Multiple visible top ties; representative five central positions, open sky, no canopy')
 for side in [-1,1]:
  add('Yellow vertical round member '+str((j,side)),mf.Manifold.cylinder(z0-1.9,.45,.45,16).translate([side*13.8,y0,1.7]),0,'Vertical round supports observed in panoramic pixels; spacing representative')
# Lower square-grid railing; visible metal has pale grey color, not inferred green from distant photo.
for side in [-1,1]:
 x=side*12.5
 for j,y0 in enumerate(np.linspace(-79.5,79.5,17)):
  bx('Tall railing frame post '+str((side,j)),[x-.38,y0-.45,1.6],[x+.38,y0+.45,16],3,'Posts for transparent upper safety panels; exact count simplified')
 for z in [2.2,3.8,5.4,7,8.6,10.2]:
  bx('Grid horizontal '+str((side,z)),[x-.2,-80,z-.18],[x+.2,80,z+.18],3)
 for j,y0 in enumerate(np.linspace(-79.5,79.5,81)):
  bx('Grid vertical '+str((side,j)),[x-.22,y0-.18,2],[x+.22,y0+.18,10.4],3,'Representative square-lattice infill; exact cell count not reconstructed')
 # Two safety wire levels seen in side-facing 360 images. Glass itself omitted.
 for z in [12.2,15.6]:bx('Upper safety rail '+str((side,z)),[x-.12,-80,z-.12],[x+.12,80,z+.12],3,'Transparent panel boundaries/wires simplified to thin rails; glazing omitted')
 bx('Main handrail '+str(side),[x-.4,-80,10],[x+.4,80,10.65],3)
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='DYU Design Curved Bridge upper span');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Complete visible upper span only. Nominal straight flat deck and smooth side arches; no foundations or school building connections. Representative railing cells and cross ties. Glazing and engineering I-section details omitted. No survey or current-condition claim.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
