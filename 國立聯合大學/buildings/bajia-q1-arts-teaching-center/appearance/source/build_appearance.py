"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='4728cfad77601086a6b032a7d6da06535ba29e2134a37e0c9f3d322f3d0bac46'
PALETTE=[('neutral_unseen','#AAA79F'),('warm_ochre_wall','#BAA57F'),('cool_gray_tower','#B3BAB7'),('blue_gray_glazing','#557586'),('charcoal_mullions','#596564'),('rust_brown_rails','#92766A'),('gray_steps','#9C9F98'),('pale_right_hall','#BEBAB0')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_back_roof_cut_sides_and_display_base_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0003)&(hi[:,2]<=b+.0003)
 def xx(a,b):return (lo[:,0]>=a-.0003)&(hi[:,0]<=b+.0003)
 def yy(a,b):return (lo[:,1]>=a-.0003)&(hi[:,1]<=b+.0003)
 def plane(y):return np.all(abs(t[:,:,1]-y)<.0003,axis=1)
 def box(x,y,z,w,d,h):return xx(x-w/2,x+w/2)&yy(y-d/2,y+d/2)&zz(z,z+h)
 for x,y,z,w,d,h in [(-29,-7,2.3,66,58,18.4),(-38,7,20.5,40,34,30),(-55,18,2.3,19,26,42.2),(-8,-26,2.3,29,13,18.7)]:paint(box(x,y,z,w,d,h)&(n[:,1]<-.99),1,'source_front_ochre_wall_not_window_spandrel_glass')
 paint(box(-8,-27,20.2,33,16,2),1,'source_ochre_entry_header_blank_no_letters')
 paint(box(-43,-35.2,20,38,2,1.6),1,'observed_ochre_terrace_fascia')
 paint(box(-8,5,20.5,24,36,40)&(n[:,1]<-.99),2,'observed_cool_gray_tower_front_frame')
 paint(box(-8,5,59.4,25.5,37,1.6)&(n[:,1]<-.99),2,'observed_tower_front_lintel_edge_roof_unseen')
 paint(xx(-17.5,1.5)&zz(22.5,57.3)&plane(-11.9),3,'existing_tower_glazing_back')
 for x in np.linspace(-16.5,.5,8):
  paint(box(float(x),-12.6,22.4,.75,2,35),4,'existing_tower_vertical_mullions_dark')
 for i,x in enumerate(np.linspace(-16.5,.5,8)):
  for z in np.arange(25.5+(i%2)*2.5,56,7.7):paint(box(float(x),-12.6,float(z),2.7,2,.75),4,'existing_staggered_transoms_dark_no_fake_extra_pattern')
 for z in [25,39]:
  paint(xx(-57.5,-22.5)&zz(z,z+7.9)&plane(-9.2),3,'left_wing_original_window_band_back')
  for x in np.arange(-55.5,-23,4.2):paint(box(float(x),-9.8,z-.1,.85,1.5,8.1),4,'left_wing_existing_vertical_mullions')
  paint(box(-40,-9.8,z+5.7,35.1,1.5,.85),4,'left_wing_existing_transom')
  paint(box(-40,-10.65,z-.65,35.8,1.5,.85),1,'left_wing_sill_ochre')
 paint(xx(-20.75,4.75)&zz(3,18.5)&plane(-31.5),3,'lower_entry_original_glazing_back')
 for x in [-18.6,-13.3,-8,-2.7,2.6]:paint(box(x,-32.2,2.9,.9,1.6,15.7),4,'entry_existing_mullions')
 paint(box(-8,-32.2,14.1,25.6,1.6,.9),4,'entry_existing_transom')
 paint(box(45,7,2.3,44,43,31.5)&(n[:,1]<-.99),7,'undated_official_aerial_right_hall_front_pale_proxy_not_2026_claim')
 paint(xx(27,63)&zz(5.2,30)&plane(-13.45),3,'historical_aerial_right_hall_existing_glazing_back')
 for x in [29,37,45,53,61]:paint(box(x,-14.1,5.1,.95,2,25),4,'existing_right_hall_vertical_mullions')
 for z in [12.8,22]:paint(box(45,-14.1,z,36.2,2,.95),4,'existing_right_hall_transoms')
 for x in [5.2,20]:paint(xx(x,x+1.5)&yy(-39.5,-14)&zz(2.3,24.1),1,'source_ochre_solid_stair_cheeks')
 paint(xx(5.5,20.5)&yy(-39.5,-14)&zz(2.3,21)&(n[:,2]>.99),6,'existing_compressed_stair_treads_gray_not_accessibility_survey')
 for x in np.arange(-61,7,3.8):paint(box(float(x),-31,21.5,.95,.95,3.4),5,'existing_thickened_terrace_rail_posts_rust_brown')
 paint(box(-28,-31,24,72,1,.95),5,'existing_terrace_toprail_rust_brown')
 for x in [6,20.7]:
  for y in np.arange(-38.5,-14,3.5):paint(box(x,float(y),5+(y+39.5)/25.5*19,.9,.9,2.5),5,'existing_stair_rail_posts')
  zlow=7.4+(t[:,:,1]+39)/25*18.7;zhigh=8.5+(t[:,:,1]+39)/25*18.5
  paint(xx(x-.6,x+.6)&yy(-39,-14)&np.all((t[:,:,2]>=zlow-.0003)&(t[:,:,2]<=zhigh+.0003),axis=1),5,'existing_sloped_stair_handrail_rust_brown')
 for y in np.arange(-12.5,28,3.8):paint(box(23.2,float(y),34.5,.95,.95,2.9),5,'observed_right_hall_side_rail_posts')
 paint(box(23.2,7.5,36.6,.95,42.5,.95),5,'observed_right_hall_toprail')
 paint(hi[:,2]<=2.4001,0,'neutral_display_base_not_site_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU Q1 Arts Teaching Center original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuuq1-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official Q1 gallery photos1/2 EXIF2025 plus undated official aerial; uncalibrated proxies','scope':'Observed front ochre, cool gray tower, original window backs and charcoal mullions, rust rails, gray treads. Right hall bounded by undated historical aerial not current claim. Rear/roof neutral; no artworks/logos/text or neighbor buildings.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
