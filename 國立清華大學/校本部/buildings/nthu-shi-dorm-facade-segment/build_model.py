#!/usr/bin/env python3
"""NTHU Shi dormitory visible-front segment. Dimensions are photo proportions, not surveyed."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('wall','Grey white tiled wall','#B9BDB8','Official June2026 photo; tile grid omitted'),
('frame','Pale window frames','#D4D8C9','Visible window/door frames, no exact color calibration'),
('glass','Muted window shadow','#566763','Curtains and reflections abstracted to neutral gray green'),
('brick','Red brown horizontal bands','#8B493D','Visible brick bands; uncalibrated photograph color'),
('dark','Dark recess and fan','#303A37','Shadow abstraction, not internal geometry'),
('base','Grey step and plinth','#9A9C96','Visible entry steps; authored segment footing'),
('sign','Blank sign panel','#C8C6A6','Visible pale sign; no letters copied'),
('cut','Artificial rear closure','#B1B1A9','Unobserved artificial shallow backing, not actual rear elevation')]]
SCALE=5.1
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.6]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Observed visible feature; photo normalized, not measured'):add(name,box(a,b),mat,evidence)
def frontcyl(rad,depth,x,y,z,n=24):return mf.Manifold.cylinder(depth,rad,rad,n).rotate([90,0,0]).translate([x,y,z])
bx('Authored segment footing',[-10.3,-1.5,-.6],[10.3,1.6,-.15],5,'Authored connected footing, not foundation or surveyed site')
bx('Five-bay two-visible-level wall',[-10,-.12,-.2],[10,1.35,8.1],0,'Five deliberately selected repeating facade bays, two visible levels above canopy only; not whole building')
bx('Artificial flat rear closure',[-10,1.28,-.18],[10,1.43,8.1],7,'Authored cut back, not real rear elevation')
# Horizontal brick bands visibly separate the two levels and border the lower edge.
for lo,hi in [(0,.55),(4.0,4.7)]:
 bx('Red brown brick band',[-10,-.22,lo],[10,-.10,hi],3,'Observed red brick horizontal band; courses not engraved')
for i in range(6):
 x=-10+4*i
 bx('Pale vertical structural rib',[x-.14,-.31,0],[x+.14,.02,7.85],1,'Observed pale continuous ribs, nominal spacing')
def window(name,x0,x1,z0,z1):
 bx(name+' dark glazing',[x0,-.23,z0],[x1,-.10,z1],2,'Observed glazing/shadow rectangle; curtains omitted')
 for x in (x0,x1):bx(name+' jamb',[x-.045,-.34,z0-.045],[x+.045,-.08,z1+.045],1)
 for z in (z0,z1):bx(name+' rail',[x0-.045,-.34,z-.045],[x1+.045,-.08,z+.045],1)
for bay in range(5):
 x=-9.70+4*bay
 for level in range(2):
  z=.75+4.0*level
  window('Upper horizontal glazing',x,x+3.35,z+2.0,z+2.70)
  for dx in (1.10,2.20):bx('Transom divider',[x+dx-.04,-.34,z+2.0],[x+dx+.04,-.08,z+2.70],1)
  window('Right tall glazing',x+2.23,x+3.35,z+.22,z+1.97)
  bx('Tall window central mullion',[x+2.76,-.36,z+.22],[x+2.84,-.08,z+1.97],1)
  bx('Tall window upper divider',[x+2.23,-.36,z+1.47],[x+3.35,-.08,z+1.55],1)
  bx('Tall window sill',[x+2.16,-.43,z+.10],[x+3.43,-.08,z+.22],1)
  bx('Visible simplified exterior air conditioner',[x+.58,-.91,z+.16],[x+1.70,-.08,z+.89],1,'Visible exterior unit; not internal machinery, label/pipe/bracket details omitted')
  add('Dark circular fan impression',frontcyl(.28,.08,x+1.04,-.86,z+.52),4,'Observed round fan; no invented blades')
# Window/opening proportions normalized from photograph, nominal rather than measured.
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='NTHU Shi dormitory facade');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Photo-informed Shi dormitory front facade segment ONLY. Five bays, two visible levels only; artificial rear and ends, not whole building.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
