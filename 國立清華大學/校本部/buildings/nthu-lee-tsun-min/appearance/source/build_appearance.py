"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='9be582cd39182301404224874dc47a9769a7a9b67dfaa649059bf2097cc5f625'
PALETTE=[('neutral_unknown_or_corridor','#AAA79F'),('pale_silver_mesh_proxy','#CBD0CC'),('muted_orange_frame','#C28A42'),('ivory_piers_frames','#D1D3CA'),('muted_dark_graygreen_glazing','#52615C')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_roof_right_side_and_open_corridor_backs_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-20)&xx(-41,61)&zz(17,95),1,'source_main_front_silver_screen_proxy_NO_added_mesh_weave')
 paint(plane(0,-41)&yy(-20,52)&zz(29.8,95),1,'source_left_silver_screen_proxy')
 paint(plane(1,52)&xx(-41,61)&zz(17,95),1,'source_garden_screen_and_balcony_band_outer_face')
 paint(plane(0,-68)&yy(-42.5,56.5)&zz(2.8,28),1,'source_low_side_silver_screen_proxy')
 paint(plane(1,-42.5)&xx(-68,-18)&zz(2.8,28),1,'source_low_front_silver_screen')
 for x in [17,47]:paint(box(x-1.6,x+1.6,-31,-17,50,80),2,'source_orange_upper_deep_frame_bounded_inner_outer_returns')
 for z in [50,77]:paint(box(15.5,48.5,-31,-17,z,z+3),2,'source_orange_upper_frame_horizontal')
 for x in [-57,-31]:paint(box(x-1.3,x+1.3,-49.5,-40.5,4,28),2,'source_orange_lower_frame')
 for z in [4,26]:paint(box(-58.5,-29.5,-49.5,-40.5,z,z+2.5),2,'source_orange_lower_frame_horizontal')
 for x in [22,32,42]:paint(box(x-.65,x+.65,-16.5,-13.5,52,77),3,'source_upper_original_white_window_grid')
 paint(box(19.5,44.5,-16.5,-13.5,61,62.3),3,'source_upper_window_horizontal_grid')
 paint(plane(1,-14)&xx(18.5,45.5)&zz(52,78),4,'source_upper_inner_window_back_only')
 for x in [-52,-44,-36]:paint(box(x-.6,x+.6,-43,-39,5,26),3,'source_lower_white_window_grid')
 for z in [12,20]:paint(box(-55.5,-32.5,-43,-39,z,z+1.2),3,'source_lower_white_horizontal_grid')
 paint(plane(1,-40)&xx(-55.5,-32.5)&zz(5,26),4,'source_lower_door_window_back_only')
 paint(plane(0,-65.8)&yy(-32.5,50.5)&zz(9,20),4,'source_low_side_actual_glazed_strip')
 for y in range(-28,49,8):paint(box(-69.5,-65.5,y-.6,y+.6,9,20),3,'source_low_side_white_frames')
 for x in [-36,-16,4,24,44,59]:paint(box(x-1.7,x+1.7,-17.5,-12.5,3,17.2),3,'source_white_ground_piers_bounded_returns')
 paint(plane(1,44)&xx(9,55)&zz(5,14),4,'source_garden_ground_glass')
 for x in [12,24,36,48]:paint(box(x-.65,x+.65,43.75,47.25,5,14),3,'source_garden_ground_white_frames')
 paint(hi[:,2]<=3.0001,0,'unsplit_base_not_green_lawn')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU Lee Tsun Min Hall original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthulee-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Architectural journal and NTHU photographs, uncalibrated proxies','scope':'Silver-white screen outer faces, two orange deep frames, white ground columns and existing grids, discrete known glazing. Open corridor and screen aperture backs neutral, not glass. Unknown roof and right side neutral; screen weave omitted by original geometry.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
