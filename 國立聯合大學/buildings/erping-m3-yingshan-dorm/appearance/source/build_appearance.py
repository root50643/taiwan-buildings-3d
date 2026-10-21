"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='e8d8de5411c9b28cdcae08ad3c927a747902196f2227312b26d66669f99e06ac'
PALETTE=[('neutral_unknown','#AAA79F'),('light_gray_concrete','#B4B5AF'),('pale_window_frames_louvers','#D0D4CF'),('muted_blue_gray_glazing','#6F858B'),('silver_grid_bridge_rails','#9FA9AC'),('muted_tan_entry_edge','#A4936B'),('dark_entry_proxy','#6C7373')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_rear_end_roof_or_occluded_surface_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.003,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-9)&xx(-68,69)&zz(2.3,67.3),1,'documented_main_and_right_front_concrete')
 paint(box(-70.5,-51.5,-12.2,-11.4,2.3,69.3),1,'documented_left_tower_front_including_arch_recess')
 paint(box(-67.05,-54.95,-12.45,-11.35,8,51.5),2,'documented_offwhite_louver_panel')
 for x in [-36,-25,-14,-3,8,19,30]:
  for row in range(5):
   z=4.6+row*10.2
   paint(box(x-5.1,x+5.1,-13.4,-8.5,z,z+8.8),1,'faceted_bay_concrete_spandrel_cap_not_all_glass')
   paint(plane(1,-12.55)&xx(x-2.7,x+2.7)&zz(z+3,z+7.5),3,'front_bay_discrete_glazing_back')
   paint(box(x-.4,x+.4,-13.575,-12.425,z+2.95,z+7.55),2,'existing_white_bay_mullion')
   paint(box(x-2.75,x+2.75,-13.575,-12.425,z+6.24,z+7.04),2,'existing_white_bay_transom')
   for side in [-1,1]:
    ang=np.deg2rad(-side*32.6);qx=t[:,:,0]-(x+side*3.95);qy=t[:,:,1]+11.75;u=qx*np.cos(ang)+qy*np.sin(ang);v=-qx*np.sin(ang)+qy*np.cos(ang)
    paint(np.all(abs(v-.5)<.003,axis=1)&np.all(abs(u)<=1.003,axis=1)&zz(z+3,z+7.5),3,'existing_splayed_side_pane_back_only')
 for row in range(5):
  z=5+row*10.2
  for x,y,z0,w,h,d,m in [(46,-9.1,z+2.6,16.1,5.6,1.15,3),(-46,-9.1,z+.5,9,9,1.2,2)]:
   paint(plane(1,y+d/2)&xx(x-w/2,x+w/2)&zz(z0,z0+h),3,'documented_end_strip_discrete_window_back')
   for k in range(1,m+1):
    q=x-w/2+w*k/(m+1);paint(box(q-.4,q+.4,y+.05-(d+.15)/2,y+.05+(d+.15)/2,z0-.05,z0+h+.05),2,'existing_pale_end_strip_mullion')
   paint(box(x-w/2-.05,x+w/2+.05,y+.05-(d+.15)/2,y+.05+(d+.15)/2,z0+h*.72,z0+h*.72+.8),2,'existing_pale_end_strip_transom')
 paint(plane(1,-8.4)&xx(38,54)&zz(24.9,34.4),6,'entry_recess_dark_proxy_not_asserted_glass')
 for x in [40,46,52]:paint(box(x-.45,x+.45,-9.9,-8.3,24.9,34.5),2,'existing_entry_frame')
 paint(box(36.9,55.1,-12.4,-8.2,34.5,35.7),1,'entry_hood_gray_concrete')
 paint(box(35.5,36.7,-10.3,-8.9,24,57.5),5,'documented_narrow_tan_contrasting_edge')
 paint(box(38,54,-10.6,-8.8,54.1,57.6),1,'blank_plaque_no_gold_lettering')
 paint(box(-58.7,29,-6,20,58,62.8),4,'documented_exposed_metal_grid_NOT_PV_no_cover')
 paint(box(36.9,71,-34.1,-8.7,23.4,25.3),1,'documented_gray_bridge_slab_not_tree_shadow')
 for x in [37.5,54.5]:paint(box(x-.6,x+.6,-33.8,-11,25.1,29.7),4,'existing_bridge_rails_metal')
 paint(hi[:,2]<=2.4001,0,'neutral_original_base_no_landscape')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU M3 Yingshan Dormitory original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuum3-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official M3 front and accommodation-centre panorama; uncalibrated proxies','scope':'Documented front gray concrete and faceted bay spandrels, pale frames/louvers, precise discrete front/side panes, tan entrance edge and exposed silver rooftop grid NOT PV. Unknown rear right return and roof apparatus neutral; no extra water tanks or lettering.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
