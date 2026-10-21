"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='9a27d2f8fb8f4dc75fa5ef59e35c959ba8b04fc041635b824b79544780de3bfb'
PALETTE=[('neutral_unknown_or_mixed','#AAA79F'),('silverwhite_horizontal_shades','#CAD0C9'),('warm_ochre_rear_and_portal','#BEA57D'),('dark_neutral_shadow_recess_NOT_glass','#626966'),('gray_concrete_stairs','#969C97'),('palegray_annex_cladding','#B9C2BC'),('silver_entry_strips','#C0C8C3')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_main_roof_sides_mixed_canopy_fascia_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 for i in range(24):
  z=5+i*3.2;paint(box(-70,70,-22.5,-17.5,z,z+1.2),1,'source_original_silverwhite_horizontal_shading_blade')
  z=6.3+i*3.2;paint(plane(1,-18.2)&xx(-67,67)&zz(z,z+1.7),3,'source_deep_shaded_gap_neutral_proxy_NOT_all_glass')
 for x in [-68,68]:paint(box(x-.75,x+.75,-20.4,-18.4,3,83),1,'source_pale_vertical_end_strip')
 for x in [-19,19]:paint(box(x-3,x+3,-34.5,-17.5,3,26),2,'source_ochre_portal_pier_bounded_returns')
 paint(plane(1,-18)&xx(-15,15)&zz(4,23),3,'source_dark_entry_back_neutral_not_full_curtainwall_claim')
 for x in [-10,0,10]:paint(box(x-.5,x+.5,-18.7,-16.9,4,23),6,'source_original_silver_entry_strip')
 paint(plane(1,29)&zz(3,82.8),2,'source_rear_paired_ochre_solid_towers')
 paint(plane(1,27)&xx(-7.5,7.5)&zz(12,82),3,'source_open_stair_recess_neutral_NOT_glass')
 for z in range(15,80,9):paint(box(-7.5,7.5,26.5,29.5,z,z+1.3),4,'source_rear_original_concrete_stair_slabs')
 for x in [-46,-30,30,46]:
  for z in [12,23,34,45,56,67,78]:paint(plane(1,27.75)&xx(x-2.5,x+2.5)&zz(z,z+2),3,'source_rear_small_dark_window_proxy')
 paint(plane(1,37.5)&xx(-66,-28)&zz(3,17.8),5,'source_rear_annex_pale_cladding_face_no_invented_corrugation')
 paint(box(-21,21,-37.85,-29.15,2.8,7),4,'source_gray_entrance_steps')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Yen Tjing Ling Center original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntuyen-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTU official 2010 E63 front and rear photographs, uncalibrated proxies','scope':'Silverwhite original shades, ochre portal and rear towers, neutral dark gaps NOT uniform glass, gray stair slabs and pale annex rear. Main roof/sides and mixed canopy fascia neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
