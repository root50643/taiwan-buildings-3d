"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='9b9c512aa492e75b469581f0184a8e51ac557800865f5b8e89ec2390745aa55e'
PALETTE=[('neutral_mixed_or_unknown','#AAA79F'),('pale_pinkbeige_tiles','#C9B4A3'),('muted_orange_red_brick','#AD7559'),('gray_tile_concrete','#929B99'),('silver_window_frames','#C0CCC7'),('muted_graygreen_glazing','#849F98')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_main_walls_top_frame_band_entry_back_balconies_and_unknown_roof_rear_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 for x,w in [(-34,9),(19,10)]:paint(plane(1,-38.5)&xx(x-w/2,x+w/2)&zz(31,78),1,'source_pink_projected_upright_front_only_dark_balcony_recess_neutral')
 # Top bar includes an unmodeled gray upper band, so stays neutral.
 for x in [-19,4]:paint(box(x-1.8,x+1.8,-29.8,-26.2,33,77),3,'source_gray_round_pier_bounded_circumference')
 for z in [36,47,58,69]:
  paint(plane(1,-25.1)&xx(-28,12)&zz(z,z+7),5,'source_separate_center_window_back_NOT_solid_spandrel')
  for x in [-26,-21,-16,-11,-6,-1,4,9]:paint(box(x-.35,x+.35,-27.35,-24.85,z,z+7),4,'source_existing_center_silver_vertical_frame')
  paint(box(-28,12,-27.35,-24.85,z+3.2,z+3.9),4,'source_existing_center_silver_crossbar')
 for z in [13,24,35,46,57,68,79,90]:
  for x in [-45,39]:paint(plane(1,-33.1)&xx(x-3.25,x+3.25)&zz(z,z+6.5),5,'source_discrete_front_side_window_back')
 paint(plane(1,-31.5)&xx(-28.5,10.5)&zz(89,96),5,'source_top_front_glazed_recess')
 for x in [-24,-15,-6,3,12]:paint(box(x-.5,x+.5,-36.1,-31.1,89,96),4,'source_top_original_silver_mullion')
 for y in [-16,32]:
  for z in [12,23,34,45,56,67,78,89]:
   paint(box(42.8,50.8,y-6,y+6,z,z+1.3),3,'source_right_balcony_slab_NOT_window')
   paint(box(49.2,50.4,y-6,y+6,z+1.3,z+3.5),3,'source_existing_coarse_balcony_rail_neutralgray_no_invented_glass_panes')
 for z in [36,47,58,69,80,91]:
  for y in [-31,-3,8,19,40]:
   w=6.5 if y==-31 else 5.5;paint(plane(0,49.1)&yy(y-w/2,y+w/2)&zz(z,z+6.5),5,'source_discrete_right_window_back')
 paint(plane(0,54)&yy(-10,26)&zz(11,32),2,'source_right_low_brick_box_outer_face')
 for z in [14,24]:
  for y in [-4,7,18]:paint(plane(0,53.1)&yy(y-3,y+3)&zz(z,z+6),5,'source_low_box_window_back')
 paint(plane(1,-41.5)&xx(-36.5,20.5)&zz(3,32),2,'source_red_front_portal_face_only_mixed_inner_white_entry_back_neutral')
 paint(box(15.25,20.75,-42,-40,3,32),2,'source_blank_red_name_pier_no_text')
 for x in [-28,-21,-14,-7,0,7]:paint(box(x-.4,x+.4,-43.7,-38.7,5,28),4,'source_original_entry_silver_vertical_strip')
 for z in [12,20]:paint(box(-31.5,11.5,-43.7,-38.7,z,z+.8),4,'source_original_entry_silver_crossbar')
 paint(box(-34,14,-53,-42,3,7.2),3,'source_concrete_entry_steps')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU Delta Hall original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthudelta-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTHU official alumni and EE photographs, uncalibrated proxies','scope':'Projected upright front pinkbeige, red entrance outer frame and right low box, gray columns and balcony slabs, actual discrete glazing and silver frames. Mixed main walls, upper frame gray band, inner entry white canopy backing, balcony recesses and unknown roof/rear neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
