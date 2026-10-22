"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='299656bf3e4e9e65d94a0b4ace96512a289698820cc020f28dca4207076ba5da'
PALETTE=[('neutral_unconfirmed_structure','#AAA79F'),('observed_lake_facing_brick_frame_proxy','#B7866D'),('observed_low_wing_fascia_front_proxy','#424A4D')]
DOMAINS=[('brick_top',16,-63,63,97.7,101,1),('brick_cap',14.5,-65,65,101,103,1),('brick_left',14.5,-64.25,-61.75,38,103,1),('brick_right',14.5,61.75,64.25,38,103,1),('low_fascia',-61,-66,66,35,37.2,2)]
def classify(tri):
 v=tri;e=.0002;color=np.zeros(len(v),dtype=int);why=np.full(len(v),'neutral_unconfirmed_or_outside_documented_scope',dtype=object)
 cross=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);norm=cross/np.linalg.norm(cross,axis=1)[:,None]
 for name,y,x0,x1,z0,z1,c in DOMAINS:
  m=(abs(v[:,:,1]-y)<e).all(1)&(v[:,:,0]>=x0-e).all(1)&(v[:,:,0]<=x1+e).all(1)&(v[:,:,2]>=z0-e).all(1)&(v[:,:,2]<=z1+e).all(1)&(norm[:,1]<-.99)
  assert not color[m].any();color[m]=c;why[m]='documented_complete_front_faces_'+name
 assert np.bincount(color).tolist()==[8652,12,2]
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU Innovation Incubation Center limited original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthu-innovation-incubation-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Bioarch completed-work photos: capture dates unknown. EXIF dates absent. XMP toolkit 2012 is software version, project 2011–2016 and URL 2024/11 are not capture dates. Uncalibrated sRGB, not current-condition survey.','scope':'14 complete lake-facing original faces only: 12 brick frame fronts and 2 low-wing fascia fronts, 1263.87546 mm2. Incomplete frame selection is intentional; glazing, colored fins, planted roof, horizontal eaves, side/rear and all other surfaces remain neutral. Original approximate geometry unchanged.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
