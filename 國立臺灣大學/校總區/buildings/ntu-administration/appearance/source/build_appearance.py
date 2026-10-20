"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='80c6ce47e2253100375bc2cd1b82ff0c539daf10016e8ea5074a026f29247e69'
PALETTE=[('neutral_unseen','#AAA79F'),('redorange_brick','#B16F52'),('pale_warm_gray_stone','#BFC0B4'),('pale_bluegray_glazing','#809A9D'),('charcoal_roof','#505653'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_side_rear_and_roof_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0002)&(hi[:,2]<=b+.0002)
 paint(np.all(abs(t[:,:,1]+15.5)<.0002,axis=1)&zz(4,28.8),1,'source_front_wing_brick_field')
 paint(np.all(abs(t[:,:,1]+21.5)<.0002,axis=1)&zz(3,29.8),1,'source_projected_center_brick_field')
 for x in [-62,-54,-46,-38,38,46,54,62]:
  scope=(lo[:,0]>=x-2.2502)&(hi[:,0]<=x+2.2502)&(lo[:,1]>=-15.5002)&(hi[:,1]<=-14.7498)
  for z,h in [(5,8),(17,8)]:
   paint(scope&zz(z,z+h),2,'existing_window_returns_pale_stone_no_new_frame_geometry')
   paint(scope&np.all(abs(t[:,:,1]+14.75)<.0002,axis=1)&zz(z,z+h),3,'existing_wing_window_back_bluegray')
 for x in [-19,19]:
  scope=(lo[:,0]>=x-2.7502)&(hi[:,0]<=x+2.7502)&(lo[:,1]>=-21.5002)&(hi[:,1]<=-20.6498)
  for z in [5,17]:
   paint(scope&zz(z,z+8),2,'existing_center_flanking_window_returns_pale')
   paint(scope&np.all(abs(t[:,:,1]+20.65)<.0002,axis=1)&zz(z,z+8),3,'existing_center_flanking_window_back_bluegray')
 for x in [-11,-7,7,11]:
  paint((lo[:,0]>=x-1.3502)&(hi[:,0]<=x+1.3502)&(lo[:,1]>=-23.3502)&(hi[:,1]<=-20.6498)&zz(4,26),2,'registered_four_existing_columns_pale_stone')
  paint((lo[:,0]>=x-1.8002)&(hi[:,0]<=x+1.8002)&(lo[:,1]>=-23.8002)&(hi[:,1]<=-20.1998)&(zz(3.2,4.4)|zz(25,26.1)),2,'existing_simplified_capitals_and_column_bases_pale')
 paint((lo[:,0]>=-13.5002)&(hi[:,0]<=13.5002)&(lo[:,1]>=-25.0002)&(hi[:,1]<=-20.9998)&zz(26,27.7),2,'existing_portico_entablature_pale_stone')
 paint((hi[:,1]<=-15.9998)&(zz(3,4)|zz(14,15)),2,'existing_front_bands_pale_proxy_not_added_stone_panels')
 paint((hi[:,1]<=-23.3498)&zz(2.8,4.9)&(lo[:,0]>=-14.5002)&(hi[:,0]<=14.5002),2,'existing_front_steps_gray_stone')
 paint((n[:,2]>.05)&(n[:,1]<-.05)&(lo[:,2]>=27.9998)&(hi[:,2]<=35.0002),4,'registered_visible_front_roof_slopes_dark_gray')
 paint(hi[:,2]<=3.0001,5,'display_base_not_landscape')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Administration original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'admin-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NTU administration photograph credited to Chen Chao-lun; watermark 2014 and embedded DateTimeOriginal 2014-07-28 16:15:13, timezone unprovided and not independently verified approximations, not measured material swatches','scope':'Registered front brick, four pale columns and capitals, pale recess returns and grayblue glazing; unseen rear neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
