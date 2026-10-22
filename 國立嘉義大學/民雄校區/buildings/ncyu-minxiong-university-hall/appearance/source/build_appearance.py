"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='b9e1584fdcaba19e2aab8b6205612e98a793fcbd7ef86d9fa394503623482c9c'
PALETTE=[('neutral_unconfirmed_structure_roof_frames','#AAA79F'),('observed_front_white_main_wall_proxy','#D7D9D5'),('observed_front_brick_eaves_proxy','#B76B50')]
def classify(tri):
 v=tri;e=.0002;color=np.zeros(len(v),dtype=int);why=np.full(len(v),'neutral_unconfirmed_or_outside_documented_scope',dtype=object)
 white=(abs(v[:,:,1])<e).all(1)&(v[:,:,0]>=-6.25-e).all(1)&(v[:,:,0]<=43.75+e).all(1)&(v[:,:,2]>=29.8-e).all(1)&(v[:,:,2]<=50.1+e).all(1)
 brick=np.zeros(len(v),dtype=bool)
 for a,b in [((47.875,-4.75),(47.875,-21.375)),((47.875,-21.375),(32.25,-38.375)),((32.25,-38.375),(11.875,-38.375))]:
  d=np.array(b)-a;L=np.linalg.norm(d);q=v[:,:,:2]-a;u=(q*d).sum(2)/L;dist=abs(q[:,:,0]*d[1]-q[:,:,1]*d[0])/L
  brick|=(dist<e).all(1)&(u>=-e).all(1)&(u<=L+e).all(1)&(v[:,:,2]>=18.2-e).all(1)&(v[:,:,2]<=22.9+e).all(1)
 assert white.sum()==8 and brick.sum()==38 and not (white&brick).any()
 color[white]=1;why[white]='documented_front_main_white_wall_complete_faces'
 color[brick]=2;why[brick]='documented_front_brick_eaves_complete_faces'
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCYU Minxiong University Hall limited original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ncyu-minxiong-university-hall-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official NCYU front photo: all three EXIF dates 2019-02-10 12:08:04; second official photo undated. Uncalibrated approximate sRGB, not 2026 condition.','scope':'8 white front main-wall and 38 brick front-eaves complete faces only. 10.62507 mm2 difference between ideal rectangles and selected complete faces includes rejected cross-boundary faces and gaps without corresponding coplanar exterior surfaces. Glass, frames, gray top lip, horizontal roofs, sides and rear neutral. Original 2011 street-view geometry and 2019/undated colors span different years.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
