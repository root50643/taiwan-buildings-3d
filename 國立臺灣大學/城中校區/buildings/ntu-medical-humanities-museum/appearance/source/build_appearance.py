"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='931bee1b74562d474606610a63bc63bb96c6da3fe0da8ce9f1b6c9af0d3d8718'
PALETTE=[('neutral_unseen','#AAA79F'),('warm_cream_arcade_and_trim','#D0CBAC'),('red_brown_brick','#9C6D5C'),('mint_metal_roof','#A3C4AF'),('dark_gray_band','#737B78'),('dark_brown_window_frames','#665745'),('muted_glazing','#70878A'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_rear_and_return_walls_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def xx(a,b):return (lo[:,0]>=a-.00025)&(hi[:,0]<=b+.00025)
 def yy(a,b):return (lo[:,1]>=a-.00025)&(hi[:,1]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 paint(plane(1,-23)&zz(3,38.8),1,'central_front_wall_cream_base')
 paint(plane(1,-23)&zz(23,38),2,'central_upper_arch_spandrel_existing_brick_faces')
 paint(plane(1,-25)&zz(38,55)&xx(22,56),2,'existing_central_gable_front_brick_no_invented_coping_strip')
 # Observed west front arcade remains cream even its shallow recess backs.
 paint(xx(-68,16.5)&yy(-15.85,-12.9)&zz(3,37),1,'west_arcade_cream_wall_columns_and_recesses_not_glass')
 paint(xx(61.5,71.5)&plane(1,-14.5)&zz(3,37.8),1,'small_east_front_stub_cream')
 for x in [28,39,50]:
  for z,h in [(5,13),(23,13)]:
   paint(xx(x-5.15,x+5.15)&yy(-24.8,-21.7)&zz(z-.4,z+h+.8)&~plane(1,-23),1,'existing_central_arch_surround_cream')
   paint(xx(x-4.2,x+4.2)&plane(1,-21.3)&zz(z,z+h),6 if z==23 else 1,'upper_actual_window_back_glazing' if z==23 else 'lower_arcade_recess_cream_not_glass')
  paint(xx(x-4.4,x+4.4)&yy(-23.9,-21.9)&zz(28,29),5,'existing_upper_window_horizontal_brown_frame')
  paint(xx(x-.5,x+.5)&yy(-23.8,-21.6)&zz(23,35),5,'existing_upper_window_vertical_brown_frame')
 for x in [21,33.5,44.5,57]:
  paint(xx(x-1.4,x+1.4)&yy(-25.5,-22.5)&zz(21,38.5),1,'original_central_columns_caps_and_bases_cream')
 for z,w in [(20.5,44),(38,47)]:paint(xx(39-w/2,39+w/2)&yy(-25.2,-22.2)&zz(z,z+(2 if z==20.5 else 1.8)),1,'existing_central_horizontal_cream_bands')
 for x in [-59,-47,-35,-23,-11,1]:paint(xx(x-6,x+6)&yy(-16,-14)&zz(21.5,23.5),4,'existing_west_arcade_horizontal_dark_gray_band')
 paint(xx(36,42)&yy(-26.1,-23.5)&zz(47,53),1,'round_medallion_trim_and_back_pale_not_black_hole')
 # Public aerial directly documents the connected mint sheet-metal roof volumes.
 paint(yy(-24,65)&zz(38.3,51.3)&(n[:,2]>.1)&(n[:,2]<.999),3,'aerial_registered_mint_metal_roof_slopes_not_gray_tile')
 paint(plane(2,46.3)|plane(2,51.3)|plane(2,45.3),3,'original_flat_hip_roof_ridge_tops_mint')
 paint(plane(1,-16)&zz(37,38.7),1,'west_front_eaves_cream_only')
 paint(hi[:,2]<=3.0001,7,'display_base_not_site_paving')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Medical Humanities Museum Central Block And West Wing original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'medical-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official museum front image and original photographer 2023-posted series; actual photo dates unknown','scope':'Central facade and west front arcade, original mint roof volumes registered to aerial. Lower and west arcade recesses are not glazing. Unknown return/rear walls neutral; no invented pediment coping or sign.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
