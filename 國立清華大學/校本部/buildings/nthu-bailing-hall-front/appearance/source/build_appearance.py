"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='dd4e8970dfa0bb56a7960558ed12f2942245bbe51d92a0d0741505115cf64bd3'
PALETTE=[('neutral_unknown_or_mixed','#AAA79F'),('white_fascia_and_window_frames','#D4D5CD'),('pale_gray_tiled_piers','#BCBCB1'),('muted_dark_graygreen_glazing','#637873'),('charcoal_coping_edge','#383D3B'),('gray_entry_steps','#8B918C')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_roof_rear_right_and_unsplit_platform_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-46)&xx(-39.5,39.5)&zz(6,39),3,'historical_photo1_front_glass_unshaded_not_photo2_lowered_blind_white')
 paint(plane(0,-39.5)&yy(-47,47)&zz(6,39),3,'historical_photo1_registered_left_glass_back')
 paint(plane(1,-46.5)&xx(-5,5)&zz(6,20),3,'historical_entry_door_glass_back')
 for x in range(-38,39,8):paint(box(x-.55,x+.55,-51,-47,6,39),1,'source_existing_front_white_mullions')
 for z in [7,13,20,36,39]:paint(box(-41,41,-51,-47,z,z+(2 if z==20 else 1.1)),1,'source_existing_front_white_transoms')
 for y in range(-44,46,8):paint(box(-44.5,-40.5,y-.55,y+.55,6,39),1,'source_existing_left_white_mullions')
 for z in [7,13,20,36,39]:paint(box(-44.5,-40.5,-49.5,49.5,z,z+(2 if z==20 else 1.1)),1,'source_existing_left_white_transoms')
 for x in [-5,0,5]:paint(box(x-.6,x+.6,-51.7,-47.7,6,20),1,'source_white_entry_leaves_frames')
 paint(box(-5.5,5.5,-51.7,-47.7,19,20.2),1,'source_white_entry_door_header')
 for x in [-42,-14,14,42]:
  paint(box(x-1.7,x+1.7,-52.5,-46.5,5,41),2,'source_gray_tiled_front_piers_no_brick_texture')
  paint(box(x-2.5,x+2.5,-53.5,-46.5,5,6.4),2,'source_same_pier_footing_component')
 for y in [-48,-24,0,24,48]:
  paint(box(-45.5,-39.5,y-1.7,y+1.7,5,41),2,'source_gray_tiled_left_piers')
  paint(box(-46,-39,y-2.5,y+2.5,5,6.4),2,'source_same_left_pier_footing')
 for x in [-34.5,-11.5,11.5,34.5]:paint(box(x-10.9,x+10.9,-57,-53,42,47)&(norm[:,2]<.0001),1,'source_white_segmented_front_fascia_edges_soffit')
 for y in [-40,-14,12,38]:paint(box(-48,-44,y-12.25,y+12.25,42,47)&(norm[:,2]<.0001),1,'source_white_segmented_left_fascia')
 paint(box(-47.5,47.5,-55,59,40,42)&(norm[:,2]<.0001)&((lo[:,1]<-48.9)|(lo[:,0]<-42.4)),1,'source_visible_overhang_edges_and_underside_not_top')
 for x in range(-40,41,8):paint(box(x-.7,x+.7,-54.5,-46.5,39,41),1,'source_existing_white_soffit_ribs')
 paint(zz(47,47.9)&(plane(1,-53.5)|plane(0,-46)),4,'source_dark_coping_front_left_vertical_edge_only_original_simplified_offset')
 paint(box(-15,15,-65,-59,3,4)|box(-13,13,-60.5,-55.5,3,5),5,'source_shortened_gray_entry_steps')
 paint(hi[:,2]<=3.0001,0,'unsplit_base_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU Bailing Front Historical Pre-2025 Appearance original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthubailing-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTHU alumni/library historical front-pavilion photographs, pre-2025 renovation context; uncalibrated proxies','scope':'Known front/left white frames and fascia, pale gray tiled piers, unshaded glass proxy from photo1, dark vertical coping edge. Photo2 blinds not white glass; old scan shape only. Roof top, unknown rear/right and unsplit platform neutral; no Hall of Fame crown or interiors.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
