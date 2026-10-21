"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='30660095840c143eb4573c3723922c8019defa56ab73789f542942fab6918995'
PALETTE=[('neutral_unknown','#AAA79F'),('muted_red_brick','#AD725C'),('pale_gray_concrete_band','#ADB3AA'),('dark_graygreen_glazing','#53605A'),('dark_gray_window_frames','#707B73'),('pale_cream_soffit','#CCC7B5')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_roof_rear_left_side_and_balcony_recess_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-43)&xx(-50,50)&zz(3,104.8),1,'source_front_red_brick_field')
 paint(plane(0,50)&yy(-43,60)&zz(3,104.8),1,'source_right_red_brick_field_and_lower_wing')
 paint(plane(1,-27)&xx(-28.5,18.5)&zz(7,85),1,'source_front_loggia_back_brick_floor_dividers')
 paint(plane(0,34)&yy(-24,8)&zz(7,85),1,'source_right_loggia_back_brick_floor_dividers')
 paint((plane(0,-28.5)|plane(0,18.5))&yy(-43,-27)&zz(7,85),1,'source_front_loggia_brick_inner_pier_return')
 paint((plane(1,-24)|plane(1,8))&xx(34,50)&zz(7,85),1,'source_right_loggia_brick_inner_pier_return')
 paint(plane(2,85)&(box(-28.5,18.5,-43,-27,85,85)|box(34,50,-24,8,85,85)),5,'source_pale_loggia_ceiling_NOT_dark_shadow_wall')
 for z in [10,20,30,40,50,60,70,80]:
  paint(plane(1,-26.1)&xx(-26.5,16.5)&zz(z,z+6.5),3,'source_front_loggia_discrete_window_back')
  paint(plane(0,33.1)&yy(-22.5,6.5)&zz(z,z+6.5),3,'source_right_loggia_discrete_window_back')
  for x in [-24,-16,-8,0,8,16]:paint(box(x-.45,x+.45,-28.45,-25.95,z,z+6.5),4,'source_front_original_dark_window_mullions')
  for y in [-20,-12,-4,4]:paint(box(32.95,35.45,y-.45,y+.45,z,z+6.5),4,'source_right_original_dark_window_mullions')
 for x in np.arange(-44,46,6):paint(plane(1,-41.8)&xx(x-1.3,x+1.3)&zz(90,99),3,'source_narrow_top_front_window_back')
 for y in np.arange(-37,25,6):paint(plane(0,48.8)&yy(y-1.3,y+1.3)&zz(90,99),3,'source_narrow_top_right_window_back')
 for z in [8,18,28,38,48,58,68,78]:
  paint(box(-46,-34,-46.5,-41.5,z,z+2.2)|box(48.5,53.5,12.5,23.5,z,z+2.2),2,'source_gray_balcony_slab_existing_thick_proxy')
 for z in [15,25,35,45,55,65,75,85,101]:
  for x,w in [(-40,20),(35,30)]:paint(box(x-w/2,x+w/2,-43.7,-42.5,z,z+1.2),2,'source_original_thickened_pale_front_horizontal_band')
  for y,d in [(-33,20),(18,18)]:paint(box(49.5,50.7,y-d/2,y+d/2,z,z+1.2),2,'source_original_thickened_pale_right_horizontal_band')
 for z in [20,30,40,50,60,70]:
  paint(plane(0,48.75)&yy(29,57)&zz(z,z+6.5),3,'source_lower_right_wing_window_back')
  for y in [32,38,44,50,56]:paint(box(48.85,51.35,y-.45,y+.45,z,z+6.5),4,'source_lower_right_wing_existing_window_mullion')
 for y in [30,38,46,54]:paint(box(47.5,52.5,y-1,y+1,3,16),2,'source_lower_wing_pale_ground_column')
 paint(hi[:,2]<=3.0001,0,'unsplit_base_not_grass')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU TSMC Building original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthutsmc-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTHU MBA street and OIR aerial photographs, uncalibrated proxies','scope':'Source front and right red brick including registered loggia back dividers; pale relief bands/balcony slabs, cream loggia ceiling, discrete dark glazing and frames. Unknown roof/rear/left and unregistered balcony recesses neutral. Public art tubing absent in original remains absent.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
