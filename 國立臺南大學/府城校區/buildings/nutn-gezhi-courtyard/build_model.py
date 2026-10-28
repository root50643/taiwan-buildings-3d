#!/usr/bin/env python3
"""NUTN Ge-Zhi five-storey building: official plan/photo bounded exterior.
No source images; absolute dimensions/columns/window details estimated.
"""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e} for i,n,c,e in [
 ('wall','Off-white tile','#D7D3C5','Official courtyard photographs'),('glass','Opaque dark glass','#505957','Photographic uncalibrated approximation'),('frame','Grey window frames','#8B8C81','Photographic simplified detail'),('accent','Muted apricot bands','#C4A489','Visible corridor bands'),('roof','Neutral roof plane','#B7B9AD','Roof details not documented'),('base','Display support','#BFC5BB','Authored support, not terrain'),('shadow','Recessed doors','#78766A','Simplified visible classroom openings')]]
SCALE=3.5
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.55]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Approximate feature based on official floor plan/photo, not survey'):add(name,box(a,b),mat,evidence)
W,D,F=48.3,29.2,3.7
bx('Display support',[-2,-2,-.55],[W+2,D+2,0],5,'Authored display base')
# Plan footprint: long left wing, back strip, shorter right wing; front-right 1F roof terrace.
for k in range(5):
 z=k*F
 bx(f'Left rooms level{k+1}',[0,2.2,z],[10,D,z+F])
 bx(f'Back rooms level{k+1}',[10,21.2,z],[W,D,z+F])
 bx(f'Right rooms level{k+1}',[34,10.2,z],[W,21.3,z+F])
 # central courtyard room front above double-height entrance
 if k>=2:bx(f'Central rooms above entrance {k+1}',[12.6,14.2,z],[34,18.35,z+F])
 bx(f'Back enclosed corridor slab{k+1}',[10,18.15,z],[W,21.4,z+.26])
 bx(f'Back upper slab{k+1}',[10,18.15,z+F-.2],[W,21.4,z+F])
 # Left open walkway
 bx(f'Left gallery floor{k+1}',[9.8,0,z],[12.7,21.3,z+.26])
 for y in [1,5.2,9.4,13.6,17.8,21.0]:bx(f'Gallery column{k}-{y}',[12.2,y-.18,z],[12.65,y+.18,z+F])
 if k>0:bx(f'Left gallery guard{k}',[12.25,0,z+.20],[12.65,21.3,z+1.12])
 bx(f'Left gallery roof{k+1}',[9.9,0,z+F-.18],[12.7,21.3,z+F])
 # inner left windows behind walkway, photo-supported grouping approximated
 for j,y in enumerate([3,7.2,11.4,15.6,19.8,24]):
  bx(f'Gallery window frame{k}-{j}',[9.94,y-.75,z+1.45],[10.16,y+.75,z+2.85],2)
  bx(f'Gallery glass{k}-{j}',[10.14,y-.65,z+1.55],[10.2,y+.65,z+2.75],1)
  bx(f'Gallery mullion{k}-{j}',[10.19,y-.025,z+1.5],[10.23,y+.025,z+2.8],0)
  bx(f'Gallery transom{k}-{j}',[10.18,y-.75,z+2.35],[10.25,y+.75,z+2.45],0)
 # long exterior back windows from plan wall openings; panes simplified
 for j,x in enumerate([2.6,6.5,17.5,21.5,25.5,30,37,41.5,45.6]):
  bx(f'Back frame{k}-{j}',[x-.82,D-.04,z+1.3],[x+.82,D+.13,z+2.7],2)
  bx(f'Back pane{k}-{j}',[x-.7,D+.12,z+1.42],[x+.7,D+.16,z+2.6],1)
 # left outer openings plan supported but photo not detailed
 for j,y in enumerate([4.5,8.7,13,17.3,22,26]):
  bx(f'Left outer frame{k}-{j}',[-.13,y-.8,z+1.3],[.04,y+.8,z+2.7],2)
  bx(f'Left outer pane{k}-{j}',[-.17,y-.7,z+1.42],[-.12,y+.7,z+2.6],1)
 # right long outer facade
 for j,y in enumerate([12,16.5,23,26.5]):
  bx(f'Right outer frame{k}-{j}',[W-.04,y-.7,z+1.35],[W+.13,y+.7,z+2.7],2)
  bx(f'Right outer pane{k}-{j}',[W+.12,y-.6,z+1.45],[W+.17,y+.6,z+2.6],1)
 # Central courtyard paired room windows; tall vertical tile panels visible above entrance
 if k>=2:
  for j,x in enumerate([15,18.3,21.6,24.9,28.2,31.5]):
   bx(f'Courtyard front frame{k}-{j}',[x-.72,14.06,z+1.0],[x+.72,14.24,z+3.05],2)
   bx(f'Courtyard front glass{k}-{j}',[x-.62,14.02,z+1.1],[x+.62,14.08,z+2.95],1)
   bx(f'Courtyard front centre bar{k}-{j}',[x-.03,13.98,z+1.02],[x+.03,14.07,z+3.02],0)
   bx(f'Courtyard transom{k}-{j}',[x-.72,13.96,z+2.5],[x+.72,14.07,z+2.6],0)
  for x in [13.7,17,20.3,23.6,26.9,30.2,33.5]:
   bx(f'Tile vertical reveal{k}-{x}',[x-.16,13.98,z+.1],[x+.16,14.3,z+F],0)
 # Third-floor wide entrance window band with upper transom
 if k==2:
  bx('Entrance upper wide glass',[17.8,13.91,z+1],[29,14.02,z+3.05],1)
  bx('Entrance upper transom',[17.75,13.85,z+2.5],[29.05,13.95,z+2.61],0)
  for x in [17.8,19.65,21.5,23.35,25.2,27.05,29]:bx(f'Wide window mullion{x}',[x-.06,13.84,z+.98],[x+.06,13.95,z+3.08],0)
 # Right courtyard blank block with four stacks of narrow ventilation slots
 for x in [36,38,40,44.6]:
  for q in range(3):
   zz=z+1.4+q*.42
   bx(f'Right small slot{k}-{x}-{q}',[x-.15,10.05,zz],[x+.15,10.23,zz+.22],1)
 # glass stair vertical band at courtyard elbow
 bx(f'Elbow glazing{k}',[33.9,10.6,z+.8],[34.12,13.3,z+3.1],1)
 # outward balcony at front of right block, photo stacks 2F up
 if k>=1:
  bx(f'Elbow balcony slab{k}',[31.8,10.1,z+.0],[34.2,13.4,z+.28],0)
  bx(f'Elbow balcony solid guard{k}',[31.75,10.1,z+.2],[32.02,13.4,z+1.2],0)
  for yy in [10.1,13.12]:bx(f'Elbow balcony endwall{k}-{yy}',[31.75,yy,z+.2],[34.2,yy+.28,z+1.45],0)
