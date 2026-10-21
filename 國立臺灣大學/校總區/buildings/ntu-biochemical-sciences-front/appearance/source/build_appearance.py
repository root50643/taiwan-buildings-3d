"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='6eb741451da41c9fa6c8689e4cf6784232a769d8503c76d914834f0cd6f115de'
PALETTE=[('neutral_unknown','#AAA79F'),('muted_red_tile','#AD6B59'),('silver_gray_sunshades','#ADB3AC'),('offwhite_canopy','#D2D3C6'),('muted_graygreen_door_glass','#7E8E83'),('muted_graybronze_door_frames','#8D9481')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_outer_sides_rear_roof_and_upper_louver_back_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-23.5)&xx(-65,65)&zz(2.8,70.8),1,'source_front_solid_red_tile_including_lower_entry_surround')
 for x in [-50,50]:
  paint(plane(1,-30)&box(x-15,x+15,-30,-30,3,71),1,'source_blank_front_red_tile_wing')
  cx=x+(8 if x>0 else -8)
  rr=np.sqrt((t[:,:,0]-cx)**2+(t[:,:,1]+25)**2)
  paint(xx(cx-7,cx+7)&yy(-32,-25)&zz(3,71)&(np.abs(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])[:,2])<.00001),1,'source_rounded_front_corner_red_tile_only_front_half')
 for x in [-61,61]:paint(plane(1,-28.5)&box(x-4,x+4,-28.5,-28.5,70,75),1,'source_front_end_of_raised_tile_side_wall')
 for x in [-30,-10,10,30]:paint(box(x-1.9,x+1.9,-28,-22,17,71),1,'source_existing_red_tile_vertical_louver_bands')
 for x in [-20,0,20]:
  for z in range(21,68,3):paint(box(x-8.5,x+8.5,-28,-20,z,z+1.2),2,'source_existing_silver_gray_horizontal_sunshade_not_glass')
  paint(plane(1,-21.5)&xx(x-7,x+7)&zz(5,16),4,'source_separate_ground_door_glass_back')
 for x in [-26,-13,0,13,26]:paint(box(x-.5,x+.5,-24.5,-22.5,5,16),5,'source_existing_lower_vertical_door_frame_proxy')
 paint(box(-37,37,-40,-20,17,19.8),3,'source_offwhite_canopy_with_bounded_same_material_top')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Biochemical Sciences Front original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntubiochem-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTU official historical N24 exterior photos; uncalibrated material proxies','scope':'Red tile front wings and leading curves, red vertical bands, silvergray existing sunshades, offwhite canopy with bounded same-material top, separate ground glazing and frames. Upper recess behind louvers and unknown sides/rear/roof neutral, no added equipment or annex.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
