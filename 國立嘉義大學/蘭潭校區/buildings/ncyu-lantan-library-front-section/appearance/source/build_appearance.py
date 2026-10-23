"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='322571cbcfec4a2b2a51552089e0bc20ede425f622e062b4cab37513190dc4e6'
PALETTE=[('neutral_unconfirmed_structure','#AAA79F'),('observed_front_upper_cylinder_warm_white','#DDDCD2'),('observed_front_conical_roof_silver_grey','#969DA0')]
def classify(tri):
 v=tri;e=.0003;color=np.zeros(len(v),dtype=int);why=np.full(len(v),'neutral_unconfirmed_or_outside_documented_scope',dtype=object)
 cross=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);norm=cross/np.linalg.norm(cross,axis=1)[:,None]
 for cx in [-62,62]:
  for typ in [1,2]:
   union=np.zeros(len(v),bool)
   for i in range(32,64):
    theta=(i+.5)*2*np.pi/64;u=np.array([np.cos(theta),np.sin(theta)]);dot=(v[:,:,:2]-[cx,-4])@u
    if typ==1:
     m=(abs(dot-9*np.cos(np.pi/64))<e).all(1)&(v[:,:,2]>=47-e).all(1)&(v[:,:,2]<=60.2+e).all(1)&(abs(norm[:,2])<e)
    else:
     rad=9.5-(v[:,:,2]-60.2)*5/6
     m=(abs(dot-rad*np.cos(np.pi/64))<e).all(1)&(v[:,:,2]>=60.2-e).all(1)&(v[:,:,2]<=66.2+e).all(1)&(norm[:,2]>.1)&(norm[:,2]<.9)
    union|=m&(v[:,:,1]<=-4+e).all(1)
   assert not color[union].any();color[union]=typ;why[union]=f'observed_front_half_{cx}_{PALETTE[typ][0]}'
 assert np.bincount(color).tolist()==[6118,264,128]
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCYU Lantan Library Front Section limited original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ncyu-lantan-library-front-section-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official front photo capture date unknown; oblique photo EXIF Original/Digitized and XMP CreateDate 2018-05-30, Modify 2018-10-11. Uncalibrated opaque material proxies, not exact color or 2026 condition.','scope':'392 complete original triangles: front-half upper cylinder skin 264 warm-white faces and cone roofs 128 silver-grey faces; all 3 vertices on original 64-sided support planes, y<=-4. Rear halves, window holes, horizontal caps, ring bands, brick walls and central windows neutral. Original front section only, not whole building. No new geometry.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
