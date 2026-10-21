"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='e736d9054cb5673b206ef24b07877a681839b7e47ee80e2f71de07e384f294e7'
PALETTE=[('neutral_unknown','#AAA79F'),('muted_redbrown_tile','#9F8175'),('muted_graygreen_glass','#87968D'),('pale_silver_existing_frames','#BDC5BE')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_right_rear_roof_and_ground_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-19.5)&xx(-68,68)&zz(2.8,69.8),1,'source_front_solid_redbrown_tile_wall')
 paint(plane(0,-68)&yy(-19.5,29.5)&zz(2.8,69.8),1,'source_left_end_redbrown_tile_wall')
 for y in [-20,-2,15,29]:paint(box(-68.8,-67.2,y-1,y+1,3,70),1,'source_left_end_tile_rib')
 for z in [20,37,54]:paint(box(-68.5,68.5,-20.4,-18.8,z,z+1.3),1,'source_existing_front_tile_sill')
 for z in [23,40,57]:
  for x in [-55,-34,-13,26,48]:
   if z==23 and x==26:continue
   paint(plane(1,-18)&xx(x-8,x+8)&zz(z,z+9),2,'source_upper_window_back_only')
   paint(box(x-.5,x+.5,-20.05,-18.15,z,z+9),3,'source_existing_upper_vertical_frame')
   paint(box(x-7.75,x+7.75,-20.05,-18.15,z+6,z+6.9),3,'source_existing_upper_horizontal_frame')
 for x in [-57,-41,-25,-9,51,64]:
  paint(plane(1,-18)&xx(x-5.5,x+5.5)&zz(5,17),2,'source_ground_window_back_only')
  paint(box(x-.5,x+.5,-20.05,-18.15,5,17),3,'source_existing_ground_vertical_frame')
 paint(box(4.5,39.5,-25,-17,3,35),1,'source_projecting_entry_tile_surround')
 paint(box(4.5,39.5,-29,-19,18.5,24),1,'source_solid_brown_sign_fascia_NO_letters_NO_glass')
 for z,h,w,xs in [(4,14,23,[15,22,29]),(25,9,29,[14,22,30])]:
  paint(plane(1,-23.5)&xx(22-w/2,22+w/2)&zz(z,z+h),2,'source_entry_glazed_back_separate_from_solid_fascia')
  for x in xs:
   hw=.55 if z==4 else .5
   paint(box(x-hw,x+hw,-25.6,-23.6,z,z+h),3,'source_existing_entry_vertical_frames')
 for y in [-12,6,22]:
  for z in [10,29,46,63]:paint(plane(0,-66.5)&yy(y-5.5,y+5.5)&zz(z,z+4),2,'source_left_end_low_window_strip_back')
 paint(hi[:,2]<=3.0001,0,'unsplit_ground_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Food Science Front original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntufood-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTU official 2010 S48 historical photographs, uncalibrated proxies','scope':'Front/left reddish-brown tiles, separated existing glazing and silver frames, solid entry fascia not glass; unregistered right/rear/roof neutral. Original simplified window rhythm and absent annex preserved.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
