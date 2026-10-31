#!/usr/bin/env python3
"""Historical Zhen Wu pavilion: editable multi-photo interpretation, not a measured replica."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('roof','Warm pale roof','#C9C4AE','Faded archival color photographs; approximate uncalibrated palette'),
('structure','Gray concrete supports','#8A8980','Archival photo tones, no material laboratory identification'),
('cap','Dark ribbed top cap','#676A62','Visible dark top of central pillar; purpose and section not confirmed'),
('base','Authored display base','#AAA79B','Manufacturing base, not actual pool or terrain')]]
SCALE=10.0
# Nominal proportion units; all configurable, NOT surveyed metres.
P={'outer_radius':5.8,'oculus_radius':2.65,'support_radius':3.65,'roof_bottom':3.75,'roof_thickness':.22,'post_width':.68,'post_depth':.52,'sector_count':4,'ribs_per_gap':6,'pillar_height':5.25,'cap_radius':.48,'cap_height':.65}
(ROOT/'parameters.json').write_text(json.dumps(P,indent=2))
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.4]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=1,evidence='Photo-proportional interpretation; not a measured dimension'):add(name,box(a,b),mat,evidence)
def sector(ri,ro,a,b,z,h):
 angles=np.linspace(math.radians(a),math.radians(b),max(3,int(b-a)+1))
 pts=[[ro*math.cos(t),ro*math.sin(t)] for t in angles]+[[ri*math.cos(t),ri*math.sin(t)]for t in angles[::-1]]
 return mf.CrossSection([pts]).extrude(h).translate([0,0,z])
add('Author circular footing',mf.Manifold.cylinder(.4,6.15,6.15,192).translate([0,0,-.4]),3,'Authored connected display support, not real stairs, pool or terrain')
# Four solid sectors alternate with four open radial rib sectors, inferred across095/096/097.
for i in range(4):
 c=-90+90*i
 add(f'Solid annular roof sector {i+1}',sector(P['oculus_radius'],P['outer_radius'],c-22.5,c+22.5,P['roof_bottom'],P['roof_thickness']),0,'Four solid / four open sectors inferred from multiple built photographs; excludes unbuilt upturned design')
 # Inner ring is continuous around clear open oculus; does not cap opening.
 add(f'Inner connecting ring quarter {i+1}',sector(2.65,2.93,c-22.6,c+67.6,3.58,.40),1,'Visible continuous inner-ring support around open sky hole; nominal thickness')
 for j in range(P['ribs_per_gap']):
  a=c+22.5+(j+.5)*45/P['ribs_per_gap'];r0=2.88;r1=6.08
  q=box([r0,-.065,3.77],[r1,.065,3.99]).rotate([0,0,a])
  add(f'Open radial rib {i+1}-{j+1}',q,1,'Approximately six ribs per visible gap; evenly spaced normalization, not measured spacing')
for i in range(8):
 a=-90-22.5+45*i;r=P['support_radius']
 q=box([r-P['post_depth']/2,-P['post_width']/2,-.05],[r+P['post_depth']/2,P['post_width']/2,3.80]).rotate([0,0,a])
 add(f'Ring rectangular post {i+1}',q,1,'Eight rectangular posts inferred from multi-angle photos; exact sections and equal spacing normalized')
 # A short radial beam connects post to inner ring and carries adjacent slabs.
 q=box([2.80,-.20,3.48],[r+.26,.20,3.80]).rotate([0,0,a])
 add(f'Post head inward beam {i+1}',q,1,'Visible dark horizontal heads; nominal support depth')
add('Central tall pillar',mf.Manifold.cylinder(P['pillar_height'],.19,.19,48).translate([0,0,-.04]),1,'Central isolated high pillar visible across historical views; near-circular section approximate, function unspecified')
add('Central expanded cap',mf.Manifold.cylinder(P['cap_height'],P['cap_radius'],P['cap_radius'],64).translate([0,0,5.17]),2,'Dark enlarged vertically ribbed top; near-circular plan is nominal approximation, not proven section')
for j in range(24):
 a=j*360/24
 add(f'Cap simplified vertical ridge {j+1}',box([.455,-.022,5.17],[.50,.022,5.82]).rotate([0,0,a]),2,'Simplified representative vertical texture; count is authored, not surveyed')
# Pool, chairs, name marker, staircase, landscape, vegetation and all unbuilt schematic features omitted.
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='NYCU Zhen Wu historical pavilion');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Historical photograph-informed ring-roof pavilion body; no landscape, stairs, furniture or current-condition claim.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
