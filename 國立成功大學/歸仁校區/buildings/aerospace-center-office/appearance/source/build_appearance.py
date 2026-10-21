"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='cd983ed76d5dcb9d9170afa5d4b0aaaf3c21ff8a05689b7f49ad53a2b65a0271'
PALETTE=[('neutral_unregistered_left_rear_roof','#AAA79F'),('offwhite_tile_concrete_proxy','#C9C9BD'),('dark_gray_window_proxy','#606E6B'),('gray_closed_metal_shutters','#929C98'),('dark_mixed_entry_proxy','#686B67')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_opposite_long_side_rear_roof_base_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.004)&(hi[:,2]<=b+.004)
 def xx(a,b):return (lo[:,0]>=a-.004)&(hi[:,0]<=b+.004)
 def yy(a,b):return (lo[:,1]>=a-.004)&(hi[:,1]<=b+.004)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-64)&xx(-55,55)&zz(2.9,53.9),1,'2010_photo_registered_short_end_offwhite_body_no_weathering_texture')
 paint(plane(0,55)&yy(-64,64)&zz(2.9,53.9),1,'right_long_return_same_tile_system_bounded_extension_not_independent_opposite_side_evidence')
 for y in [-60,-40,-20,0,20,40,60]:paint(box(54.5,56.3,y-1,y+1,27,52),1,'registered_right_upper_uprights_same_body_material')
 paint(box(54.5,56.3,-63.5,63.5,51,53),1,'registered_right_upper_cornice_body_material')
 paint(plane(1,-65.5)&xx(-56.5,56.5)&zz(53,54.6),1,'front_roof_edge_only_no_roof_top_guess')
 paint(plane(0,56.5)&yy(-65.5,65.5)&zz(53,54.6),1,'right_roof_edge_only')
 paint(plane(1,-64.6)&xx(-56,56)&zz(54,56),1,'visible_front_outer_parapet_face')
 paint(plane(0,56)&yy(-63.5,63.5)&zz(54,56),1,'visible_right_outer_parapet_face')
 for x in [-35,0,35]:
  for dx in [-6.75,-2.25,2.25,6.75]:
   for z in [32,39]:paint(plane(1,-62.9)&xx(x+dx-1.8,x+dx+1.8)&zz(z,z+6),2,'2010_short_end_original_discrete_window_back')
 paint(plane(1,-62.85)&xx(-41,-29)&zz(4,24),4,'2010_mixed_dark_entry_back_not_blue_glass_claim')
 for x in [0,35]:
  paint(plane(1,-62.85)&xx(x-10,x+10)&zz(10,21),3,'2010_closed_metal_shutter_not_glass_no_new_slat_geometry')
  paint(box(x-12,x+12,-68.75,-63.25,22,23.2),3,'source_shutter_sheet_hood_simplified_flat_component')
 for y in [-49,-29,-9,11,31,51]:
  for dy in [-4.5,0,4.5]:
   for z in [9,32]:paint(plane(0,53.85)&yy(y+dy-1.75,y+dy+1.75)&zz(z,z+12),2,'right_return_window_system_bounded_extension_no_opposite_mirroring')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU Aerospace Center Office Historical Bounded Appearance original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nckuaero-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NCKU GIS two original JPEG endpoints, camera Original2010-04-09; historical offwhite body and gray closed shutters, no stains baked in','scope':'I023 office exterior only. Registered short end and bounded right long return same material system; lower two short-end openings are metal shutters not glass. Opposite longside, rear, roof and base neutral. Front camera changed to show registered right return, no geometry changed; source model symmetry approximation retained.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
