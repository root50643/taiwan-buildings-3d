"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='2adb78809384750589d56806aac33da2eafe03bd5fd3209700cb81f898569b0d'
PALETTE=[('neutral_unknown','#AAA79F'),('warm_ivory_background','#CFC9B9'),('gray_beige_projected_bays','#B5B4A8'),('muted_blue_green_glazing','#698A92'),('silver_gray_existing_frames','#A3ADAF'),('dark_gray_entry_canopy','#626D70')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_roof_rear_depth_ground_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.003,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-8.5)&xx(-66.5,66.5)&zz(2.8,67.8),1,'source_background_warm_ivory_wall')
 paint(plane(1,-23.5)&xx(-68,-56)&zz(2.8,74.3),1,'source_left_blank_front_endpier')
 paint(plane(1,-21.5)&xx(56,68)&zz(2.8,76.3),1,'source_right_blank_front_endpier')
 paint(plane(1,-22.5)&xx(-9.5,9.5)&zz(3,75),4,'existing_central_stack_solid_grid_silver_gray_NOT_continuous_glass')
 for x,h in [(-54,24),(-45,24),(-36,44),(-27,44),(-18,71),(-9,71),(18,77),(27,77),(36,46),(45,46),(54,25),(63,25)]:
  paint(box(x-4.5,x+4.5,-27,-25,3,h+3)&(abs(n[:,2])<.1),2,'source_gray_beige_bay_front_and_beveled_spandrels')
  for z in np.arange(5.2,h+1,7.25):
   if z+3.3>h+2:continue
   paint(plane(1,-26.25)&xx(x-2.8,x+2.8)&zz(z,z+3.3),3,'existing_flat_bay_window_back')
   for sign in [-1,1]:
    ang=np.deg2rad(sign*40);dx=t[:,:,0]-(x+sign*3.45);dy=t[:,:,1]+26
    u=dx*np.cos(ang)+dy*np.sin(ang);v=-dx*np.sin(ang)+dy*np.cos(ang)
    paint(np.all(abs(v-.65)<.004,axis=1)&np.all(abs(u)<=1.004,axis=1)&zz(z,z+3.3),3,'existing_angled_bay_recess_back_local_cut_plane')
 for z in np.arange(5.5,73,7.25):
  for x in [1.1,6.4]:paint(plane(1,-21.75)&xx(x-2.1,x+2.1)&zz(z,z+4.2),3,'central_stack_existing_pane_back_only')
 for x,minz in [(-48,29),(-35,49),(42,51),(54,30)]:
  for z in np.arange(6,62,7.25):
   if z>=minz:paint(plane(1,-7.75)&xx(x-5.25,x+5.25)&zz(z,z+4.5),3,'visible_background_discrete_window_back')
 for z in [28.8,51.2,67.2]:paint(box(-4.3,14.3,-24,-22.2,z,z+1.4),4,'existing_central_horizontal_break_silver_gray')
 paint(plane(1,-21.5)&xx(.6,9.4)&zz(3,9.7),5,'entry_dark_recess_proxy')
 paint(box(-3,13,-24.4,-22,8.1,11.75),5,'source_dark_gray_curved_canopy')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NHRI Zhunan Phase Two Dormitory original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nhridorm2-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Reiju contractor complete front exterior photograph; uncalibrated proxies','scope':'Ivory background front, gray-beige bay spandrels, existing flat/angled blue-green window backs, silver-gray simplified central grid and dark entry canopy. Unknown side/depth/rear/roof neutral. No curtain or interior detail; completion date is not photo date.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
