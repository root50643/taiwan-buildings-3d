"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='2c062e7e131e13c64ae9aa322ffe92769c2580043e9ad3f6124e6e21f11bc3f9'
PALETTE=[('neutral_unconfirmed_structure','#AAA79F'),('observed_central_glazing_back','#597078'),('observed_front_white_columns_beam','#DDDCD6')]
def classify(tri):
 v=tri;eps=.0002;color=np.zeros(len(v),dtype=int)
 regions=[]
 for x in [-11.2,-5.6,0,5.6,11.2]:
  for z in [3.4,7.8,12.2]:regions.append((1,-24.81,[(x-2.45)*1.2,(x+2.45)*1.2],[1.6+z*1.2,1.6+(z+1.85)*1.2]))
 for x in [-14,-8.4,-2.8,2.8,8.4,14]:regions.append((2,-29.61,[(x-.575)*1.2,(x+.575)*1.2],[4.36,20.8]))
 regions.append((2,-30.66,[-18,18],[19.72,21.16]))
 for mat,y,xr,zr in regions:
  m=(abs(v[:,:,1]-y)<eps).all(1)&(v[:,:,0]>=xr[0]-eps).all(1)&(v[:,:,0]<=xr[1]+eps).all(1)&(v[:,:,2]>=zr[0]-eps).all(1)&(v[:,:,2]<=zr[1]+eps).all(1)
  assert not (color[m]!=0).any();color[m]=mat
 why=np.full(len(v),'neutral_unconfirmed_or_outside_documented_scope',dtype=object);why[color==1]='central_window_backs';why[color==2]='front_column_and_name_beam_faces'
 assert np.bincount(color).tolist()==[7062,30,14]
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NPUST Yukang Memorial Library limited original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'npust-yukang-library-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'MOE official photo personally viewed; page date 2026-01-22, capture date unknown (no EXIF/XMP); uncalibrated material approximations.','scope':'Only 30 central recessed window back faces and 14 front column/name beam faces. Remaining 7062 faces neutral; gray walls, roof, rear, sides and unknown glazing unchanged. Modest front-central benefit only.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
