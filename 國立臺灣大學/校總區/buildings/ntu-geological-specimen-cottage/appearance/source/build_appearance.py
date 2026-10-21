"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='807ae5fd53872cff6d68706fc48a2208b783916394791560bb8c4e27b1e558da'
PALETTE=[('neutral_unknown','#AAA79F'),('ivory_plaster','#D1CFC0'),('buff_stone_base','#B9A376'),('gray_stone_bands','#989D99'),('charcoal_tile_roof','#4E5452'),('gray_green_metal','#98AAA5'),('muted_teal_glazing','#628D8E')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_reverse_wall_and_ground_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-22.5)&xx(-60,48)&zz(7,33),1,'observed_blind_longwall_solid_plaster_NOT_glass')
 for x in [-59,-40,-21,-2,17,36,47]:paint(box(x-.7,x+.7,-23.5,-21.7,7,33),1,'observed_integral_plaster_pilasters')
 paint((plane(0,-60)|plane(0,48))&yy(-22.5,22.5)&zz(7,33),1,'documented_both_end_plaster_walls')
 paint((plane(0,-62.5)|plane(0,50.5))&yy(-26,26)&zz(32,47),1,'documented_end_gables_plaster')
 paint((plane(1,-23.5)|plane(0,-60)|plane(0,48))&box(-60,48,-23.5,23.5,2.8,7.8),2,'visible_buff_stone_base_no_block_texture')
 paint(box(-60,48,-23.3,-22.1,6.8,8.1),3,'visible_gray_stone_sill_band')
 # Both slopes retain one bounded roof material system; far slope not separately photographed.
 paint(box(-62.5,50.5,-26,26,32,47)&(n[:,2]>.7)&(abs(n[:,1])>.3),4,'tile_roof_same_system_bounded_extension_to_far_slope')
 for x in [-44,-23,-2,19,40]:paint(box(x-2.9,x+2.9,-2.9,2.9,44.5,53.4),5,'observed_existing_ridge_ventilator_metal_same_system')
 for x in [-62.5,50.5]:
  back=x+1.5 if x<0 else x-1.5
  paint(plane(0,back)&yy(-6,6)&zz(35,44),6,'documented_end_pentagonal_window_back')
  paint(box(x-1.8,x+1.8,-.5,.5,35,43),5,'existing_end_window_center_mullion')
  for y0 in [-4,4]:paint(box(x-1.8,x+1.8,y0-.45,y0+.45,35,41),5,'existing_end_window_side_mullion')
  paint(box(x-1.8,x+1.8,-5.5,5.5,39,39.9),5,'existing_end_window_horizontal_mullion')
 for y in [-13,13]:
  paint(plane(0,-58.5)&yy(y-5.5,y+5.5)&zz(10,27),6,'documented_twin_rectangular_window_backs')
  paint(box(-63.5,-58.5,y-7.5,y+7.5,27,28.8),3,'documented_gray_stone_window_hoods')
 # Vestibule front/entry are documented; opposite long face remains neutral.
 paint(plane(1,-22.5)&xx(47,73)&zz(2.8,28.8),5,'visible_vestibule_gray_green_solid_frame_proxy')
 paint(plane(0,73)&yy(-22.5,22.5)&zz(2.8,28.8),5,'documented_vestibule_entry_end_frame')
 for x in [53,64]:paint(plane(1,-21.1)&xx(x-4,x+4)&zz(9,26),6,'visible_vestibule_side_window_back')
 for y in [-14,0,14]:paint(plane(0,71.5)&yy(y-5.5,y+5.5)&zz(9,26),6,'documented_vestibule_entry_window_back')
 for x in [48,58.5,72.5]:paint(box(x-.75,x+.75,-23.3,-21.7,3,30),5,'visible_existing_vestibule_vertical_frames')
 for y in [-21,-7,7,21]:paint(box(72.2,73.8,y-.75,y+.75,3,30),5,'existing_vestibule_entry_vertical_frames')
 paint(box(47,73,-23.35,-21.65,7,8.5),5,'visible_vestibule_horizontal_frame')
 paint(box(45.5,74.5,-24,24,29,30.8),5,'documented_vestibule_metal_canopy')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Geological Specimen Cottage original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntucottage-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTU official 2014 newsletter and 2010 historic photograph; uncalibrated proxies','scope':'Documented two end walls and one blind long wall; dark roof extended as one tile material system, gray-green ridge vents, buff base, gray stone hoods and discrete muted panes. Unknown reverse long wall and reverse vestibule neutral; no logos or aging texture.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
