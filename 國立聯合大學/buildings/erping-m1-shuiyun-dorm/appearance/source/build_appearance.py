"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='55d99977be034a72c4b2925b92412d612314c70c0c81678ab7e08058093ffc8c'
PALETTE=[('neutral_unknown','#AAA79F'),('documented_red_brick','#AA6550'),('pale_gray_frames_soffits','#C3C6C1'),('silver_plates_rails_inlay','#9FA8AA'),('muted_blue_gray_glazing','#6B858D'),('gray_platform_ramp','#999E9B')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_rear_outer_side_roof_and_unsplit_base_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.003,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,16)&xx(-66,62)&zz(4.4,57.9),1,'documented_inner_tall_wing_brick')
 paint(plane(0,26)&yy(-40.5,16)&zz(4.4,39.8),1,'documented_inner_low_wing_brick')
 paint(box(24,64,-42.6,-39.9,4.4,40.9)&(n[:,1]<-.1),1,'documented_short_front_brick_with_original_coarse_coursing')
 for z in [20,37.5,55]:
  m=box(-67,63,13.2,17,z,z+3.4);paint(m,1,'observed_tall_front_brick_band');paint(m&(n[:,2]<-.9),2,'observed_pale_band_soffit')
 for z in [20,37.5]:
  for bounds in [(23,26.8,-41.5,43.5),(24,64,-42.6,-38.8)]:
   m=box(*bounds,z,z+3.4);paint(m,1,'observed_low_wing_brick_band');paint(m&(n[:,2]<-.9),2,'observed_pale_band_soffit')
 for row in range(3):
  z=7+row*17.5
  for x,w in [(-56,12),(-39,12),(-24,7),(-11,13),(8,12),(23,7)]:
   paint(plane(1,16.6)&xx(x-w/2,x+w/2)&zz(z,z+10.5),4,'tall_wing_discrete_pane_recess')
   m=1 if w<9 else 2
   for k in range(1,m+1):
    q=x-w/2+w*k/(m+1);paint(box(q-.4,q+.4,15.275,16.725,z-.05,z+10.55),2,'original_pale_window_mullion')
   paint(box(x-w/2-.05,x+w/2+.05,15.275,16.725,z+7.56,z+8.36),2,'original_pale_window_transom')
 for row in range(2):
  z=7+row*17.5
  for y,w in [(-31,9),(-17,10),(-3,10),(10,8)]:
   paint(plane(0,26.65)&yy(y-w/2,y+w/2)&zz(z,z+10.5),4,'low_wing_discrete_pane_recess')
   paint(box(25.2,26.7,y-.425,y+.425,z-.1,z+10.6),2,'low_wing_pale_mullion')
   paint(box(25.2,26.7,y-w/2-.05,y+w/2+.05,z+7.6,z+8.45),2,'low_wing_pale_transom')
 paint(plane(1,16.6)&xx(10.5,23.5)&zz(4.6,18),4,'inside_corner_entry_discrete_recess')
 for x in [11,17,23]:paint(box(x-.425,x+.425,15.2,16.7,4.5,18.1),2,'inside_corner_existing_entry_frame')
 paint(box(10.4,23.6,15.2,16.7,14.9,15.75),2,'inside_corner_transom')
 paint(plane(1,-40)&xx(27,37)&zz(4.7,19.5),3,'front_door_neutral_metal_not_whole_glass')
 paint(plane(1,-40)&xx(27,37)&zz(13.35,19.5),4,'front_door_only_existing_separable_upper_pane')
 paint(box(26.95,37.05,-41.25,-39.75,12.5,13.35),2,'front_door_transom')
 paint(plane(1,-40.05)&xx(49.5,59.5)&zz(15.7,20),4,'small_front_window_pane')
 paint(box(54.1,54.9,-41.275,-39.925,15.65,20.05),2,'small_front_mullion')
 paint(box(49.45,59.55,-41.275,-39.925,18.796,19.596),2,'small_front_transom')
 for bounds in [(24,44,-43,-41.2,22.1,29.1),(26,38,-42.45,-40.95,19.4,22.4),(40,61,-41.2,-40.3,11.6,16),(50.575,51.425,-41.15,-40.15,6,12)]:
  paint(box(*bounds),3,'existing_blank_plate_or_bowl_artwork_silver_no_text')
 for x in [47,55]:
  for z in [6,8.5,11]:paint(box(x-.85,x+.85,-41.2,-40.2,z,z+1.7),3,'existing_small_stone_inlay')
 paint(box(-50,-20,26,38,57.6,63.1)&(n[:,1]<-.1),2,'documented_front_roof_screen_only')
 paint(box(22,64,-51.2,-38.2,2.3,4.8),5,'documented_gray_front_platform')
 paint(box(4.5,21.5,-50,17,2.3,6),5,'existing_ramp_gray_not_grass')
 for x in [4.8,21.2]:paint(box(x-.6,x+.6,-45,15,2.35,8.2),3,'existing_ramp_rail_silver')
 paint(box(26.4,45.6,-47.6,-46.4,4.5,9.6),3,'existing_front_rail_silver')
 paint(hi[:,2]<=2.4001,0,'neutral_original_ground_base_no_landscape')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU M1 Shuiyun Dormitory original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuum1-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official M1 front and accommodation-centre courtyard photos; uncalibrated proxies','scope':'Documented short front and inner courtyard red brick, pale existing frames and band soffits, silver blank plates and bowl relief, discrete glass proxies and gray ramp. Unknown rear outer sides and roofs neutral; no letters or additional penthouse/landscape.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
