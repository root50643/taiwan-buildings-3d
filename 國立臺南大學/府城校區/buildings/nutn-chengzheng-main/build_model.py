#!/usr/bin/env python3
"""Chengzheng exterior mass; official plan/photo evidence, not current-condition survey."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e} for i,n,c,e in [
 ('wall','Terracotta facade','#A95D48','Official dated/undated historical exterior photos'),('glass','Opaque dark glazing','#3C5353','Uncalibrated historical-photo approximation'),('frame','Window frame','#B6B4A0','Visible pale narrow frames'),('accent','Dark brick trim','#894B3D','Photo3 central portal and facade pilasters'),('roof','Neutral roof plane','#9C9C90','Roof topology unavailable; explicitly neutral enclosed cap'),('base','Authored display support','#BFC5BB','Support not terrain'),('shadow','Recessed entry','#263A36','Main portal shadow approximation')]]
SCALE=2.6
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.6]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Historical official-photo facade; dimensions and repeated detail approximate'):add(name,box(a,b),mat,evidence)
W,D,H=71.,32.,22.25
F=H/5
bx('Authored display support',[-4,-7,-.6],[75,35,0],5,'Not terrain; basement omitted')
# Axis2-17 dimension sum71m, A-F32m; central17m hall separates27m wings.
# Interior courts and hall roof are NOT cut through without roof evidence.
bx('West wing principal envelope',[0,0,0],[27,D,H],0,'1F dimensioned plan2025 and photos; interior not represented')
bx('East wing principal envelope',[44,0,0],[W,D,H],0,'1F dimensioned plan2025 and photos; interior not represented')
bx('Central connecting hall',[27,.8,0],[44,D-.8,H],0,'1F central entrance and tall glazed central facade; not an outdoor gap')
# End stair projections documented in1F. Upper extent is schematic under photographed side mass.
for x,xx in [(-2,0),(71,73)]:
 bx(f'End stair projection{x}',[x,11,0],[xx,21,H-.8],0,'1F stair projection position; height simplified from exterior')
# Subtle façade pilasters and 5 repeated storeys. Six4.5m bays per wing.
for side in [0,D]:
 sg=-1 if side==0 else 1
 for start in [0,44]:
  for j in range(7):
   x=start+j*4.5;aa,bb=sorted([side-.06*sg,side+.22*sg]);bx(f'Wing pilaster{side}-{x}',[x-.17,aa,.2],[x+.17,bb,H-.5],3)
  for k in range(5):
   z=k*F
   for j in range(6):
    x=start+j*4.5+2.25
    aa,bb=sorted([side-.05*sg,side+.11*sg]);bx(f'Window surround{side}-{k}-{x}',[x-1.65,aa,z+1.15],[x+1.65,bb,z+3.35],2)
    aa,bb=sorted([side+.1*sg,side+.16*sg]);bx(f'Glazed opening{side}-{k}-{x}',[x-1.52,aa,z+1.27],[x+1.52,bb,z+3.23],1)
    for dx in [-.51,.51]:
     aa,bb=sorted([side+.15*sg,side+.22*sg]);bx(f'Glazing mullion{side}-{k}-{x}-{dx}',[x+dx-.045,aa,z+1.24],[x+dx+.045,bb,z+3.26],2)
    aa,bb=sorted([side+.15*sg,side+.23*sg]);bx(f'Glazing transom{side}-{k}-{x}',[x-1.55,aa,z+2.65],[x+1.55,bb,z+2.73],2)
    aa,bb=sorted([side-.08*sg,side+.58*sg]);bx(f'Window shade{side}-{k}-{x}',[x-1.78,aa,z+3.4],[x+1.78,bb,z+3.57],0,'Photo6 horizontal short window shades')
# Central17m bay: two brick piers flank9m glazed curtain wall.
for side in [0,D]:
 sg=-1 if side==0 else 1
 for x in [27,40]:
  aa,bb=sorted([side-.2*sg,side+.45*sg]);bx(f'Central brick pier{side}-{x}',[x,aa,0],[x+4,bb,H+.24],0)
  for k in range(5):
   aa,bb=sorted([side+.44*sg,side+.50*sg]);bx(f'Pier narrow opening{side}-{x}-{k}',[x+1.35,aa,k*F+1.35],[x+2.65,bb,k*F+3.15],1)
 aa,bb=sorted([side+.77,side+.87]) if side==0 else (D-.87,D-.77)
 bx(f'Curtain wall{side}',[31,aa,3.3],[40,bb,H-2.7],1,'Historical front central multi-storey glazed hall; rear extent schematic')
 for x in [31+i*1.5 for i in range(7)]:
  aa,bb=(.65,.82) if side==0 else (D-.82,D-.65);bx(f'Curtain vertical{side}-{x}',[x-.09,aa,3.3],[x+.09,bb,H-2.6],2)
 for z in [3.3+i*1.25 for i in range(14)]:
  aa,bb=(.64,.82) if side==0 else (D-.82,D-.64);bx(f'Curtain horizontal{side}-{z}',[31,aa,z],[40,bb,z+.1],2)
 # Broad brick horizontal floor bands, distinguish from glazing grid.
 for z in [7.4,12.2,17.0]:
  aa,bb=(.3,.83) if side==0 else (D-.83,D-.3);bx(f'Curtain brick band{side}-{z}',[31,aa,z],[40,bb,z+.45],3)
 aa,bb=(.56,.84) if side==0 else (D-.84,D-.56);bx(f'Entry dark doors{side}',[31,aa,.1],[40,bb,3.15],6)
 for x in [31,33.25,35.5,37.75,40]:
  aa,bb=(.45,.7) if side==0 else (D-.7,D-.45);bx(f'Entry jamb{side}-{x}',[x-.1,aa,.1],[x+.1,bb,3.3],2)
# Arched fanlight in central brick pediment; clipping circle is supported by front photo3.
# Highest point23.75m reflects documented height, but exact floor/roof allocation is approximate.
verts=np.array([[30.5,-.1,19.3],[40.5,-.1,19.3],[35.5,-.1,23.75],[30.5,.9,19.3],[40.5,.9,19.3],[35.5,.9,23.75]],np.float32)
faces=np.array([[0,2,1],[3,4,5],[0,1,4],[0,4,3],[1,2,5],[1,5,4],[2,0,3],[2,3,5]],np.uint32)
add('Central triangular brick pediment',mf.Manifold(mf.Mesh(verts,faces[:,::-1].copy())),0,'Photo3: triangular brick pediment surrounding semicircular fanlight')
circle=mf.Manifold.cylinder(.14,2.9,2.9,48).rotate([90,0,0]).translate([35.5,.02,19.8]);clip=box([32,-.4,19.8],[39,.1,22.8]);add('Central semicircular fanlight',mf.Manifold.batch_boolean([circle,clip],mf.OpType.Intersect),1,'Photo3 half-round dark fanlight; no circular old-library motif')
# Side ends: sparse apertures, no unsupported dense blanket grid.
for side in [0,71]:
 sg=-1 if side==0 else 1
 for k in range(5):
  for y in [5,27]:
   aa,bb=sorted([side-.05*sg,side+.1*sg]);bx(f'End small window{side}-{k}-{y}',[aa,y-.65,k*F+1.6],[bb,y+.65,k*F+2.8],1,'Photo2 small sparse side windows; both sides schematic mirrored')
# Front raised approach and steps; plan shows elaborate polygonal side stairs, simplified straight.
bx('Entry platform',[27,-2,0],[44,1,.55],0,'1F front steps, simplified accessible display geometry')
for i in range(6):bx(f'Entry step{i}',[29,-4+i*.35,0],[42,-1.7+i*.35,.09*(i+1)],0,'Plan-derived front approach, risers estimated')
for a,b in [(0,27),(44,71)]:
 bx(f'Wing plinth{a}',[a,-.4,0],[b,.12,.6],3)
 bx(f'Neutral roof{a}',[a+.3,.3,H-.08],[b-.3,D-.3,H+.08],4,'Roof not visible in sources; neutral solid cap, no claimed courtyard roof topology')
 for y in [0,D-.25]:bx(f'Roof parapet{a}-{y}',[a,y,H],[b,y+.25,H+.45],0,'Photographic edge; thickness approximate')
bx('Neutral central roof',[27,1,H-.1],[44,D-1,H+.08],4,'Unverified roof topology; neutral enclosed cap, not an open courtyard claim')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NUTN Chengzheng five-storey main building');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Official dimension-chain 1F plan and historical-photo bounded exterior; enclosed roof is neutral because roof topology not verified; not survey/current-condition/trial print'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
