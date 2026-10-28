#!/usr/bin/env python3
"""NTU Odeum: dimensioned2016 plan and official exterior drawing/photo; estimated fine details."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e} for i,n,c,e in [
 ('wall','Cream tiled wall','#D6C9B7','Official exterior photograph, uncalibrated'),('frame','Grey structural frames','#777C79','Photographed tapered front frame, official axon side frames'),('roof','Grey roof','#747A76','Official axon roof topology; approximate colour'),('glass','Opaque blue-green glass','#294F58','Official front stained glass approximated opaque for manufacturing'),('mullion','Pale metal mullions','#A4B6B4','Official front photo'),('coral','Coral fascia','#BD6851','Official front canopy soffit and front wall band'),('base','Authored support','#B4B6AD','Not terrain'),('door','Door surround','#605A4E','Official front photo'),('stain_green','Glass muted green','#65867B','Selected glass colours approximate'),('stain_purple','Glass muted purple','#786C87','Selected glass colours approximate'),('stain_blue','Glass muted blue','#507B9A','Selected glass colours approximate')]]
SCALE=6.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.5]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Official axon/photo feature; exact dimensions approximate'):add(name,box(a,b),mat,evidence)
def prism(name,points,y0,y1,mat,evidence):
 add(name,mf.CrossSection([points]).extrude(y1-y0).rotate([90,0,0]).translate([0,y1,0]),mat,evidence)
# Local x is front right, y towards stage/rear; no geographic orientation claim.
# Main hall interior7.95m wide; audience12.9m +stage6.4m +foyer~4.0m.
W,L=8.55,23.0
bx('Display support',[-1.8,-3.4,-.5],[25.7,25.2,0],6,'Authored display support, not terrain')
prism('Main gabled hall envelope',[(0,0),(W,0),(W-.55,8.6),(W/2,9.5),(.55,8.6)],0,L,0,'2016 plan main hall +official front/axon; height~9.5m estimated from8.6m internal ceiling')
# Low longitudinal service strip and perpendicular office wing: retain full2016 plan outline.
bx('Side service strip',[8.2,0,0],[12.45,23.0,3.4],0,'2016 plan toilets, office and second backstage beside hall; height approximate')
bx('Perpendicular office wing',[12.25,12.25,0],[24.0,19.0,3.5],0,'2016 plan black office rectangle; width/depth traced proportionally, not directly dimensioned')
bx('First backstage and equipment',[12.25,19.,0],[18.7,23.85,3.5],0,'2016 plan first backstage/equipment outline; height approximate')
bx('Stage rear projection',[1.3,22.9,0],[7.25,23.8,8.0],0,'2016 plan shallow projection behind screen; exterior roof not photographed, simplified cap')
# Gable roof, sloping gently on both halves, no flat box substituted for main nave.
prism('Left roof plane',[(.45,8.48),(W/2,9.38),(W/2,9.60),(.35,8.70)],-.18,L+.18,2,'Official axon and front gable silhouette')
prism('Right roof plane',[(W/2,9.38),(W-.45,8.48),(W-.35,8.70),(W/2,9.60)],-.18,L+.18,2,'Official axon and front gable silhouette')
# Each portal frame also crosses the roof, as visible in official axon.
for y in [3.5,6.7,9.9,13.1,16.3,19.5,22.7]:
 prism(f'Roof portal left{y}',[(.27,8.60),(W/2,9.50),(W/2,9.75),(.27,8.85)],y-.16,y+.16,1,'Official axon transverse portal frames over gabled roof; exact thickness estimated')
 prism(f'Roof portal right{y}',[(W/2,9.50),(W-.27,8.60),(W-.27,8.85),(W/2,9.75)],y-.16,y+.16,1,'Official axon transverse portal frames over gabled roof; exact thickness estimated')
# Large front tapered structural surround is characteristic and visibly separate from wall panels.
for side in [0,1]:
 pts=[(-.18,0),(.43,0),(.95,8.65),(.30,8.83)] if side==0 else [(W-.43,0),(W+.18,0),(W-.30,8.83),(W-.95,8.65)]
 prism('Front tapered frame'+str(side),pts,-.16,.20,1,'Official front photo: sloping tapered grey perimeter')
prism('Front gable cap',[(.30,8.3),(W/2,9.15),(W-.30,8.3),(W-.30,8.83),(W/2,9.72),(.30,8.83)],-.17,.23,1,'Grey deep front gable border; geometric approximation')
# Six slender side windows and seven grey portal ribs from official axon (not blind facade grid).
for y in [3.5,6.7,9.9,13.1,16.3,19.5,22.7]:
 for side in [0,1]:
  pts=[(-.12,.15),(.35,.15),(.88,8.75),(.38,8.9)] if side==0 else [(W-.35,.15),(W+.12,.15),(W-.38,8.9),(W-.88,8.75)]
  prism(f'Side tapered rib{side}-{y}',pts,y-.16,y+.16,1,'Official axon repeating structural portal ribs; exact spacing inferred')
for j,y in enumerate([5.1,8.3,11.5,14.7,17.9,21.1]):
 for side in [0,1]:
  # Long-side wall tapers .55m by8.6m; glazing follows slope, rather than floating.
  z0,z1=(.8 if side==0 else 3.55),8.1;x0=.55*z0/8.6;x1=.55*z1/8.6
  pts=[(x0-.025,z0),(x0+.045,z0),(x1+.045,z1),(x1-.025,z1)] if side==0 else [(W-x0-.045,z0),(W-x0+.025,z0),(W-x1+.025,z1),(W-x1-.045,z1)]
  prism(f'Long side glass{side}-{j}',pts,y-.30,y+.30,3,'Official axon slender side glazing; opposite side repetition inferred, not fully photographed')
  for z in ([1.3,2.4,3.4,4.4,5.5,6.6,7.7] if side==0 else [4.4,5.5,6.6,7.7]):
   x=.55*z/8.6
   a,b=(x-.05,x+.04) if side==0 else (W-x-.04,W-x+.05)
   bx(f'Window crossbar{side}-{j}-{z}',[a,y-.31,z],[b,y+.31,z+.055],4)
# Front vertical stained-glass band terminating in gable.
bx('Front tall glazing',[3.28,-.19,3.6],[5.27,-.12,8.85],3,'Official front photograph tall centre glazing')
for row in range(8):
 for col in range(3):
  mat=[3,8,10,9,3,8,3][(row*3+col)%7];x=3.30+col*.65;z=3.64+row*.63
  bx(f'Front glass pane{row}-{col}',[x,-.218,z],[x+.62,-.18,min(z+.60,8.82)],mat,'Approximate stained glass colour rhythm; not identical panes')
for x in [3.25,3.92,4.59,5.29]:bx(f'Front glazing mullion{x}',[x-.025,-.25,3.6],[x+.025,-.19,8.86],4)
for z in [3.61+i*.63 for i in range(9)]:bx(f'Front glazing crossbar{z}',[3.25,-.25,z],[5.30,-.19,z+.045],4)
# Entrance canopy spans hall+service wing and continues along side.
bx('Front canopy soffit',[-.65,-.85,3.25],[12.7,.6,3.38],5,'Official front photo coral soffit')
bx('Front canopy fascia',[-.70,-.9,3.38],[12.75,.65,3.67],1,'Official front photo broad grey slab')
bx('Side strip roof',[8.2,.5,3.4],[12.7,23.15,3.65],2,'Official axon flat roof over service strip')
bx('Office wing roof',[12.2,12.0,3.5],[24.25,19.2,3.8],2,'Official axon low office roof; no unseen equipment')
bx('Backstage roof',[12.2,18.9,3.5],[18.95,24.0,3.8],2,'Official axon lower backstage mass roof')
# Door1.77m width from plan, surround slightly larger; true transparent interior deliberately omitted.
bx('Entry surround',[3.29,-.25,.12],[5.26,.05,3.08],7,'Plan entry width1.77m,height2.89m; surround photograph')
bx('Entry opaque door',[3.39,-.28,.16],[5.16,-.22,2.98],3,'Official photo dark glazed double doors')
for x in [3.39,4.275,5.16]:bx(f'Entry stile{x}',[x-.04,-.32,.15],[x+.04,-.26,3.0],7)
bx('Front coral band',[5.35,-.20,1.25],[8.25,-.11,1.55],5,'Official photo horizontal accent to right of door, no tiny lettering')
# Office ribbon windows from official axon; unseen back walls remain plain.
for j in range(6):
 x=12.7+j*1.8
 bx(f'Office glazing{j}',[x,12.15, .55],[x+1.5,12.25,2.85],3,'Official axon outward-facing office windows; exact count approximate')
 bx(f'Office mullion{j}',[x+.73,12.1,.55],[x+.79,12.2,2.85],4)
 bx(f'Office transom{j}',[x,12.08,2.25],[x+1.5,12.19,2.32],4)
for y in [1.4,3.4,5.4,7.4,9.4]:bx(f'Service side window{y}',[12.43,y,.65],[12.50,y+1.25,2.8],3,'Official axon side strip openings; spacing schematic')
# Ground approach and small ramp: authored simplified photo-derived entry, no site landscape.
bx('Front platform',[-.2,-1.4,0],[W+.2,.2,.26],1)
for i in range(3):bx(f'Entry step{i}',[.8,-2.3+i*.3,0],[7.8,-1.2,.085*(i+1)],1,'Front photographed steps; tread/riser dimensions estimated')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NTU Odeum plan-backed whole exterior');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'2016 official dimensioned plan, official axonometric and undated official photos; rear apertures and accessory details simplified; not survey/current-condition/trial print'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