# left forward stair core from floor plan, small stacked windows
bx('Left forward stair core',[5.0,-.5,0],[10.8,2.5,19.5],0)
for k in range(5):
 bx(f'Front stair window frame{k}',[6.3,-.64,k*F+1.3],[8.3,-.46,k*F+2.75],2)
 bx(f'Front stair pane{k}',[6.45,-.69,k*F+1.45],[8.15,-.61,k*F+2.6],1)
 bx(f'Front stair vertical mullion{k}',[7.25,-.73,k*F+1.3],[7.35,-.6,k*F+2.75],0)
 bx(f'Front stair transom{k}',[6.3,-.75,k*F+2.25],[8.3,-.63,k*F+2.36],0)
# 1F right low extension, documented roof terrace in photo0
bx('Front right low wing',[34,0,0],[W,10.4,F],0)
for x in [35.6,38.4,41.2,44,46.8]:
 bx(f'Low wing front window{x}',[x-.65,-.13,1.8],[x+.65,.04,2.55],2)
 bx(f'Low wing front pane{x}',[x-.55,-.18,1.9],[x+.55,-.12,2.45],1)
bx('Terrace front parapet',[33.8,-.15,F],[W+.15,.18,F+.7],0)
bx('Terrace right parapet',[W-.12,0,F],[W+.16,10.4,F+.7],0)
bx('Terrace left parapet',[33.8,0,F],[34.12,10.4,F+.7],0)
for x in [35.5,38,40.5,43,45.5,48]:bx(f'Terrace grid x{x}',[x-.02,.2,F],[x+.02,10.1,F+.015],2)
for y in [2,4,6,8,10]:bx(f'Terrace grid y{y}',[34.2,y-.02,F],[48.1,y+.02,F+.015],2)
# entrance piloti two storeys high with photosupported central circular supports
for x in [17.5,29]:
 add(f'Entrance round column{x}',mf.Manifold.cylinder(7.4,.38,.38,24).translate([x,12.8,0]),0,'Visible tall round portico columns; positions/radius approximated')
bx('Entrance balcony apron',[16.5,11.6,7.2],[30,14.4,8.1],0,'Photo central 3F projection above high entrance')
bx('Entrance platform',[12.3,8.9,0],[34.2,14.4,.5],0)
for k in range(4):bx(f'Courtyard stair{k}',[12.3,7.4+k*.4,0],[34.1,9+k*.4,(k+1)*.125],0)
# Entry doors at recessed back of double-height portico
bx('Entrance recess wall',[12.6,18.0,0],[34,18.3,7.4],0)
bx('Continuous deep entry glazing',[16.0,17.82,.5],[30.5,18.04,3.25],1)
for x in [16,19.6,23.2,26.8,30.5]:bx(f'Entry mullion{x}',[x-.08,17.75,.5],[x+.08,17.9,3.3],0)
bx('Recessed second level glazing',[13,17.8,4.1],[33.7,18.05,7.1],1)
bx('Recessed second level gallery floor',[12.6,15.8,3.7],[34,18.3,3.96],0)
bx('Recessed second level gallery guard',[12.6,15.8,3.9],[34,16.12,4.95],0)
for x in [14,19,24,29,33]:bx(f'Recessed upper mullion{x}',[x-.09,17.73,4.9],[x+.09,17.88,7.2],0)
# staggered roof outline without fabricated equipment
for name,a,b in [('Left',[0,0,18.5],[12.7,D,18.85]),('Back',[12.5,14.2,18.5],[W,D,18.85]),('Right',[34,10.2,18.5],[W,14.3,18.85])]:bx('Roof cap '+name,a,b,4)
# Low roof parapets, no roof equipment invented
for name,a,b in [('Left outer',[0,0,18.8],[.22,D,19.3]),('Back',[0,D-.22,18.8],[W,D,19.3]),('Right outer',[W-.22,10.2,18.8],[W,D,19.3]),('Left courtyard',[12.45,0,18.8],[12.7,14.2,19.3]),('Back courtyard',[12.5,14.2,18.8],[34,14.45,19.3]),('Right courtyard',[34,10.2,18.8],[W,10.45,19.3])]:bx('Low roof parapet '+name,a,b,0)
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NUTN Ge-Zhi five-storey courtyard building');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Official plan-backed five-storey asymmetric courtyard mass with low front wing; historical official-photo exterior, schematic exterior openings; not survey/current-condition/trial print'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
