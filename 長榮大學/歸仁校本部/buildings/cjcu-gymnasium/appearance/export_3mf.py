#!/usr/bin/env python3
"""Core 3MF basematerials, exact original float32 coordinates and ordered triangles.
No library rewriter: decimal values round-trip exactly to each source IEEE float32.
"""
from pathlib import Path
import argparse,json,zipfile,xml.etree.ElementTree as ET
import numpy as np
HERE=Path(__file__).resolve().parent
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',NS)
def tag(n):return '{'+NS+'}'+n
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=HERE);a=p.parse_args();root=a.out
D=np.load(root/'mesh-data.npz');palette=json.loads((HERE/'palette.json').read_text());m=ET.Element(tag('model'),{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'zh-TW'})
ET.SubElement(m,tag('metadata'),{'name':'Title'}).text='CJCU gymnasium roof — non-photometric sheet-family illustration only'
r=ET.SubElement(m,tag('resources'));bm=ET.SubElement(r,tag('basematerials'),{'id':'1'})
for d in palette:ET.SubElement(bm,tag('base'),{'name':d['id'],'displaycolor':d['hex']+'FF'})
o=ET.SubElement(r,tag('object'),{'id':'2','type':'model','pid':'1','pindex':'0'});mesh=ET.SubElement(o,tag('mesh'));vs=ET.SubElement(mesh,tag('vertices'))
for v in D['vertices']:ET.SubElement(vs,tag('vertex'),dict(zip(('x','y','z'),[repr(float(x)) for x in v])))
ts=ET.SubElement(mesh,tag('triangles'))
for face,mi in zip(D['faces'],D['materials']):ET.SubElement(ts,tag('triangle'),{'v1':str(face[0]),'v2':str(face[1]),'v3':str(face[2]),'pid':'1','p1':str(mi),'p2':str(mi),'p3':str(mi)})
ET.SubElement(ET.SubElement(m,tag('build')),tag('item'),{'objectid':'2'})
files={'[Content_Types].xml':b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>', '_rels/.rels':b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>', '3D/3dmodel.model':ET.tostring(m,encoding='utf-8',xml_declaration=True)}
with zipfile.ZipFile(root/'cjcu-gymnasium-roof-illustration.3mf','w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name,b in files.items():
  zi=zipfile.ZipInfo(name,(1980,1,1,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16;z.writestr(zi,b)
print('Wrote core 3MF with exact decimal float32 vertices and basematerials')
