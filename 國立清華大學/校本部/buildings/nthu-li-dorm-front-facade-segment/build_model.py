#!/usr/bin/env python3
"""NTHU Li dormitory visible-front segment. Dimensions are photo proportions, not surveyed."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('wall','Grey white tiled wall','#B9BDB8','Official June2026 photo; tile grid omitted'),
('frame','Pale window frames','#D4D8C9','Visible window/door frames, no exact color calibration'),
('glass','Muted window shadow','#566763','Curtains and reflections abstracted to neutral gray green'),
('screen','Brown circular screen','#765444','Visible brown round-hole screens; holes reduced'),
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
bx('Authored common segment footing',[-13.5,-2.6,-.6],[13.1,1.6,-.15],5,'Artificial common support, not surveyed site or foundation')
bx('Left five-bay shallow wall',[-13,-.12,-.2],[2,1.35,12.65],0,'Observed four-level five-bay wing only, left continuation clipped')
bx('Central entry screen backing',[2,-.12,-.2],[4.9,1.35,14.20],0,'Three screen panels visible, nominal height normalized')
bx('Right higher window tower',[4.9,-.40,-.2],[12.5,1.35,15.60],0,'Visible four-level taller mass, depth artificial shallow segment')
# Neutral rear overlay does not claim actual back.
for name,x0,x1,h in [('left',-13,2,12.65),('center',2,4.9,14.20),('right',4.9,12.5,15.60)]:
 bx('Artificial rear '+name,[x0,1.28,-.18],[x1,1.43,h],7,'Flat artificial cut backing; unseen real rear excluded')
def window(name,x0,x1,z0,z1,y,n):
 bx(name+' dark pane',[x0,y-.03,z0],[x1,y+.08,z1],2)
 for x in np.linspace(x0,x1,n+1):bx(name+' vertical frame',[x-.045,y-.13,z0-.04],[x+.045,y+.09,z1+.04],1)
 for z in [z0,z0+(z1-z0)*.49,z1]:bx(name+' horizontal frame',[x0-.045,y-.13,z-.045],[x1+.045,y+.09,z+.045],1)
 # shallow projecting sill
 bx(name+' sill',[x0-.10,y-.19,z0-.10],[x1+.10,y+.09,z0-.015],1)
for floor in range(4):
 z=.65+3.0*floor
 for bay in range(5):
  x=-12.7+3*bay;window('Wing window',x,x+2.40,z,z+1.78,-.17,4)
  # Observed external window air conditioning; simplified body and dark fan disk.
  bx('External AC simple body',[x+.30,-.87,z-.03],[x+1.07,-.24,z+.52],1,'Each observed window group has exterior AC; bracket/pipe details omitted')
  add('AC fan disk',frontcyl(.20,.035,x+.59,-.85,z+.245),4,'Round dark fan impression, no blades/engineering details')
for floor in range(4):
 z=.65+3.65*floor
 window('Tower broad window',5.30,10.20,z,z+2.15,-.45,3)
 window('Tower narrow window',10.85,12.45,z,z+2.15,-.45,2)
 bx('Tower projecting window skirt',[5.1,-.60,z-.45],[12.5,-.30,z-.14],0,'Visible shallow projecting window skirt, no unknown side extension')
# Three distinctive circular-hole screens, authentic hole TYPE retained; count deliberately reduced.
for low,high in [(3.75,6.25),(6.80,9.72),(10.27,13.25)]:
 bx('Screen dark inner recess',[2.25,-.20,low],[4.65,-.08,high],4,'Dark background of circular screen, not reconstructed interior')
 panel=box([2.25,-.42,low],[4.65,-.10,high]);holes=[]
 for row in range(7):
  for col in range(6):
   x=2.46+col*.38+(row%2)*.06;z=low+.20+row*(high-low-.40)/6
   holes.append(frontcyl(.135,.50,x,-.02,z,20))
 panel=panel-mf.Manifold.batch_boolean(holes,mf.OpType.Add)
 add('Brown circular-hole screen',panel,3,'Visible circular perforation type; reduced six columns by seven staggered rows per panel, not actual count')
# Entry below lowest panel; blank fascia is observed, label not fabricated.
window('Entry dark double door',2.35,4.58,.28,3.25,-.18,2)
bx('Entry shallow canopy slab',[1.65,-1.42,3.25],[4.95,.18,3.48],0)
bx('Entry blank sign fascia',[1.65,-1.46,3.32],[4.95,-1.25,4.12],0,'Blank fascia; historical text omitted, not a fictional inscription')
bx('Entry right canopy return',[4.66,-1.42,.12],[4.95,.18,3.50],0,'Visible right canopy pier, depth and support thickness normalized')
for k in range(3):bx('Entry simplified step',[2.15,-2.25+k*.32,-.2],[4.68,-.30,.05+k*.11],5,'Three visible riser impressions; exact terrain and accessibility ramp excluded')
bx('Blank service center plaque',[6.55,-.64,3.18],[9.20,-.44,4.02],6,'Public visible sign retained as blank panel; no letters/person data')
# No speculative upper roof, unseen side wings, whole-building plan, wiring, names or furniture.
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='NTHU Li dormitory facade');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Photo-informed Li dormitory front facade segment ONLY. Five-bay four-level wing, three round-hole screens and taller four-level tower; shallow artificial rear, no whole-building claim.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
