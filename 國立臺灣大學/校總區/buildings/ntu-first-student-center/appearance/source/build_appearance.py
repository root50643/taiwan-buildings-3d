"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='298bb09f37c4d63867255b3d36e90bfa40b86c0e2e3bb0b7c9cb7498ca9b4c24'
PALETTE=[('neutral_mixed_or_unknown','#AAA79F'),('white_fold_end','#DADDD5'),('bluegray_piers','#8B9DA7'),('charcoal_window_grid','#414342'),('subdued_upper_glass','#AAB5B3'),('red_entry_door','#AD3740'),('muted_brass_handle','#9B8861'),('gray_concrete_steps','#989C95')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_lower_window_panels_wall_bands_and_unseen_roof_sides_rear_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-24.5)&zz(30,38.5),1,'source_white_front_fold_end_not_unknown_roof_top')
 for x in [-60,-36,-12,12,36,60]:paint(box(x-1.2,x+1.2,-26.8,-23.2,3,31),2,'source_bluegray_existing_front_pier')
 for x in [-65,-48,-24,24,48,65]:
  paint(plane(1,-22)&xx(x-7.25,x+7.25)&zz(20,28),4,'source_upper_subdued_window_back')
  for z,h in [(5,10),(20,8)]:
   for dx in [-4,0,4]:paint(box(x+dx-.5,x+dx+.5,-23.7,-22.3,z,z+h),3,'source_existing_dark_window_vertical_grid')
  for z in [9,13,23,26]:paint(box(x-7.25,x+7.25,-23.7,-22.3,z,z+.9),3,'source_existing_dark_window_horizontal_grid')
 # Central upper blank opening lacks actual grid, remains neutral.
 paint(plane(1,-21.75)&xx(-5.5,5.5)&zz(4,17),5,'source_central_red_double_door_back')
 paint(box(-.5,.5,-24.25,-22.75,4,17),5,'source_red_original_door_center_strip')
 for x in [-1.5,1.5]:paint(box(x-1.3,x+1.3,-24.2,-23.4,5.7,8.3),6,'source_original_round_door_handle_muted_brass')
 paint(box(-72,72,-25.25,-22.75,17.5,19.2),7,'source_existing_concrete_band_white_tile_unsplit_omitted')
 paint(box(-18.5,18.5,-34.85,-27.55,2.8,6.3),7,'source_concrete_entry_steps')
 paint(box(-53,-15,-36.5,-27.5,2.8,6.8),7,'source_existing_simplified_concrete_ramp')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU First Student Center original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntufirst-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTU Visitor Center official exterior photograph, uncalibrated proxies; illustration only for shape identity','scope':'Historic front only: white fold end, bluegray piers, existing dark window grid and upper glass, red door/brass handles, gray steps. Mixed lower panels and walls, central missing grid, main roof/sides/rear neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
