"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='13323ab16bb7f7a42864609695fd7b26a80aa4cd52df7d28d6e1d902a0421b9b'
PALETTE=[('neutral_unseen','#AAA79F'),('gray_concrete','#9D9E98'),('green_canopy','#4E8174'),('entry_glazing','#577E7C'),('silver_frames','#B0B5AF'),('warm_taup_door','#8B8070'),('silver_roof','#BCC1BC')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_side_windows_foyer_roof_and_display_base_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0003)&(hi[:,2]<=b+.0003)
 def xx(a,b):return (lo[:,0]>=a-.0003)&(hi[:,0]<=b+.0003)
 def yy(a,b):return (lo[:,1]>=a-.0003)&(hi[:,1]<=b+.0003)
 def plane(y):return np.all(abs(t[:,:,1]-y)<.0003,axis=1)
 def box(x,y,z,w,d,h):return xx(x-w/2,x+w/2)&yy(y-d/2,y+d/2)&zz(z,z+h)
 paint(box(0,-53,2.3,65,29,20)&(n[:,1]<-.99),1,'observed_front_foyer_gray_aggregate_proxy_no_stain_texture')
 paint(box(22,-53,2.3,22,32,28)&(n[:,1]<-.99),1,'observed_raised_front_gray_wall_no_signage')
 paint(box(-15,-67,2.3,32,10,16)&(n[:,1]<.01)&(n[:,2]<.01),4,'existing_entry_box_frame_silver_not_transparent_interior')
 paint(box(-15,-67,18.1,38,15,2),2,'documented_green_canopy_existing_solid_slab')
 paint(xx(-28,-2)&zz(4,16)&plane(-71.3),3,'existing_entry_glazing_back_only_original_mullions_cut_away')
 paint(xx(16,28)&zz(4,22)&plane(-68.4),5,'documented_solid_right_door_taup_not_glass')
 paint(xx(15,29)&yy(-70.5,-68.5)&zz(23,30),4,'existing_semicircular_arch_relief_silver_gray')
 # Source photo shows left slope; right slope is an explicit limited same-roof extrapolation.
 paint(xx(-34,34)&yy(-45,69)&zz(26,35)&(n[:,2]>.5),6,'main_hall_silver_roof_left_observed_right_same_roof_color_extrapolation')
 paint(hi[:,2]<=2.4001,0,'neutral_display_base_not_site_pavement')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU Erping S1 Lotus Aquatic Center original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuus1-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Complete official NUU S1 photo1 EXIF2025; uncalibrated proxies','scope':'Observed entry gray, green canopy, entry glazing, warm solid door, silver arch and main roof. Right roof slope same-material bounded extrapolation; unseen walls and side panes neutral. No tanks, pipes, logos or adjacent housing. Truncated photo2 not used.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
