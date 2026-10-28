#!/usr/bin/env python3
"""Original bounded historical-photo model; not complete treatment facility or current survey."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':'tile','name':'Approximate salmon wall tile','hex':'#B69B85','evidence':'historical photos; no color calibration'}, {'id':'lower','name':'Warm light grey lower wall','hex':'#AAA99D','evidence':'visible two-tone tile field'}, {'id':'concrete','name':'Grey concrete cornice and window surrounds','hex':'#A5A79B','evidence':'visible projecting window caps and ring edges'}, {'id':'glass','name':'Dark opaque window panes','hex':'#454E46','evidence':'visible panes, no interior'}, {'id':'louver','name':'Dark green central louvers','hex':'#35574B','evidence':'visible wide central louver panel'}, {'id':'roof','name':'Neutral unseen roof infill','hex':'#B7B5A8','evidence':'unseen roof surface neutral'}, {'id':'base','name':'Display plinth','hex':'#B3B6AD','evidence':'authored support, not full landscape'}]
SCALE=7.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.45]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Photo-derived approximate proportion; no measured dimension'):add(name,box(a,b),mat,evidence)
def cy(name,cx,cy,z0,z1,r,mat,evidence):add(name,mf.Manifold.cylinder(z1-z0,r,r,96).translate([cx,cy,z0]),mat,evidence)
W,D,H=16.,10.,5.6
bx('Display base',[-1.5,-1.5,-.45],[W+1.5,D+1.5,0],6,'Authored support; retaining walls, grounds and underground tanks excluded')
bx('Neutral solid lower main envelope',[0,0,-.02],[W,D,2.0],1,'Visible lower grey tile; unseen rear/other short end neutral, not confirmed blank walls')
bx('Salmon upper envelope',[0,0,1.99],[W,D,H],0,'Four official photos show compact low rectangular building')
# Curved central upper facade and circular rooftop enclosure, radius/position estimated.
cy('Central curved upper wall',8,3.65,4.65,6.55,3.9,0,'Circular drum visible above central louvers; exact rear footprint unseen')
cy('Drum solid neutral top plane',8,3.65,6.48,6.56,3.75,5,'Roof interior unseen, solid neutral display infill, no invented equipment')
# Visible concrete coping ring and continuous lower band; panels are opaque tile, not holes.
ring=mf.Manifold.cylinder(.18,4.02,4.02,96)-mf.Manifold.cylinder(.25,3.76,3.76,96).translate([0,0,-.03])
add('Circular coping ring',ring.translate([8,3.65,6.55]),2,'Photo1-4 grey ring, simplified 96-sided cylinder')
ring=mf.Manifold.cylinder(.18,4.02,4.02,96)-mf.Manifold.cylinder(.25,3.76,3.76,96).translate([0,0,-.03])
add('Drum lower horizontal band',ring.translate([8,3.65,5.65]),2,'Visible solid drum with shallow rectangular panel relief')
for i in range(16):
 ang=2*math.pi*i/16
 s=box([3.76,-.10,5.75],[4.02,.10,6.58]).rotate([0,0,math.degrees(ang)]).translate([8,3.65,0])
 add(f'Drum shallow vertical divider {i+1}',s,2,'Sixteen evenly spaced display dividers inferred from visible rhythm; exact total unverified')
# Two flanking flat roof wings with stepped cornice, not full continuous slab across drum.
for lo,hi in [(0,5.8),(10.2,16)]:
 bx(f'Wing cornice lower {lo}',[lo-.16,-.16,4.85],[hi+.16,D+.16,5.03],2,'Grey horizontal lower fascia visible')
 bx(f'Wing cornice flared step {lo}',[lo-.30,-.30,5.23],[hi+.30,D+.30,5.48],0,'Stepped approximation of outward flaring cornice, not exact curved profile')
 bx(f'Wing top concrete coping {lo}',[lo-.55,-.55,5.48],[hi+.55,D+.55,5.66],2,'Wide flat overhanging cap visible')
 bx(f'Wing roof neutral infill {lo}',[lo-.30,-.30,5.65],[hi+.30,D+.30,5.69],5,'Unseen top infill neutral')
def front_window(label,x,z0=2.05,z1=4.35,w=1.65):
 bx(label+' pane',[x,-.06,z0],[x+w,.02,z1],3,'Visible front two windows per side; approximate positions')
 bx(label+' cap',[x-.23,-.30,z1],[x+w+.23,.04,z1+.24],2,'Projecting grey lintel in official photos')
 bx(label+' sill',[x-.23,-.30,z0-.20],[x+w+.23,.04,z0],2,'Projecting grey sill')
 bx(label+' transom',[x,-.11,2.75],[x+w,-.05,2.84],2,'Visible horizontal pane split, simplified')
for i,x in enumerate([.65,3.1,11.15,13.65]):front_window(f'Front window {i+1}',x)
# Observed left short end four windows, not mirrored to far end.
for i,y in enumerate([.9,3.15,5.4,7.65]):
 bx(f'Observed left end pane {i+1}',[-.06,y,2.05],[.02,y+1.15,4.35],3,'Four windows on same short end in photo1,2,4')
 bx(f'Observed left end cap {i+1}',[-.30,y-.22,4.35],[.04,y+1.37,4.59],2)
 bx(f'Observed left end sill {i+1}',[-.30,y-.22,1.85],[.04,y+1.37,2.05],2)
 bx(f'Observed left end transom {i+1}',[-.11,y,2.75],[-.05,y+1.15,2.84],2)
# Central louver field opaque, not service interior.
bx('Central dark green louver backing',[5.9,-.10,.45],[10.1,.02,4.7],4,'Broad central green louver panel visible; no interior reconstruction')
for i in range(5):bx(f'Louver vertical mullion {i+1}',[5.9+i*1.025,-.23,.45],[6.0+i*1.025,-.08,4.7],4,'Visible central panel divisions simplified')
for i in range(24):bx(f'Central simplified blade {i+1}',[5.9,-.19,.50+i*.17],[10.1,-.08,.57+i*.17],4,'24 relief rails for display, actual blade count unverified')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NUK laboratory wastewater main building historical exterior');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Historical-photo exterior approximation; unseen rear and far short side neutral; not underground treatment facility; not current/as-built; not trial printed'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
