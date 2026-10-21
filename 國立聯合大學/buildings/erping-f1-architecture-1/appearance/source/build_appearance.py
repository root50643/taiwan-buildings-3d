"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='91bb0d8dc10370e1c174090be4187774a2249aa3f53aa5213c5b7b81e49204c9'
PALETTE=[('neutral_unknown','#AAA79F'),('gray_concrete_front','#A4A6A1'),('pale_frame_sign_fascia','#C3C7C4'),('dark_teal_glazing_proxy','#3E6264'),('dark_roof_edge','#45525B'),('annex_tile_gray','#B4B9B4'),('shopfront_glazing_proxy','#788D8E')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_rear_roof_sides_or_unregistered_detail_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.001)&(hi[:,2]<=b+.001)
 def xx(a,b):return (lo[:,0]>=a-.001)&(hi[:,0]<=b+.001)
 def yy(a,b):return (lo[:,1]>=a-.001)&(hi[:,1]<=b+.001)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.001,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-14)&xx(-70,70)&zz(2.3,84.3),1,'registered_front_gray_concrete_not_neighbor_H1_or_F2')
 paint(box(-71,71,-14.5,-13.8,84,93),2,'original_front_high_fascia_pale_silver')
 paint(box(-71.5,71.5,-15,-14,92.5,93.8)&(n[:,1]<-.2),4,'observed_dark_front_roof_edge_only_unseen_flat_top_neutral')
 paint(box(-67,17,-16.25,-14,23,75)&(hi[:,1]<-14.001),2,'existing_projecting_front_window_piers_and_bands_pale')
 for z in [38,64]:
  for x in [-60,-51,-42,-29,-20,-11]:paint(xx(x-3.8,x+3.8)&zz(z,z+4)&plane(1,-12.85),3,'narrow_clerestory_recess_back_dark_teal_proxy')
  paint(xx(1.5,14.5)&zz(z-13,z+3)&plane(1,-12.9),3,'tall_bay_mixed_glass_panel_uniform_teal_proxy_not_all_glass_claim')
 paint(xx(-64.9,-57.1)&zz(15,19.5)&plane(1,-12.9),3,'lower_left_slit_window_recess')
 paint(box(-52.5,-9.5,-27.5,-14,2.3,18.3),5,'annex_existing_tile_massing_and_grooves_gray_not_glass')
 paint(box(-53,-9,-28,-12,18.5,23)&(n[:,2]>.2),3,'observed_green_sloping_annex_cap_surface_only')
 for x in [25,37,49,61]:paint(xx(x-5,x+5)&zz(5,20)&plane(1,-12.85),6,'discrete_shopfront_recess_bluegray_opaque_glass_proxy')
 paint(box(17.5,70.5,-19,-14,20,25),2,'blank_existing_shop_sign_no_letters_or_brand')
 paint(hi[:,2]<=2.4001,0,'neutral_display_base')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU F1 Architecture One original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuuf1-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official F1 Architecture One photos1–2; uncalibrated proxies','scope':'Observed front gray concrete, pale fascia and original window relief, teal recess proxies and annex cap, pale gray annex, bluegray shop panes. Mixed tall bays approximate; unknown rear and flat roof neutral. No brand or neighboring buildings.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
