"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='69696f3dc9233460a8d0410508628204b63c0e8b548848c4c161b7cd153a5cd3'
PALETTE=[('neutral_unseen','#AAA79F'),('rose_beige_wall','#BD9F92'),('offwhite_ribs_and_rim','#CDCEC1'),('dark_bluegray_glazing','#4C626B'),('gray_window_bands_and_plinth','#8E9694'),('display_plinth','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None];xy=t[:,:,:2]-np.array([0,-3]);r=np.linalg.norm(xy,axis=2);ang=np.degrees(np.arctan2(c[:,1]+3,c[:,0]));front=(ang>=-178)&(ang<=14)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_roof_rear_and_joining_stub_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00015)&(hi[:,2]<=b+.00015)
 paint(front&(r.min(1)>=43.98)&(r.max(1)<=44.0002)&zz(5.2,65.8),1,'registered_curved_wall_and_solid_central_sign_panel_rose')
 for a in [-168,-151,-134,-117,-63,-46,-29,-12,5]:
  sector=(ang>=a-6.501)&(ang<=a+6.501)&(r.min(1)>=41.68)&(r.max(1)<=44.0002)
  paint(sector&zz(7,62),4,'existing_recess_returns_and_horizontal_bands_gray')
  for z,h in [(7,13),(21.2,12.8),(35.2,12.8),(49.2,12.8)]:paint(sector&(r.max(1)<=41.7002)&zz(z,z+h),3,'existing_curved_recess_back_glazing')
 # Coordinate frames register each original structural rib, never fill the central wall with glass.
 for a in [-178,-160,-143,-126,-109,-71,-54,-37,-20,-3,14]:
  ar=np.radians(a);u=np.array([np.cos(ar),np.sin(ar)]);v=np.array([-np.sin(ar),np.cos(ar)]);rad=xy@u;side=xy@v
  paint((rad.min(1)>=42.6498)&(rad.max(1)<=46.1502)&(np.max(abs(side),axis=1)<=1.1002)&zz(4.8,63.8),2,'existing_tall_structural_rib_offwhite')
  paint((rad.min(1)>=41.7498)&(rad.max(1)<=47.0502)&(np.max(abs(side),axis=1)<=1.7002)&zz(62.8,66.6),2,'existing_flared_capital_offwhite')
 paint(front&(r.min(1)>=47.17)&(r.max(1)<=47.2002)&(abs(n[:,2])<.1)&zz(65.8,69),2,'registered_round_rim_vertical_surface_offwhite')
 paint(front&(r.max(1)<=48.5002)&zz(3,5.2),4,'registered_low_curved_plinth_gray')
 # Visible service tower faces only; rear is not inferred from the side photo.
 tower=(lo[:,0]>=-42.0002)&(hi[:,0]<=-23.9998)&(lo[:,1]>=15.9998)&(hi[:,1]<=42.0002)&zz(3,77.8)
 paint(tower&((np.all(abs(t[:,:,0]+42)<.0002,axis=1))|(np.all(abs(t[:,:,1]-16)<.0002,axis=1))),1,'registered_visible_service_tower_rose')
 for z in [12,28,44,60]:paint(np.all(abs(t[:,:,0]+40.85)<.0002,axis=1)&(lo[:,1]>=23.9998)&(hi[:,1]<=34.0002)&zz(z,z+10),3,'existing_service_tower_recess_back_glazing')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NPTU Music Hall Rotunda Segment original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nptu-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NPTU Music Hall 1 and 2 photographs credited to General Affairs Office; embedded DateTimeOriginal 2019-07-19 and 2016-10-30, timezone unprovided and not independently verified approximations, not measured material swatches','scope':'Registered rotunda front, pale ribs and solid rose central wall; visible service tower only; roof and rear neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
