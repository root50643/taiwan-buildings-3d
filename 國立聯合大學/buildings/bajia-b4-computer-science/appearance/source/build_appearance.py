"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='166c05cd28dcd4192e145d51d8846e5a7895bf2c1b0ed5c56cefee664311743c'
PALETTE=[('neutral_unseen','#AAA79F'),('gray_concrete','#9CA3A3'),('offwhite_panels','#CCD0C9'),('sage_tile','#8BA99A'),('pale_yellow_upper','#D8C98F'),('muted_green_glazing','#63847F'),('pale_window_frame','#B8C5BD'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_rear_roof_side_and_unregistered_opening_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def xx(a,b):return (lo[:,0]>=a-.00025)&(hi[:,0]<=b+.00025)
 def yy(a,b):return (lo[:,1]>=a-.00025)&(hi[:,1]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 paint(xx(-67,68)&yy(-27.3,-21.4)&zz(2.4,68.6)&(n[:,1]<.1),1,'observed_front_gray_concrete_not_unknown_right_end')
 paint(xx(30,48)&yy(-24.4,-22.6)&zz(3.1,68.1),3,'existing_vertical_green_tile_panel_source3')
 for z,h in [(17.4,13.1),(41.9,14.4)]:paint(xx(7,47)&yy(-24.3,-22.6)&zz(z,z+h),3,'existing_horizontal_green_relief_H_pattern_proxy')
 # Do not pretend the original H relief partitions coincide with every real window.
 for x in [-35,-21,-7,7,21]:paint(xx(x-3.1,x+3.1)&yy(-27,-20.6)&zz(19,58.4),2,'existing_broad_white_projecting_panels')
 paint(xx(-46.5,32.5)&yy(-23.95,-22.65)&zz(64.1,68.6),4,'existing_shallow_top_band_yellow_no_roof_color')
 paint(xx(-47,33)&yy(-25.45,-22.55)&zz(68,69.1),1,'existing_upper_eave_gray')
 # Ordinary repeated bays have mixed real window/corridor identities; only unambiguous left bays use glass.
 for x in [-45,-24,-2,20]:
  for z in [7,19.5,32,44.5,57]:
   back=xx(x-6,x+6)&plane(1,-21.4)&zz(z,z+7.1)
   paint(back,5 if x in [-45,-24] else 0,'registered_left_window_back' if x in [-45,-24] else 'mixed_center_bay_uncertain_neutral_not_glass')
   for dx in [-3.5,0,3.5]:paint(xx(x+dx-.425,x+dx+.425)&yy(-25.1,-21.1)&zz(z,z+7.1),6,'existing_bay_frame_pale_material_proxy')
   paint(xx(x-6,x+6)&yy(-25.1,-21.1)&zz(z+4.8,z+5.65),6,'existing_horizontal_window_frame')
 # Reapply full white panels where frames merge, avoid arbitrary gray strips on them.
 for x in [-35,-21,-7,7,21]:paint(xx(x-3.1,x+3.1)&yy(-27,-25.1003)&zz(19,58.4),2,'frontmost_white_panel_planes')
 paint(xx(-14,2)&plane(1,-21.7)&zz(3.4,20.4),5,'source_central_double_height_entry_back_green_glass')
 for x in [-11,-6,-1]:paint(xx(x-.475,x+.475)&yy(-26.8,-21.4)&zz(3.4,20.4),6,'existing_entry_vertical_mullions_pale')
 for z in [9.5,15]:paint(xx(-14,2)&yy(-26.8,-21.4)&zz(z,z+.95),6,'existing_entry_horizontal_mullions_pale')
 paint(xx(56,68)&yy(-24.35,-22.85)&zz(17.5,68.3),1,'right_corner_glazing_structural_surround')
 paint(xx(56.95,67.05)&plane(1,-23.7)&zz(18.4,66.7),5,'source_right_front_curtain_glass_back_only')
 for x in [58.7,62,65.3]:paint(xx(x-.425,x+.425)&yy(-24.65,-23.25)&zz(18.4,66.7),6,'existing_right_curtain_mullions_pale')
 for z in [29.8,42.2,54.6,60.1]:paint(xx(56.8,67.2)&yy(-24.65,-23.25)&zz(z,z+.9),6,'existing_right_curtain_horizontal_mullions')
 for z in [7,19.5,32,44.5,57]:paint(xx(47,55)&plane(1,-22.3)&zz(z,z+8.6),0,'right_open_stair_gallery_neutral_not_glass')
 paint(xx(-66.5,-51.5)&yy(-26,-22)&zz(2.4,68.3)&(n[:,1]<.1),1,'left_front_stair_tower_gray_frame')
 paint(xx(-64.3,-53.7)&plane(1,-25.1)&zz(5,64),5,'source_left_diagonal_stair_glazing_back')
 for x in [-62,-58]:paint(xx(x-.45,x+.45)&yy(-26.25,-24.85)&zz(5,64),6,'existing_left_stair_glazing_vertical_mullions')
 for z in [15.5,28,40.5,53]:
  paint(xx(-64.5,-53.5)&yy(-26.25,-24.85)&zz(z,z+1),6,'existing_left_stair_glazing_cross_frames')
  paint(xx(-64,-54)&yy(-27.2,-24.3)&zz(z-5,z+4.6)&(lo[:,1]<-26.251),1,'existing_diagonal_stair_spandrel_gray_not_glass')
 paint(xx(-69.5,69.5)&yy(-34,-22.5)&zz(2.4,3.4),1,'existing_shallow_entry_terrace_gray')
 paint(hi[:,2]<=2.4001,7,'neutral_display_base_not_site')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU Bajia B4 Computer Science original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuub4-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Correct official B4 photos3 and8, EXIF2025; photos12/13/15 withdrawn as B3 misidentification','scope':'Observed B4 front only; original H relief approximate, mixed central bays and open gallery neutral. Existing diagonal stair glazing separated from gray spandrels. No roof PV invented; rear/right end neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
