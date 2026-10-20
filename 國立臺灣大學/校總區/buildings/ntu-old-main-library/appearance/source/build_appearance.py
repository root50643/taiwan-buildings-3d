"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='5d1e1f4997cd25592fdd88fec6b6f15cceab4cf11d9ffd95ab925cb08d65ee42'
PALETTE=[('neutral_unseen','#AAA79F'),('redbrown_brick','#A77F68'),('gray_stone_surround_and_bands','#A5ABA4'),('pinkish_sandstone_lower_arches','#B59A8E'),('dark_brown_mullions','#62504A'),('muted_bluegray_glazing','#718B92'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_rear_roof_sides_and_deep_portico_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0002)&(hi[:,2]<=b+.0002)
 paint((hi[:,1]<=-13.9998)&zz(3,45),1,'registered_front_brick_and_existing_wing_brick_arch_relief')
 paint(np.all(abs(t[:,:,1]+27.5)<.0002,axis=1)&zz(3,16.3),0,'deep_loggia_closed_proxy_back_neutral_not_shadow')
 for x in [-59,-49,-39,-29,29,39,49,59]:
  scope=(lo[:,0]>=x-2.6002)&(hi[:,0]<=x+2.6002)
  paint(scope&np.all(abs(t[:,:,1]+13.15)<.0002,axis=1)&zz(19,32),5,'existing_upper_wing_window_back_bluegray_not_stone_arch')
  paint(scope&np.all(abs(t[:,:,1]+13.25)<.0002,axis=1)&zz(5,14),5,'existing_lower_wing_window_back_bluegray')
 paint((lo[:,0]>=-7.3502)&(hi[:,0]<=7.3502)&(lo[:,1]<-19.5002)&zz(20,35.85),2,'existing_central_tall_arch_surround_gray')
 paint((lo[:,0]>=-6.5002)&(hi[:,0]<=6.5002)&np.all(abs(t[:,:,1]+18.6)<.0002,axis=1)&zz(20,35),5,'central_tall_window_recess_back_bluegray')
 for x in [-16,16]:
  scope=(lo[:,0]>=x-2.1002)&(hi[:,0]<=x+2.1002)&(lo[:,1]>=-19.5002)&(hi[:,1]<=-18.6998)&zz(20,32)
  paint(scope,2,'existing_flank_lancet_returns_pale_stone')
  paint(scope&np.all(abs(t[:,:,1]+18.7)<.0002,axis=1),5,'existing_flank_lancet_recess_back_bluegray')
 for x in [-3.5,0,3.5]:paint((lo[:,0]>=x-.4502)&(hi[:,0]<=x+.4502)&(lo[:,1]>=-19.6002)&(hi[:,1]<=-18.5998)&zz(20,30),4,'existing_central_vertical_mullions_dark_brown')
 for z in [24,28]:paint((lo[:,0]>=-6.2502)&(hi[:,0]<=6.2502)&(lo[:,1]>=-19.6002)&(hi[:,1]<=-18.5998)&zz(z,z+.9),4,'existing_central_horizontal_mullions_dark_brown')
 for x in [-13,0,13]:paint((lo[:,0]>=x-5.3502)&(hi[:,0]<=x+5.3502)&(lo[:,1]<-31.0002)&zz(3,17.15),3,'existing_lower_three_arch_relief_pinkish_sandstone')
 paint((hi[:,1]<=-29.6998)&(lo[:,0]>=-20.5002)&(hi[:,0]<=20.5002)&zz(18.5,20),2,'existing_loggia_top_ledge_gray')
 paint(np.all(abs(t[:,:,1]+15)<.0002,axis=1)&zz(34,35.3),2,'existing_upper_wing_front_cornice_gray')
 paint((n[:,2]>.05)&(lo[:,2]>=35.9998)&(hi[:,2]<=45.0002)&(hi[:,1]<=-10.4998)&(lo[:,0]>=-22.501)&(hi[:,0]<=22.501),2,'existing_central_gable_top_edge_gray_proxy')
 paint(np.all(abs(t[:,:,1]+18.4)<.0002,axis=1)&zz(37.1,40.9)&(lo[:,0]>=-1.9002)&(hi[:,0]<=1.9002),4,'existing_round_vent_recess_dark_no_new_slats')
 paint((hi[:,1]<=-30.9998)&zz(2.8,4.9)&(lo[:,0]>=-21.5002)&(hi[:,0]<=21.5002),2,'existing_entry_steps_gray')
 paint(np.all(abs(t[:,:,2]-19.4)<.0002,axis=1)&(n[:,2]>.9),0,'unseen_loggia_roof_top_neutral')
 paint(hi[:,2]<=3.0001,6,'display_base_not_landscape')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Old Main Library original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'oldlib-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NTU visitor center old library photograph; embedded DateTimeOriginal 2021-07-19 17:33:31, timezone unprovided and not independently verified approximations, not measured material swatches','scope':'Registered front brick, central gray arch and pink lower arch relief, dark existing mullions; wing arch relief remains brick; roof rear neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
