#!/usr/bin/env python3
"""Independent core 3MF XML check against original STL and original-face material mask."""
import pathlib,argparse,zipfile,xml.etree.ElementTree as ET,json,numpy as np
from material_geometry import load_stl,load_materials,bijection
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args();root=a.out
with zipfile.ZipFile(root/'model.3mf')as z:
 assert set(z.namelist())=={'[Content_Types].xml','_rels/.rels','3D/3dmodel.model'}
 xml=ET.fromstring(z.read('3D/3dmodel.model'))
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};assert xml.attrib['unit']=='millimeter'
objects=xml.findall('m:resources/m:object',ns);groups=xml.findall('m:resources/m:basematerials',ns);assert len(objects)==len(groups)==1;o=objects[0];group=groups[0]
assert len(list(o))==1 and o.find('m:mesh',ns)is not None
vertices=o.findall('m:mesh/m:vertices/m:vertex',ns);triangles=o.findall('m:mesh/m:triangles/m:triangle',ns)
v=np.asarray([[float(x.attrib[k])for k in('x','y','z')]for x in vertices],np.float64);f=np.asarray([[int(x.attrib[k])for k in('v1','v2','v3')]for x in triangles]);source=load_stl(root/'model.stl')[2];ids=bijection(source,v[f]);assert np.array_equal(ids,np.arange(5874))
materials=load_materials(root);palette=json.loads((root/'parameters.json').read_text())['palette'];bases=group.findall('m:base',ns);assert len(bases)==3
for b,q in zip(bases,palette):assert b.attrib['displaycolor'].upper()==q['hex'].upper()+'FF' and b.attrib['name']==q['name']
for i,t in enumerate(triangles):
 pid=t.attrib.get('pid',o.attrib.get('pid'));assert pid==group.attrib['id'];p1=int(t.attrib.get('p1',o.attrib.get('pindex','0')));p2=int(t.attrib.get('p2',str(p1)));p3=int(t.attrib.get('p3',str(p1)));assert p1==p2==p3==int(materials[ids[i]])
items=xml.findall('m:build/m:item',ns);assert len(items)==1 and items[0].attrib['objectid']==o.attrib['id'];transform=items[0].attrib.get('transform','1 0 0 0 1 0 0 0 1 0 0 0');assert [float(x)for x in transform.split()]==[1,0,0,0,1,0,0,0,1,0,0,0]
report={'all_pass':True,'source':'Independent XML parser, unchanged original STL and public face mask; no generated mesh arrays used.','vertices':len(v),'triangles':len(f),'exact_float64_decimal_coordinate_identity':True,'original_triangle_order_and_winding_preserved':True,'all_material_resource_ids_and_three_property_ids_correct':True,'palette_names_and_colors_correct':True,'build_transform_identity':True,'texture_or_external_members':0}
(root/'qa/3mf-xml-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
