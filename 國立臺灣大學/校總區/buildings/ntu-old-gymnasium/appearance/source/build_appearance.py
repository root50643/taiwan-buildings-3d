"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='7d6aa9e2f83242a4a1e6a5670a752521dba363bdf921893ffbb597f984926505'
PALETTE=[('neutral_unknown','#AAA79F'),('offwhite_front_rear_structure','#D0D2C9'),('dark_neutral_screen_recess','#626B66'),('muted_gray_green_glazing','#617977'),('light_gray_mullions','#A1ABA6'),('gray_olive_shutter','#85897B'),('gray_stone_steps','#989A94')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unobserved_sides_roof_ground_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint((plane(1,-55)|plane(1,55))&xx(-66.5,66.5)&zz(2.8,50.8),1,'source_front_and_back_offwhite_wall')
 for y in [-55,55]:
  paint(box(-67.5,67.5,y-2,y+2,48,51)&(abs(n[:,2])<.1),1,'observed_portal_top_beam_vertical_faces')
  for x in [-64,64]:paint(box(x-3,x+3,y-2,y+2,2.8,50.8),1,'source_end_portal_piers')
 for x in [-48,-32,-16,16,32,48]:
  paint(box(x-.55,x+.55,-55.85,-54.15,7,47),1,'source_white_screen_separator')
  for x0 in [x-4.5,x-1.5,x+1.5,x+4.5]:
   for z in range(20,46,3):paint(plane(1,-53.75)&xx(x0-.9,x0+.9)&zz(z,z+1.8),2,'screen_opening_depth_proxy_NOT_glass')
  paint(plane(1,-54)&xx(x-5.75,x+5.75)&zz(6,16),3,'source_lower_front_window_back')
  for x0 in [x-3,x+3]:paint(box(x0-.45,x0+.45,-55.8,-54.2,6,16),4,'existing_lower_front_vertical_mullions')
  paint(box(x-5.75,x+5.75,-55.8,-54.2,10,10.9),4,'existing_lower_front_horizontal_mullion')
 paint(plane(1,-52)&xx(-7.5,7.5)&zz(6,47),3,'source_central_glazed_band_back')
 for x in [-5,0,5]:paint(box(x-.45,x+.45,-55,-53,6,47),4,'central_glazing_existing_vertical_mullions')
 for z in [17,27,37]:paint(box(-7.5,7.5,-55,-53,z,z+.9),4,'central_glazing_existing_horizontal_mullions')
 paint(plane(1,53)&xx(-10,10)&zz(5,16),5,'source_closed_stage_shutter_NOT_glass')
 for x in [-51,-39,-27,27,39,51]:
  for z,h in [(8,5),(20,10),(35,10)]:
   paint(plane(1,52.5)&xx(x-4.5,x+4.5)&zz(z,z+h),3,'source_rear_discrete_window_back')
   paint(box(x-.5,x+.5,53.1,54.9,z,z+h),4,'existing_rear_vertical_mullion')
   paint(box(x-4.5,x+4.5,53.1,54.9,z+h/2,z+h/2+1),4,'existing_rear_horizontal_mullion')
 for x in range(-15,16,5):
  for z in [42,45]:paint(plane(1,52.5)&xx(x-1.8,x+1.8)&zz(z,z+1.3),2,'rear_upper_vent_depth_NOT_glass')
 for y in [-56,56]:paint(box(-11.5,11.5,y-4,y+4,16,17.5),1,'source_small_entry_stage_canopy')
 paint(box(-17,17,-63.85,-57.95,3,5.6)|box(-32,32,56.2,65,3,6.3),6,'source_front_and_rear_existing_steps_gray_stone')
 paint(hi[:,2]<=3.0001,0,'original_unsplit_ground_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Old Gymnasium original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntuoldgym-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTU official historic front photograph and PE backstage photograph; uncalibrated proxies','scope':'Offwhite front/rear, dark screen recesses not glass, separate glazing and gray mullions, closed gray-olive stage shutter, gray steps. Unknown sides and roof neutral. Source dates unknown; no lettering, deterioration, equipment or trees.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
