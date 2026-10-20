"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='0b18e54781614cffbf69d794bbdca1c4dd237a918dd9a2ef5b8bea879e638cf2'
PALETTE=[('neutral_unseen','#AAA79F'),('red_brick','#AC765F'),('pale_gallery_and_gable','#CBC9B8'),('warm_gray_stone','#AAA692'),('restrained_gable_frame_gray','#7B7C74'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_short_ends_and_roof_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 paint(plane(1,19.5)&zz(3,38.9),1,'registered_rear_long_brick_field_front_unseparated_boundary_neutral')
 for side in [-1,1]:
  xs=[-64,-54,-44,-34,-24,24,34,44,54,64] if side<0 else range(-64,65,10)
  for x in xs:
   m=(lo[:,0]>=x-3.65025)&(hi[:,0]<=x+3.65025)&(lo[:,1]>=(-19.50025 if side<0 else 16.09975))&(hi[:,1]<=(-16.09975 if side<0 else 19.50025))
   paint(m&(zz(7,19)|zz(24,35)),2,'existing_open_gallery_recess_returns_and_back_pale_not_glazing')
   paint((lo[:,0]>=x-3.70025)&(hi[:,0]<=x+3.70025)&(lo[:,1]>=side*19.5-.60025)&(hi[:,1]<=side*19.5+.60025)&zz(21,23.3),3,'existing_long_gallery_parapet_band_stone_proxy')
 for x in [-16,-9.6,-3.2,3.2,9.6,16]:
  paint((lo[:,0]>=x-1.80025)&(hi[:,0]<=x+1.80025)&(lo[:,1]>=-28.80025)&(hi[:,1]<=-25.19975)&zz(6,36.9),3,'six_existing_front_tuscan_columns_stone')
 paint((lo[:,0]>=-19.50025)&(hi[:,0]<=19.50025)&(lo[:,1]>=-31.00025)&(hi[:,1]<=-14.99975)&zz(3,6.5),3,'existing_entry_plinth_and_steps_stone')
 paint((lo[:,0]>=-19.00025)&(hi[:,0]<=19.00025)&(lo[:,1]>=-31.00025)&(hi[:,1]<=-18.99975)&zz(36.5,39.5),3,'existing_front_portico_entablature_stone')
 paint(plane(1,-31)&zz(39,49),4,'existing_outer_pediment_face_restrained_gray_not_asserted_timber')
 paint(plane(1,-31.85)&zz(40.5,46.5),2,'existing_inner_pediment_face_pale')
 for x in [-44,36]:
  paint((lo[:,0]>=x-5.00025)&(hi[:,0]<=x+5.00025)&(lo[:,1]>=19.14975)&(hi[:,1]<=23.50025)&zz(5,23),3,'registered_rear_secondary_balcony_and_supports_stone_proxy')
 paint((plane(1,-20.5)|plane(1,20.5))&zz(38,40),3,'existing_front_and_rear_eave_band_vertical_edge_stone')
 paint(hi[:,2]<=3.0001,5,'display_base_not_source_stone_plinth')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU History Department original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'history-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NCKU images 3458, 3464 and 3472 posted 2025-02-05; capture date unverified','scope':'Registered long front and rear only; both short ends neutral because source-end orientation not independently established. Gallery backs are pale wall proxies, not glazing.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
