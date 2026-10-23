"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='50faf968b17ed490a3a7cd56b7ed0264b9c6c0cbfaa45131219ae63e38968dfd'
PALETTE=[('neutral_unconfirmed_structure','#AAA79F'),('observed_opaque_green_spandrel','#78A691'),('observed_dark_glazing_back','#3E514B')]
def classify(tri):
 sel=json.loads((A/'source/source-selection.json').read_text());v=tri/sel['scale'];eps=.0002;color=np.zeros(len(v),dtype=int);why=np.full(len(v),'neutral_unconfirmed_or_excluded',dtype=object)
 normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);areas=np.linalg.norm(normals,axis=1)/2;audit=[]
 for g in sel['groups']:
  x0,x1,z0,z1=g['bounds_unscaled_xz'];yy=g['plane_unscaled_y']
  m=(abs(v[:,:,1]-yy)<eps).all(1)&(v[:,:,0]>=x0-eps).all(1)&(v[:,:,0]<=x1+eps).all(1)&(v[:,:,2]>=z0-eps).all(1)&(v[:,:,2]<=z1+eps).all(1)&(normals[:,1]/np.linalg.norm(normals,axis=1)<-.99999)
  ids=np.flatnonzero(m).tolist();assert ids==g['ids'];assert not (color[m]!=0).any();color[m]=g['material'];why[m]=g['name'];area=float(areas[m].sum());assert abs(area-g['area_mm2'])<1e-8;audit.append(dict(name=g['name'],material=g['material'],ids=ids,count=len(ids),area_mm2=area))
 assert np.bincount(color).tolist()==[5495,120,23]
 (A/'qa/material-boundaries.json').write_text(json.dumps(dict(method='all three vertices finite plane bounds and actual cross-product normal',counts=np.bincount(color).tolist(),groups=audit),indent=2)+'\n')
 return color,why

def writezip(path,files):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in files:
   info=zipfile.ZipInfo(name,(2026,10,20,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data)
def main():
 (A/'qa').mkdir(exist_ok=True);(A/'previews').mkdir(exist_ok=True)
 raw=(R/'model.stl').read_bytes();assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
 n=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*n
 tri=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)],dtype=np.float64).reshape(n,3,3)
 v,inv=np.unique(tri.reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
 colors,why=classify(tri);assert set(colors)==set(range(len(PALETTE)))
 # .17g exactly roundtrips every source float32 value as float64.
 ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';E.register_namespace('',ns)
 model=E.Element('{'+ns+'}model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'});res=E.SubElement(model,'resources');bm=E.SubElement(res,'basematerials',{'id':'20'})
 for name,color in PALETTE:E.SubElement(bm,'base',{'name':name,'displaycolor':color+'FF'})
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'HWAI M Second Dormitory limited original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'hwai-dormitory-m-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official school PDF page 42 embedded original photo; 2019-03-06 is presentation export, not capture date. Both green spandrel and dark glazing are uncalibrated opaque proxies.','scope':'Only 120 green spandrel and 23 dark backing triangles in 19 source-supported front planes; 5495 neutral. No red brick, frames, flanking or side windows, rear or roof recoloring. Original geometry and coarse window subdivisions unchanged.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
