"""Deterministic core-3MF exchange from canonical mesh arrays; standard library only.
Four native separate-part files and one assembled appearance master. No tool mapping.
Edit geometry.json materials[*].srgb for an exchange-only palette edit, or PALETTE in
build_model.py before rebuilding all assets. Surface colors are not closed color volumes.
"""
from pathlib import Path
import hashlib,json,zipfile,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[1]
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';E.register_namespace('',NS)
def el(p,t,**a):return E.SubElement(p,'{'+NS+'}'+t,{k:str(v) for k,v in a.items()})
def model(title,palette):
 root=E.Element('{'+NS+'}model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'})
 el(root,'metadata',name='Title').text=title
 el(root,'metadata',name='Application').text='CCT bounded exterior appearance exchange'
 el(root,'metadata',name='Description').text='Approximate street-side gatehouse/name pylon; estimated rear and roof. Surface colors, no tool mapping. Physical print/fit unverified.'
 res=el(root,'resources');m=el(res,'basematerials',id=20)
 for p in palette:el(m,'base',name=p['id'],displaycolor=p['srgb']+'FF')
 return root,res
def add(res,i,p):
 ob=el(res,'object',id=i,type='model',name=p['id'],pid=20,pindex=0);mesh=el(ob,'mesh');vs=el(mesh,'vertices');fs=el(mesh,'triangles')
 for v in p['vertices']:el(vs,'vertex',**{k:format(x,'.17g') for k,x in zip('xyz',v)})
 for f,c in zip(p['triangles'],p['material_indices']):el(fs,'triangle',v1=f[0],v2=f[1],v3=f[2],pid=20,p1=c,p2=c,p3=c)
def write(path,root):
 files={'[Content_Types].xml':b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>', '_rels/.rels':b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>', '3D/3dmodel.model':E.tostring(root,encoding='utf-8',xml_declaration=True)}
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in files.items():
   item=zipfile.ZipInfo(name,(2026,10,19,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o644<<16;z.writestr(item,data)
def main():
 d=json.loads((R/'geometry.json').read_text());(R/'appearance').mkdir(exist_ok=True);(R/'appearance/parts').mkdir(exist_ok=True)
 root,res=model('CCT ASSEMBLED appearance master - not a print layout',d['materials'])
 for i,p in enumerate(d['parts'],1):
  add(res,i,p);single,rs=model('CCT '+p['id']+' native orientation; surface colors only',d['materials']);add(rs,i,p);el(el(single,'build'),'item',objectid=i);write(R/'appearance/parts'/(p['id']+'.3mf'),single)
 group=el(res,'object',id=100,type='model',name='CCT four-part assembled appearance');cs=el(group,'components')
 for i,p in enumerate(d['parts'],1):el(cs,'component',objectid=i,transform=' '.join(format(p['assembly_transform'][j][k],'.17g') for k in range(4) for j in range(3)))
 el(el(root,'build'),'item',objectid=100);write(R/'appearance/cct-gate-ASSEMBLED.3mf',root)
 print(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'appearance').rglob('*.3mf'))},indent=2))
if __name__=='__main__':main()
