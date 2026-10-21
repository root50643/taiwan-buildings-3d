"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='00ebf1b23e588921465c6f693b61f7af51dd7b9b3cec34a80c1c4c919f52df31'
PALETTE=[('neutral_unknown','#AAA79F'),('brick_front_and_broad_piers','#A45F50'),('gray_narrow_piers_and_porch_posts','#A9AAA2'),('white_two_wide_piers','#D5D7CF'),('bluegray_window_glazing_proxy','#6A8590'),('silver_window_reveals_roof_frames','#BCC4C3'),('dark_blue_PV_cells','#435871'),('gray_porch_roof','#777B77')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_rear_sides_flatroof_or_mixed_entry_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.001)&(hi[:,2]<=b+.001)
 def xx(a,b):return (lo[:,0]>=a-.001)&(hi[:,0]<=b+.001)
 def yy(a,b):return (lo[:,1]>=a-.001)&(hi[:,1]<=b+.001)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.001,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-15)&xx(-70,70)&zz(2.3,46.3),1,'registered_front_redbrick')
 for x in range(-65,66,10):paint(box(x-.6,x+.6,-16.95,-15,3,45),2,'existing_narrow_structural_piers_gray')
 for x in range(-60,61,10):paint(box(x-1.6,x+1.6,-17.5,-15,3,43),1,'existing_wide_projecting_piers_brick')
 for x in [-45,45]:paint(box(x-1.9,x+1.9,-17.9,-15,2.4,46.4),3,'two_special_wide_light_vertical_strips')
 for z in [7,21,35]:
  for x in range(-65,66,10):
   for dx in [-2.5,2.5]:
    mask=box(x+dx-1.3,x+dx+1.3,-15,-13.9,z,z+7.5)
    paint(mask,5,'existing_window_reveal_silver_no_added_mullions')
    paint(mask&plane(1,-13.9),4,'registered_discrete_window_back_bluegray_proxy')
 paint(box(-18,18,-28.5,-15,13.7,16.2),2,'porch_underside_pale_gray')
 paint(box(-18,18,-28.5,-15,13.7,16.2)&(abs(n[:,2])<.1),1,'porch_existing_vertical_fascia_brick')
 paint(box(-18,18,-28.5,-15,13.7,16.2)&(n[:,2]>.2),7,'observed_porch_roof_gray')
 for x in [-15.5,15.5]:
  paint(box(x-1.25,x+1.25,-26.75,-23.25,3,16),2,'porch_post_gray')
  paint(box(x-1.55,x+1.55,-27,-23,3,5.4),1,'separate_porch_post_brick_foot')
  paint(box(x-1.7,x+1.7,-27.1,-22.9,15.5,16.5),1,'separate_porch_post_brick_capital')
 paint(box(-18,18,-28.65,-15,16,17.5)&(abs(n[:,2])<.1),1,'existing_porch_low_parapet_brick')
 paint(box(-71,71,-15.5,-14.9,46,47.5),5,'observed_front_roof_band_silver')
 for y in [-5,18]:
  paint(box(-68,68,y-7.5,y+7.5,47,50.2),5,'existing_PV_array_frames_supports_silver_proxy')
  paint(box(-68,68,y-7.5,y+7.5,49,50.2)&plane(2,50.2),6,'actual_two_PV_cell_arrays_top_faces_only_not_generic_roof')
 paint(hi[:,2]<=2.4001,0,'neutral_display_base')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU F2 Architecture Two original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuuf2-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official F2 Architecture Two photos1–2; uncalibrated proxies','scope':'Registered front brick, narrow gray piers, two white wide strips, bluegray window recesses, gray porch posts with red feet and capitals, actual two PV array tops. Unknown rear and mixed central doorway neutral; original flat arrays not changed into observed tilted geometry.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
