"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='d9be3845ba167180ee696df279ba0bb907709bade622a10142d81fc904649ad2'
PALETTE=[('neutral_unseen','#AAA79F'),('orange_brick','#AF785C'),('warm_ochre_stone','#B5A384'),('cream_corridor_proxy','#C7C1AA'),('redbrown_recess_returns','#875E4E'),('muted_glazing_proxy','#657976'),('gray_platform','#999A91'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_roof_west_and_rear_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 paint((plane(1,-61.9)|plane(1,-62))&(lo[:,0]>=-32.50025)&(hi[:,0]<=32.50025)&zz(24.2,63.7),1,'registered_front_brick_field_and_gable')
 paint(plane(0,30.5)&zz(25,45.9),1,'registered_east_upper_brick_field')
 for x in [-19,-4.4,4.4,19]:
  mask=(lo[:,0]>=x-2.65025)&(hi[:,0]<=x+2.65025)&(lo[:,1]>=-62.00025)&(hi[:,1]<=-60.99975)&zz(29,40.4)
  paint(mask,4,'existing_front_window_returns_redbrown_proxy');paint(mask&plane(1,-61),5,'existing_front_window_recess_back_muted_glazing')
 for y in [-42,-20,2,24,46]:
  mask=(lo[:,1]>=y-3.00025)&(hi[:,1]<=y+3.00025)&(lo[:,0]>=29.84975)&(hi[:,0]<=30.50025)&zz(30,40)
  paint(mask,4,'existing_east_clerestory_returns_redbrown');paint(mask&plane(0,29.85),5,'east_clerestory_recess_back_glazing')
 for x in [-4.4,4.4]:
  paint((lo[:,0]>=x-4.20025)&(hi[:,0]<=x+4.20025)&(lo[:,1]>=-62.90025)&(hi[:,1]<=-61.49975)&zz(37,44),2,'existing_raised_paired_arch_moulding_ochre')
 oculus=(lo[:,0]>=-3.50025)&(hi[:,0]<=3.50025)&(lo[:,1]>=-62.00025)&(hi[:,1]<=-61.19975)&zz(46.5,53.5)
 paint(oculus,2,'existing_oculus_return_ochre');paint(oculus&plane(1,-61.2),5,'existing_oculus_back_glazing_proxy')
 for x in range(-27,28,6):
  z=45.7+18*(1-abs(x)/32.5)-2.1
  paint((lo[:,0]>=x-.70025)&(hi[:,0]<=x+.70025)&(lo[:,1]>=-62.80025)&(hi[:,1]<=-61.19975)&zz(z,z+2.2),2,'existing_gable_dentil_ochre')
 for x in [-33,-11,11,33]:
  paint((lo[:,0]>=x-2.75025)&(hi[:,0]<=x+2.75025)&(lo[:,1]>=-71.75025)&(hi[:,1]<=-66.24975)&zz(4.4,22.6),2,'four_existing_front_stone_columns_not_timber')
 paint(plane(1,-72.5)&zz(22.2,24.2),2,'existing_front_entablature_vertical_edge_stone')
 paint((lo[:,0]>=45.59975)&(hi[:,0]<=48.00025)&zz(5,21),3,'east_corridor_recess_and_outer_wall_cream_proxy_no_fake_timber_posts')
 paint((lo[:,0]>=-39.00025)&(hi[:,0]<=39.00025)&(lo[:,1]>=-72.00025)&(hi[:,1]<=-55.99975)&zz(3,4.5),6,'existing_front_platform_gray')
 paint(hi[:,2]<=3.0001,7,'display_base_not_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU Gechi Hall original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'gechi-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NCKU article images published 2021-09-28; exact capture dates not established','scope':'Registered front and east details; unknown west, rear and roof neutral. Existing geometry only; no new timber posts or brick texture.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
