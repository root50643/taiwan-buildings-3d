#!/usr/bin/env python3
"""NTU Xiaofu historical 1981-1986 exterior; nominal dimensions not survey measurements."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [('wall','Warm grey concrete','#C3C1B6','Early official historic photo; uncalibrated'),('rib','Light vertical ribs','#D9D8CD','Historic courtyard photos'),('glass','Opaque dark glazing','#344643','Historic photo dark apertures; manufacturing solid inlays'),('roof','Plain grey roof','#858B86','Parapet observed; unknown roof equipment omitted'),('base','Authored support','#B0B3AC','Display support not site terrain')]]
SCALE=5.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.6]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Historic photo inferred detail; estimated size'):add(name,box(a,b),mat,evidence)
def poly(name,pts,z0,z1,mat,evidence):add(name,mf.CrossSection([pts]).extrude(z1-z0).translate([0,0,z0]),mat,evidence)
# x east across plan, y down printed plan; geographic orientation follows caption only.
# All metre-like dimensions nominal proportional fit, not legible survey dimension transcription.
outline=[(0,0),(32,0),(32,15),(19,15),(13,21),(13,32),(0,32)]
bx('Authored plinth',[-2,-2,-.6],[34,34,0],4,'Authored base, no landscaped site reconstruction')
poly('Three-storey L-shaped historic shell',outline,0,10.8,0,'Official1981 upper-floor plans, inner bevelled corner; nominal32m footprint and3.6m floors estimated')
poly('Flat roof deck',outline,10.8,11.0,3,'Photos show flat parapet roof; internal equipment not evidenced')
# Low parapet on visible silhouette. Roof stairhead positions derive two plan stairs, height approximate.
for a,b in [([0,0,10.8],[32,.25,11.5]),([0,0,10.8],[.25,32,11.5]),([31.75,0,10.8],[32,15,11.5]),([0,31.75,10.8],[13,32,11.5]),([19,14.75,10.8],[32,15,11.5]),([12.75,21,10.8],[13,32,11.5])]:bx('Parapet',a,b,0,'Historic photo parapet; height estimated')
poly('Chamfer parapet',[(12.75,20.9),(18.9,14.75),(19.25,15),(13,21.25)],10.8,11.5,0,'Official plan chamfer with low parapet')
bx('South stairhead volume',[5,28,10.85],[12.8,31.8,12.2],0,'Official plan south-end stair; early photo taller end volume. Roof access continuation and height inferred')
bx('East stairhead volume',[28,10.2,10.85],[31.8,14.8,12.2],0,'Official plan east-end stair; early photo taller end volume. Height and roof access inferred')
# Historic two exposed courtyard upper-storey window strips, inset solid dark panels.
# Full strip rhythms modeled only in visible courtyard and end faces; unseen outer walls deliberately plain.
for floor in [1,2]:
 z=3.6*floor+.65
 bx('North wing courtyard glazing'+str(floor),[19,14.94,z],[31.2,15.07,z+2.1],2,'Historic courtyard photograph upper-floor glazing; count/height approximate')
 bx('West wing courtyard glazing'+str(floor),[12.94,21,z],[13.07,31.1,z+2.1],2,'Historic courtyard photograph upper-floor glazing; count/height approximate')
 poly('Bevel courtyard glazing'+str(floor),[(12.95,20.95),(18.95,14.95),(19.08,15.08),(13.08,21.08)],z,z+2.1,2,'1981 plan inner bevel and early photo glass; solid approximation')
 for j in range(13):
  x=19+j*.95;bx(f'North wing vertical fin{floor}-{j}',[x,14.90,z-.1],[x+.18,15.38,z+2.25],1,'Thin vertical fins visible early photo; rhythm approximate, not exact count')
 for j in range(11):
  y=21+j*.95;bx(f'West wing vertical fin{floor}-{j}',[12.90,y,z-.1],[13.38,y+.18,z+2.25],1,'Historic courtyard vertical fins; approximate rhythm')
 for j in range(1,6):
  x=13+j;y=34-x
  poly(f'Chamfer fin{floor}-{j}',[(x-.1,y-.1),(x+.1,y-.3),(x+.4,y),(x+.2,y+.2)],z-.1,z+2.25,1,'Chamfer bays schematically following historic courtyard rhythm')
# Ground courtyard shopfronts, simplified opaque apertures framed by structural piers.
for x in [19.6,23.5,27.4]:bx('North ground shopfront'+str(x),[x,14.94,.3],[x+3.2,15.08,3.15],2,'Historic courtyard photo ground apertures; shop labels omitted')
for y in [22,26.4]:bx('West ground shopfront'+str(y),[12.94,y,.3],[13.08,y+3.6,3.15],2,'Historic courtyard ground openings; dimensions estimated')
poly('Chamfer ground entrance',[(13.4,20.5),(18.5,15.4),(18.62,15.52),(13.52,20.62)],.2,3.15,2,'Central historic entrance assumed from upper-floor bevel and early photograph; no later external stair')
# East end small square apertures observed on early1980s distant photograph.
for z in [4.2,7.8]:bx('Historic east end square window'+str(z),[31.94,7.2,z],[32.08,9.4,z+1.4],2,'Figure5 right-hand end wall square openings; position approximate')
# Long horizontal floor bands reinforce the clear three-storey silhouette, no texture/photo embedded.
for z in [3.45,7.05]:
 bx('North courtyard floor band'+str(z),[19,14.88,z],[32,15.23,z+.2],0)
 bx('West courtyard floor band'+str(z),[12.88,21,z],[13.23,32,z+.2],0)
 poly('Chamfer floor band'+str(z),[(12.6,21.16),(19.16,14.6),(19.51,14.95),(12.95,21.51)],z,z+.2,0,'Official plan bevel and photographed floor bands')
# No1987 steel stairs,2012RC stairs/elevator, modern vine skin, logos or invented rooftop plant.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NTU Xiaofu circa1981-1986 historical exterior');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'1981 official as-built plan outline plus early1980s photos. Estimated dimensions; unknown outer apertures omitted. Historical exterior approximation, not current condition or trial print'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
