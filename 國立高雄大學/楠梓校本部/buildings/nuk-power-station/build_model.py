#!/usr/bin/env python3
"""NUK central electrical station: bounded historical-photo exterior approximation.
Unobserved rear and other short end are neutral, not reconstructed. No source images embedded.
All dimensions are estimated design metres, not measured/as-built values.
"""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':'wall','name':'Approximate warm ivory tile','hex':'#C7BBA3','evidence':'official historical photos, uncalibrated'}, {'id':'glass','name':'Opaque muted window glass','hex':'#727C7A','evidence':'visible upper glazing; no transparency/interior'}, {'id':'frame','name':'Grey window frames and fascia','hex':'#686D6A','evidence':'historical photographs'}, {'id':'vent','name':'Recessed grey louvers','hex':'#77766A','evidence':'observed low front vents; simplified slats'}, {'id':'roof','name':'Neutral roof plane','hex':'#A7A99D','evidence':'NLSC orthophoto roof outline; no equipment reconstruction'}, {'id':'base','name':'Display support','hex':'#C6C8C2','evidence':'authored support, not real terrain'}]
SCALE=5.5
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.55]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Authored simplified geometry; approximate photo proportions'):add(name,box(a,b),mat,evidence)
L,D,H=31.,13.5,10.7
bx('Display base',[-2,-2,-.55],[L+2,D+2,0],5,'Artificial support, not survey terrain')
wall=box([0,0,-.02],[L,D,H])
# Four visible groups of three windows/recesses; count is a conservative visible pattern,
# not a claim to an exhaustive window count beyond crop/tree occlusion.
xs=[2.25+g*7.4+j*1.72 for g in range(4) for j in range(3)]
for x in xs:wall=wall-box([x-.56,-.04,1.0],[x+.56,.30,5.0])
add('Main closed exterior shell, unknown sides neutral',wall,0,'Rectangular roof confirmed; three facade sides not fully documented; not an interior building model')
for i,x in enumerate(xs):
 bx(f'Front upper frame {i+1}',[x-.64,-.14,8.15],[x+.64,.03,9.43],2,'Twelve visible upper windows in four groups; full-length count not proven')
 bx(f'Front upper opaque glazing {i+1}',[x-.52,-.175,8.27],[x+.52,-.135,9.31],1)
 for level in [1.08,4.35]:
  bx(f'Front recess vent {i+1} {level}',[x-.52,.23,level],[x+.52,.31,level+.57],3,'Visible upper/lower louver panels inside shallow vertical recess')
  for k in range(3):bx(f'Vent slat {i+1} {level} {k}',[x-.52,.17,level+.07+k*.17],[x+.52,.25,level+.12+k*.17],2,'Slat count simplified for miniature, not literal actual count')
# One observed short end: two paired high windows; unknown other end deliberately plain.
for i,y in enumerate([3.0,10.0]):
 bx(f'Observed short end paired frame {i+1}',[-.14,y-1.16,8.35],[.03,y+1.16,9.33],2,'Photo1 shows two high paired windows on a short end; mapped local end is schematic')
 bx(f'Observed short end opaque glass {i+1}',[-.18,y-1.04,8.47],[-.135,y+1.04,9.21],1)
 bx(f'Paired divider {i+1}',[-.21,y-.055,8.40],[-.13,y+.055,9.28],2)
# Main projecting roof line and modest parapet match the silhouette, no invented roof equipment.
bx('Projecting dark roof cornice',[-.40,-.40,10.48],[L+.40,D+.40,10.72],2,'Continuous dark projecting strip below parapet visible in official photos')
bx('Neutral flat roof',[-.05,-.05,10.68],[L+.05,D+.05,10.87],4,'Roof footprint from NLSC public orthophoto, details not reconstructed')
for name,a,b in [('front',[-.1,-.1,10.68],[L+.1,.20,11.38]),('rear',[-.1,D-.20,10.68],[L+.1,D+.1,11.38]),('left',[-.1,-.1,10.68],[.20,D+.1,11.38]),('right',[L-.20,-.1,10.68],[L+.1,D+.1,11.38])]:bx('Parapet '+name,a,b,0,'Rectangular parapet outline; height estimated from photos')
# Fine horizontal construction seams shown only on known face, exaggerated slightly to remain visible.
for z in [1.65,6.75]:bx(f'Front horizontal seam {z}',[0,-.045,z],[L,.01,z+.025],2,'Photographic tile/control-joint line; not a measured structural floor level')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NUK electrical station bounded exterior');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Historical-photo bounded exterior approximation; neutral unknown rear and one short end; not full reconstruction; not trial printed'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
