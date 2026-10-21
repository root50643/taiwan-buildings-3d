"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='486b730467f37aec8a03a3ac39d9dc47efc538874e9fd3fcfb5e3ad4d261135e'
PALETTE=[('neutral_unknown_or_mixed','#AAA79F'),('ivory_white_front_wall','#D1D0C4'),('dark_bronze_entry_metal','#4E514A'),('pale_gray_window_metal','#A6A99D'),('muted_graygreen_glazing','#81958D'),('gray_stone_steps','#999B91')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_rear_end_roof_and_tower_slot_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-24)&xx(-42,66)&zz(2.8,99),1,'source_registered_main_front_white_wall')
 paint(plane(1,-42.5)&xx(-64,-34)&zz(2.8,109),1,'source_registered_tower_front_white_wall')
 # Do not assume opposite facade registration from historic generator claim.
 for z in [9,22,35,48,61,74,87,100]:paint(box(-53.7,-44.3,-44.75,-39.25,z,z+2.2),1,'source_tower_slot_crossbars_white_slot_back_neutral')
 paint(plane(1,-20)&xx(-2,46)&zz(3,37),4,'source_entry_curtain_glass_back_opaque_proxy_no_interior')
 for x in [0,9,18,27,36,45]:paint(box(x-.65,x+.65,-30,-20,3,37),2,'source_entry_charcoal_vertical_frames')
 for z in [9,16,23,30]:paint(box(-2,46,-29.5,-20.5,z,z+1.3),2,'source_entry_charcoal_horizontal_frames')
 for z in [42,53,64,75,86]:
  paint(plane(1,-22)&xx(-6.5,60.5)&zz(z,z+6.7),4,'source_discrete_upper_front_window_backs')
  for x in [-4,7,18,29,40,51,59]:paint(box(x-.55,x+.55,-26.25,-21.75,z,z+6.7),3,'source_upper_front_window_mullions')
  for x in [-25,-18,-11]:paint(plane(1,-22.5)&xx(x-1.9,x+1.9)&zz(z,z+7),4,'source_front_narrow_window_backs')
 paint(box(-3.5,47.5,-36,-26,3,5.5),5,'source_gray_stone_entry_steps')
 paint(hi[:,2]<=3.0001,0,'unsplit_base_not_paving_or_lawn')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU General Building II original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthugeneral2-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTHU official source photographs, uncalibrated surface proxies','scope':'Only registered front white masonry, separate graygreen window backs, charcoal entrance frames, pale upper mullions and gray entry steps. Tower continuous slot neutral, no assumed glass. Opposite facade registration unproven; rear including windows, ends and roof neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
