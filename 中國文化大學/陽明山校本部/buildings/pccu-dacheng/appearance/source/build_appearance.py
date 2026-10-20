"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='07da76ed20707136c210dd8322674695ce0090a56ba4bc4d4ed10ab7bdc7f4cf'
PALETTE=[('neutral_unseen','#A39F98'),('front_gray_wall','#92938F'),('front_roof_green_tile','#718568'),('red_eave_and_panel','#9B433B'),('pale_stone_columns_rails','#C7C6B9'),('dark_glazing_proxy','#384C4E'),('warm_door_frame_proxy','#8C704E'),('display_plinth','#898A86')]
def classify(tri):
 # Authored geometric coordinates in metres; STL remains unmodified millimetres.
 t=tri.copy();t[:,:,:2]/=2.6;t[:,:,2]=(t[:,:,2]-1.6)/2.6
 c=t.mean(axis=1);lo=t.min(axis=1);hi=t.max(axis=1)
 normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);normal/=np.linalg.norm(normal,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_surface_neutral',dtype=object)
 def paint(mask,n,reason):color[mask]=n;why[mask]=reason
 def in_z(a,b):return (lo[:,2]>=a-.0001)&(hi[:,2]<=b+.0001)
 def plane(axis,value):return np.all(abs(t[:,:,axis]-value)<.0001,axis=1)
 paint((c[:,1]<-18)&(normal[:,1]<-.9)&in_z(.72,15.9),1,'visible_front_wall_gray_proxy')
 # Only the front roof is registered to the photo; other three roofs stay neutral.
 front_roof=(lo[:,0]>=-13.5001)&(hi[:,0]<=13.5001)&(lo[:,1]>=-24.9001)&(hi[:,1]<=-8.0999)&(lo[:,2]>=15.7199)
 paint(front_roof&(normal[:,2]>.01)&(lo[:,2]>=16.1999),2,'front_roof_tile_material_continuity_proxy')
 paint(front_roof&(lo[:,2]>=19.1999),2,'existing_front_roof_ridge_green_tile_proxy')
 paint(front_roof&(c[:,1]<-16.5)&(normal[:,2]<=.01)&(hi[:,2]<=16.301),3,'visible_front_roof_eave_red_proxy')
 paint((lo[:,0]>=-12.6001)&(hi[:,0]<=12.6001)&(lo[:,1]>=-22.6501)&(hi[:,1]<=-22.0499)&in_z(15.75,16.45)&(normal[:,2]<.1),3,'existing_front_gallery_eave_beam')
 # Round columns, classified from their exact existing finite cylinders.
 for x in [-5.7,-1.9,1.9,5.7]:
  paint((lo[:,0]>=x-.3301)&(hi[:,0]<=x+.3301)&(lo[:,1]>=-24.5301)&(hi[:,1]<=-23.8699)&in_z(.55,9.1),4,'existing_front_portico_column')
 for x in np.linspace(-11.7,11.7,7):
  paint((lo[:,0]>=x-.2401)&(hi[:,0]<=x+.2401)&(lo[:,1]>=-22.5901)&(hi[:,1]<=-22.1099)&in_z(12.8,15.75),4,'existing_front_upper_gallery_column')
 # Existing railing bands/posts only; do not paint broad floor slabs as balustrades.
 paint((lo[:,1]>=-22.5701)&(hi[:,1]<=-22.1299)&(lo[:,0]>=-12.7201)&(hi[:,0]<=12.7201)&in_z(12.9,13.98),4,'existing_front_high_railing')
 paint((lo[:,1]>=-24.5201)&(hi[:,1]<=-24.0799)&(lo[:,0]>=-9.4201)&(hi[:,0]<=9.4201)&in_z(9,10.08),4,'existing_front_middle_railing')
 for x0,x1 in [(-24.5,-9.5),(9.5,24.5)]:
  for axis,value in [(1,-25.5),(0,x0),(0,x1)]:
   mask=(lo[:,axis]>=value-.2201)&(hi[:,axis]<=value+.2201)&(lo[:,0]>=x0-.2201)&(hi[:,0]<=x1+.2201)&(lo[:,1]>=-25.7201)&(hi[:,1]<=-9.7799)&in_z(9,10.08)
   paint(mask,4,'front_corner_terrace_railing_continuity_proxy')
 # Only backed front recess planes; no fake glass on unseen sides or rear.
 paint(plane(1,-18.65)&in_z(.9,3.6),6,'existing_front_ground_door_back_warm_proxy_no_added_frame')
 paint(plane(1,-18.65)&in_z(4.25,7.8),5,'existing_front_portico_upper_window_back')
 paint(plane(1,-23.48)&in_z(9.4,12.35),5,'existing_front_middle_glazing_back')
 paint(plane(1,-19.95)&in_z(13.35,15.3),5,'existing_front_upper_glazing_back')
 # Existing front corner decorative recesses: plain red, not fabricated lattice.
 for z0,z1 in [(1.5,2.8),(3.7,5),(6,7.1)]:
  paint(plane(1,-25.25)&in_z(z0,z1),3,'existing_front_decorative_recess_plain_red_no_pattern')
 paint(tri[:,:,2].max(axis=1)<=1.6001,7,'display_base_not_real_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'PCCU Dacheng Hall original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'pccu-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official photograph approximations, not measured material swatches','scope':'Front facade and one front roof only; unseen rear, side roofs and court remain neutral. Contiguous front roof and terrace rail materials are bounded extrapolations.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
