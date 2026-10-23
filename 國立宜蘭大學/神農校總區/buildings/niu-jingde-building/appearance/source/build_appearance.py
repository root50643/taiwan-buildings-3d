"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='1621b5d9a863db687ba9b426bef0c7d014a9330138dbdb3a6858bdda71e359c4'
PALETTE=[('neutral_unconfirmed_structure','#AAA79F'),('observed_classroom_glazing_proxy','#586566')]
def regions():
 for floor in range(7):
  z=5+floor*9.3
  for x in [-48,-38,-28,-18,-8,2,12,22,32,42,51]:
   if (floor==5 and x>30) or (floor==6 and x>10) or (floor in [1,2,3,4] and x>25):continue
   for name,a,b in [('lower',0,2.3),('upper',3.3,5.9)]:yield f'floor{floor+1}_x{x}_{name}',x-3.6,x+3.6,z+a,z+b
def classify(tri):
 v=tri;e=2e-5;color=np.zeros(len(v),dtype=int);why=np.full(len(v),'neutral_unconfirmed_or_outside_documented_scope',dtype=object)
 normal=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);plane=(abs(v[:,:,1]+61.9)<e).all(1)&(normal[:,1]<-1e-8)
 for name,x0,x1,z0,z1 in regions():
  mask=plane&(v[:,:,0]>=x0-e).all(1)&(v[:,:,0]<=x1+e).all(1)&(v[:,:,2]>=z0-e).all(1)&(v[:,:,2]<=z1+e).all(1)
  assert not color[mask].any();color[mask]=1;why[mask]=name
 assert np.bincount(color).tolist()==[13876,230]
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NIU Jingde Building limited original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'niu-jingde-building-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Author original photos 1, 8, 12 actually viewed. Capture dates unknown; article published 2021 is not capture evidence. Uncalibrated opaque low-saturation glazing proxy; not present-day accuracy.','scope':'Only 230 complete original -Y classroom pane backing triangles in 57 bays, upper/lower panes. All opaque walls, mixed gray bands and white piers, reveals, other elevations, roof and courtyard slots stay neutral. No geometry changes.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
