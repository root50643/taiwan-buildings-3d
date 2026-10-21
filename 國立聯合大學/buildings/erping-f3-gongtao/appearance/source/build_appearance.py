"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='1a2d5f2d7c8a07f8b613266e3e0b283d88ea10f76551e01e06656b2c1ca8ea7d'
PALETTE=[('neutral_unknown','#AAA79F'),('pale_gray_front_infill','#B9BBB7'),('dark_slate_louver_relief','#535E68'),('dark_window_frames','#414B52'),('muted_grayblue_glazing_proxy','#8798A3'),('cream_closed_entry_shutter','#B8B29F'),('stone_entry_fascia','#A3A7A3'),('silver_visible_roof_supports','#AEB7B9')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_rooftop_PV_unconfirmed_rear_sides_and_mixed_paving_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.001)&(hi[:,2]<=b+.001)
 def xx(a,b):return (lo[:,0]>=a-.001)&(hi[:,0]<=b+.001)
 def yy(a,b):return (lo[:,1]>=a-.001)&(hi[:,1]<=b+.001)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.001,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-4)&xx(-70,70)&zz(7.2,65.2),1,'front_light_gray_infill_and_spandrels')
 for x in range(-54,67,12):paint(box(x-.95,x+.95,-6.5,-4,8,64),1,'original_narrow_pale_structural_pier')
 for x in [-48,-36,-24,-12,12,24,36,48,60]:
  paint(box(x-2.4,x+2.4,-5.5,-4,8,63),2,'source_dark_louver_column_mass_original_simplification')
  for q in [x-1.6,x,x+1.6]:paint(box(q-.4,q+.4,-6.7,-4.9,8,63),2,'original_thick_louver_rods_dark_slate_not_added_detail')
 for z in [12,26,40,54]:
  for x in [-58,-42,-30,-18,-6,2,18,30,42,54]:
   paint(box(x-3.25,x+3.25,-4,-2.8,z,z+7.5),3,'existing_window_reveals_dark_frame_proxy')
   paint(xx(x-3.25,x+3.25)&zz(z,z+7.5)&plane(1,-2.8),4,'discrete_window_recess_back_muted_grayblue')
   paint(box(x-3.25,x+3.25,-5.7,-4,z+5.8,z+6.6),3,'existing_horizontal_window_mullion')
   paint(box(x-.4,x+.4,-5.7,-4,z,z+7.2),3,'existing_vertical_window_mullion')
  for x in [-67,-63,-59]:paint(xx(x-1.35,x+1.35)&zz(z+3,z+6.7)&plane(1,-2.85),4,'left_service_small_window_recess')
 paint(box(-6.5,6.5,-5.7,-2.65,10.5,21.5),5,'observed_closed_cream_entry_and_retained_overlapping_original_window_relief_not_glazing')
 for x in [-8.7,8.7]:paint(box(x-1.5,x+1.5,-11,-4,7,24),2,'source_dark_entry_cheeks_no_lettering')
 paint(box(-10.25,10.25,-11.5,-4,21.8,25.2),6,'entry_stone_lintel_blank_no_name')
 paint(box(-71.5,71.5,-5,-4,65,70.2),6,'front_broad_gray_roof_fascia')
 paint(box(-70,70,-2,38,70,75.3)&(hi[:,2]<=75.001),7,'only_visible_metal_roof_supports_and_underside_not_PV_top_claim')
 paint(hi[:,2]<=7.3001,0,'neutral_terrace_no_unsegmented_red_paving')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU F3 Gongtao Hall original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuuf3-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official F3 Gongtao Hall photos4–5; uncalibrated proxies','scope':'Front pale infill, dark original louvers, discrete grayblue window backs with original dark mullions, cream closed entry. Existing photos show canopy underside only: rooftop neutral and no PV claim despite historical source naming. Unseen sides and mixed paving neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
