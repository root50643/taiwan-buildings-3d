"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='a84438bfd7ecb6828472bf3d52783fa75840b96ab3733ca38f35c687a152be82'
PALETTE=[('neutral_unknown','#AAA79F'),('warm_midgray_concrete_ribs_portico','#858580'),('pale_gray_spandrels','#BBBDB8'),('offwhite_existing_frames','#D1D4CB'),('muted_gray_glass','#788A85')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_side_rear_roof_head_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-15)&xx(-68,68)&zz(2.8,63.8),2,'source_pale_front_solid_spandrels')
 for x in range(-66,67,12):
  paint(box(x-1.6,x+1.6,-17.5,-14.5,3,66),1,'source_original_main_vertical_concrete_rib')
  for dx in [-1.5,1.5]:paint(box(x+dx-.45,x+dx+.45,-18,-16,3,66),1,'source_original_paired_fluted_fin')
 for x in range(-60,61,12):
  for z in [6,18,30,42,54]:
   paint(plane(1,-14)&xx(x-4,x+4)&zz(z,z+8),4,'source_recessed_window_back_muted_glass_no_curtain_details')
   paint(box(x-.5,x+.5,-15.75,-14.25,z,z+8),3,'source_original_vertical_offwhite_frame')
   paint(box(x-4,x+4,-15.75,-14.25,z+4,z+4.9),3,'source_original_horizontal_offwhite_frame')
 for x in [-27,-9,9,27]:paint(box(x-1.9,x+1.9,-29.5,-22.5,3,42),1,'source_concrete_portico_pier')
 paint(box(-30,30,-36.5,-13.5,40,43.5),1,'source_portico_cap_same_concrete_bounded_top_continuity')
 for x in [-24,-12,0,12,24]:paint(box(x-.75,x+.75,-36.5,-13.5,38.5,40.5),1,'source_portico_soffit_beams')
 paint(hi[:,2]<=3.0001,0,'original_ground_and_step_base_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Agronomy Hall original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntuagron-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTU official 2010 exterior photos, uncalibrated proxies','scope':'Front gray ribs and portico, pale spandrels, offwhite existing frames and muted window backs; portico cap top is bounded same-concrete continuity. Unknown sides/rear/roof and small roof head neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
