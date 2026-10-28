#!/usr/bin/env python3
"""NDHU Artopia exterior study: official 2012 plans and completed facade photo; not a survey."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [('wall','Granite grey ground floor','#AAA9A3','School completed exterior photo; uncalibrated'),('rib','White expanded-metal skin approximation','#D9DDD9','School completed exterior photo; solid-backed coarse panel grid, no literal perforations'),('glass','Opaque dark glazing','#344643','Historic photo dark apertures; manufacturing solid inlays'),('roof','White rooftop volume','#DAD9CE','Visible existing rooftop mass in school photo; unseen depth estimated'),('base','Authored support','#B0B3AC','Display support not site terrain'),('wood','Warm entrance vertical accent','#98633E','Completed school photograph')]]
SCALE=0.12
items=[];ops=[];ids={}
def box(a,b):
 a=np.round(np.array(a)*100);b=np.round(np.array(b)*100);return mf.Manifold.cube((b-a).tolist()).translate(a.tolist())
def add(name,s,mat,evidence):
 s=s.translate([0,0,60]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Historic photo inferred detail; estimated size'):add(name,box(a,b),mat,evidence)
def poly(name,pts,z0,z1,mat,evidence):add(name,mf.CrossSection([(np.array(pts)*100).tolist()]).extrude((z1-z0)*100).translate([0,0,z0*100]),mat,evidence)
# Local x follows grid1->4, y from A rear to C street; cardinal orientation not asserted.
# Dimensions are official 2012 grid spacings, not an as-built measurement.
bx('Authored rectangular display base',[-.8,-.8,-.6],[9.7,8.4,0],4,'Authored support, NOT full triangular site or survey')
outline=[(0,0),(8.9,0),(8.9,6.6),(5.6,7.6),(0,7.6)]
poly('Ground storey with angled entry',outline,0,3.017,0,'2012 first-floor plan8.9x7.6m grid, angled front entrance; 3m height estimated')
bx('Upper storey opaque simplified envelope',[0,0,2.9],[8.907,7.607,6.0],0,'2012 second-floor plan rectangular body, height estimated; interior omitted')
bx('Roof deck',[0,0,5.9],[8.9,7.6,6.15],3,'Flat roof inference from official completed facade, depth unverified')
bx('Existing upper roof mass study',[.2,.2,6.05],[8.7,2.6,8.1],3,'White upper roof volume visible in official completed photo; rear depth and height estimated, not another verified storey')
bx('Reddish thin roof cap',[.12,.12,8.08],[8.78,2.68,8.2],5,'Thin reddish edge visible official completed photograph; depth estimated')
# Complete visible street skin translated to robust low-relief grid, NOT microscopic expanded mesh.
for i in range(17):
 x=i*8.9/16
 bx('Front metal skin vertical rib'+str(i),[x-.035,7.56,3.0],[x+.035,7.73,6.85],1,'Approximate panel rhythm from completed photo; count not surveyed, enlarged0.84mm print thickness')
bx('Front screen solid manufacturing backing',[0,7.50,3.0],[8.9,7.66,6.85],1,'Fine perforated mesh represented as solid backing with ribs, not literal holes')
for i in range(14):
 y=i*7.6/13
 bx('Left metal skin vertical rib'+str(i),[-.13,y-.035,3.0],[.04,y+.035,6.85],1,'Official completed photo left face skin panel rhythm approximated')
bx('Left screen solid manufacturing backing',[-.12,0,3.0],[.1,7.6,6.85],1,'Fine perforated mesh represented as solid backing with ribs')
# Front top frame visible in official built photo; no invented artwork suspended inside.
bx('Front open roof screen header',[-.05,7.55,6.75],[8.95,7.78,7.0],1,'Open-top metal framing in completed photo; height estimated')
bx('Left open roof screen header',[-.15,0,6.75],[.08,7.75,7.0],1,'Visible top framing, no predicted rear screen')
bx('Front doorway opaque glazing',[.3,7.52,.15],[3.35,7.68,2.65],2,'Ground opening in school completed photo; dark solid inlay')
bx('Front warm entrance accent',[3.55,7.52,.05],[4.25,7.72,3.1],5,'Vertical warm-toned entrance panel visible school photograph; width estimated')
poly('Angled entrance opaque glazing',[(5.65,7.58),(8.85,6.61),(8.9,6.73),(5.7,7.7)],.15,2.7,2,'Angled opening from2012plan and completed close photograph')
bx('Right ground aperture',[8.86,4.8,.15],[9.02,6.35,2.6],2,'Right door visible streetscape photograph; position estimated')
bx('Left vertical LED plaque',[-.18,6.15,3.1],[.04,6.65,5.45],2,'School photo vertical sign; no copied logo/lettering')
bx('Front entrance canopy',[.15,7.48,2.75],[3.55,8.0,2.9],1,'Completed photo canopy; manufacturing-solid simplification')
bx('Right entrance canopy',[8.82,4.6,2.8],[9.5,6.6,2.94],1,'Close streetscape photo canopy; no unsupported slim lattice')
# Completed-photo defining features, deliberately coarse rather than absent.
for j,z in enumerate([3.8,4.7,5.6]):
 bx('Front horizontal skin division'+str(j),[-.02,7.64,z],[8.92,7.79,z+.09],1,'Visible horizontal panel subdivisions in official completed facade; approximate spacing')
 bx('Left horizontal skin division'+str(j),[-.18,-.02,z],[.04,7.68,z+.09],1,'Horizontal panel subdivisions, coarse manufacturing interpretation')
# White upper roof enclosure has a visible window row; its unseen back remains plain.
for j in range(6):
 x=.65+j*1.22
 bx('Roof enclosure visible window'+str(j),[x,2.56,6.85],[x+.88,2.70,7.52],2,'Window row visible above metal skin in official photograph; six approximate bays, count/size not surveyed')
 bx('Roof window sill'+str(j),[x-.04,2.56,6.79],[x+.92,2.75,6.87],1,'Light window sill in official completed photo; enlarged')
# Round information column at the photographed right street corner. No copied text.
add('Rounded streetcorner information pillar',mf.Manifold.cylinder(285,31,31,32).translate([888,665,0]),1,'Close streetscape photo round information column; radius0.31m estimated with plan R300 hint; no artwork/logo')
# Visible coarse slats on canopy; shallow backing is retained for reliable attachment.
for j in range(14):
 x=.2+j*.25
 bx('Front canopy coarse slat'+str(j),[x,7.45,2.88],[x+.075,8.06,3.01],1,'Photographed canopy slatted upper surface, approximate pitch and enlarged thickness')
for j in range(9):
 y=4.65+j*.23
 bx('Right canopy coarse slat'+str(j),[8.80,y,2.92],[9.54,y+.075,3.05],1,'Close photograph side canopy coarse slats; not exact microscopic lattice')
# Ground glazing divisions: retained opaque for printable window recess appearance.
for x in [.30,1.31,2.32,3.35]:
 bx('Front door vertical frame'+str(x),[x-.035,7.65,.12],[x+.035,7.76,2.67],1,'Ground glazed door/window frames in completed photo, approximate rhythm')
bx('Front door upper frame',[.27,7.65,2.61],[3.39,7.76,2.71],1,'Visible ground opening header')
for y in [4.8,5.575,6.35]:
 bx('Right door frame'+str(y),[9.00,y-.035,.12],[9.10,y+.035,2.65],1,'Close photograph framed side door, simplified')
# Rear apertures and right upper face are intentionally plain: not evidenced as-built.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.05).simplify(.05)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NDHU Artopia source-based exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'2012 design plan grid plus school completed facade. Height and rooftop depth estimated; unobserved rear apertures omitted; no trial print; not current surveyed condition'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
