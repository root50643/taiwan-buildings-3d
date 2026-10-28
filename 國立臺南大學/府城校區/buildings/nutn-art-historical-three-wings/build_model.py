#!/usr/bin/env python3
"""NUTN Art Building before Aug 2024 partial demolition: official floor-plan massing and courtyard-photo exterior approximation.
No source images; absolute dimensions/columns/window details estimated.
"""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e} for i,n,c,e in [
 ('wall','Off-white tile','#D6D4C7','Official courtyard photographs'),('glass','Opaque dark glass','#505957','Photographic uncalibrated approximation'),('frame','Grey window frames','#8B8C81','Photographic simplified detail'),('accent','Muted apricot bands','#C4A489','Visible corridor bands'),('roof','Neutral roof plane','#B7B9AD','Roof details not documented'),('base','Display support','#BFC5BB','Authored support, not terrain'),('shadow','Recessed doors','#78766A','Simplified visible classroom openings')]]
SCALE=3.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.55]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Approximate feature based on official floor plan/photo, not survey'):add(name,box(a,b),mat,evidence)
W,D,F=69.9,30.6,3.6
bx('Display support',[-2,-2,-.55],[W+2,D+2,0],5,'Artificial display base')
# Two complete U storeys, L third level only. Rooms form closed solids, galleries remain open.
for k in range(3):
 z=k*F; x0=0 if k<2 else 29.3
 bx(f'Back room mass level{k+1}',[x0,23.4,z],[W,D,z+F],0,'Official 1F/2F U and 3F right L plan')
 
 if k<2:bx(f'Back low gallery slab level{k+1}',[0,21.2,z],[29.3,23.5,z+.24])
 bx(f'Back gallery slab level{k+1}',[max(x0,29.3),19.2,z],[W,23.5,z+.24])
 bx(f'Right wing room mass level{k+1}',[61.4,0,z],[W,23.5,z+F])
 bx(f'Right gallery slab level{k+1}',[58.1,0,z],[61.5,23.5,z+.24])
 if k<2:
  bx(f'Left wing room mass level{k+1}',[0,0,z],[8.4,23.5,z+F])
  bx(f'Left gallery slab level{k+1}',[8.3,0,z],[10.7,23.5,z+.24])
 # open courtyard column grid; practical approximation, not exact count guarantee
 for x in np.arange(x0+.25,W-.2,4.3):
  yc=21.2 if x<29.3 else 19.2
  bx(f'Back gallery column {k} {x}',[x-.20,yc,z],[x+.20,yc+.45,z+F])
 for y in np.arange(.25,19.0,4.0):
  bx(f'Right gallery column {k} {y}',[58.1,y-.2,z],[58.5,y+.2,z+F])
  if k<2:bx(f'Left gallery column {k} {y}',[10.3,y-.2,z],[10.7,y+.2,z+F])
 if k>0:
  
  if k<2:
   bx(f'Back low gallery guard {k}',[0,21.2,z+.20],[29.3,21.48,z+1.05])
   bx(f'Back low band {k}',[0,21.17,z+.34],[29.3,21.22,z+.49],3)
  bx(f'Back gallery guard {k}',[max(x0,29.3),19.2,z+.20],[W,19.48,z+1.05])
  bx(f'Back apricot band {k}',[max(x0,29.3),19.17,z+.34],[W,19.22,z+.49],3)
  bx(f'Right gallery guard {k}',[58.1,0,z+.20],[58.38,19.3,z+1.05])
  bx(f'Right apricot band {k}',[58.07,0,z+.34],[58.12,19.3,z+.49],3)
  if k<2:
   bx(f'Left gallery guard {k}',[10.42,0,z+.20],[10.70,19.3,z+1.05])
   bx(f'Left apricot band {k}',[10.68,0,z+.34],[10.73,19.3,z+.49],3)
 # courtyard visible room windows and doors behind gallery, grouped not inferred on hidden exterior
 for j,x in enumerate(np.arange(x0+1.7,W-1.2,3.1)):
  bx(f'Back window frame {k} {j}',[x-.68,23.28,z+1.52],[x+.68,23.45,z+2.70],2)
  bx(f'Back window glass {k} {j}',[x-.58,23.245,z+1.62],[x+.58,23.29,z+2.60],1)
  bx(f'Back mullion {k} {j}',[x-.025,23.21,z+1.55],[x+.025,23.26,z+2.65],0)
 for side in ['right','left']:
  if side=='left' and k==2:continue
  x=61.4 if side=='right' else 8.4;sign=-1 if side=='right' else 1
  for j,y in enumerate([2.,6.,10.,14.,18.]):
   lo,hi=sorted([x,x+sign*.16]);bx(f'{side} inner frame{k}-{j}',[lo,y-.8,z+1.35],[hi,y+.8,z+2.75],2)
   lo,hi=sorted([x+sign*.16,x+sign*.20]);bx(f'{side} inner glass{k}-{j}',[lo,y-.7,z+1.45],[hi,y+.7,z+2.65],1)
# U roofs: two storey left half and L three storey right half
for name,a,b in [('Left roof',[-.20,-.2,7.15],[10.9,23.5,7.55]),('Back low roof',[-.2,21.0,7.15],[29.35,30.8,7.55]),('Back tall roof',[29.25,19.0,10.75],[70.1,30.8,11.15]),('Right roof',[57.9,-.2,10.75],[70.1,23.5,11.15])]:bx(name,a,b,0,'Roof envelope following official storey map; equipment omitted')
# Broad flat slab fascia (photo), no decorative roof objects invented.
# Curved stair enclosure at official central courtyard stair projection.
cx,cy=28.35,19.4
cyl=mf.Manifold.cylinder(12.05,3.45,3.45,64).translate([cx,cy,0])
# front half-cylinder plus rear rectangular connection into gallery
half=cyl ^ box([cx-3.6,cy-3.6,0],[cx+3.6,cy+.10,12.05])
add('Curved central stair screen',half,0,'Photo curved white screen mapped to central stair projection; radius estimated')
bx('Stair screen right blade',[31.7,16.1,0],[32.45,21.0,12.35],0,'Tall narrow separated blade visible in photo; not independent new tower')
# dark vertical slot between blade and curved screen
bx('Stair slot shadow',[31.65,17.1,.3],[32.05,19.6,11.55],6)
for z in [3.3,6.9,10.5]:bx(f'Stair landing band {z}',[31.55,16.95,z],[32.1,19.65,z+.36],3)
# Two U opening-end stair envelopes from plan; simplified enclosed return profile not interior stairs
for x0,width,h in [(0,10.7,7.2),(58.1,11.8,10.8)]:
 bx('End stair envelope '+str(x0),[x0,0,0],[x0+width,1.6,h],0,'Plan end staircase envelope; outer elevation neutral without photographs')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NUTN pre-Aug-2024 Art Building historical three-wing exterior');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Official floor-plan U footprint with partial L third storey; courtyard photo approximation, outer elevations neutral; not measured or trial printed'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
