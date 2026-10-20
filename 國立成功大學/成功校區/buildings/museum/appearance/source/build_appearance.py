"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='a5621417d2f2968d814a9c02c37557243711bf2ae739b9465a06f31e72f94c12'
PALETTE=[('neutral_unseen','#AAA79F'),('brick_facade','#A7694F'),('cream_sills_and_gable_edge','#CEC7B1'),('dark_glazed_recess','#526368'),('warm_ochre_arch_and_coping','#AB9364'),('graybrown_front_roof','#64615A'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_sides_and_roof_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 paint(np.all(abs(t[:,:,1]+15.5)<.00025,axis=1)&zz(2.8,31.7),1,'registered_front_wing_brick_wall')
 paint(np.all(abs(t[:,:,1]+18.5)<.00025,axis=1)&zz(2.8,35.7),1,'registered_center_upper_brick_face')
 paint(np.all(abs(t[:,:,1]+19)<.00025,axis=1)&zz(35.5,42.5),1,'registered_central_gable_brick_face')
 paint(np.all(abs(t[:,:,1]+28.5)<.00025,axis=1)&zz(2.8,21.7),1,'registered_front_entrance_projection_brick')
 # Exact existing window recess backs; cream returns do not invent extra frame geometry.
 for x in [-62,-54,-44,-36,-25,-18,18,25,36,44,54,62]:
  scope=(lo[:,0]>=x-2.05025)&(hi[:,0]<=x+2.05025)&(lo[:,1]>=-15.50025)&(hi[:,1]<=-14.89975)
  for z,h in [(6,8),(16,3),(21,8)]:
   paint(scope&zz(z,z+h),2,'existing_front_window_returns_cream')
   paint(scope&np.all(abs(t[:,:,1]+14.9)<.00025,axis=1)&zz(z,z+h),3,'existing_front_window_back_dark_glazing')
  paint((lo[:,0]>=x-2.70025)&(hi[:,0]<=x+2.70025)&(lo[:,1]>=-16.35025)&(hi[:,1]<=-15.14975)&zz(5.4,6.2),2,'existing_raised_window_sill_cream')
 for x in [-9,0,9]:
  w=5.1 if x else 6.3;scope=(lo[:,0]>=x-w/2-.00025)&(hi[:,0]<=x+w/2+.00025)&(lo[:,1]>=-18.50025)&(hi[:,1]<=-17.69975)&zz(24,33.2)
  paint(scope,2,'existing_upper_arch_recess_returns_cream')
  paint(scope&np.all(abs(t[:,:,1]+17.7)<.00025,axis=1),3,'existing_upper_glazed_opening_back_proxy')
 paint((lo[:,0]>=-10.50025)&(hi[:,0]<=10.50025)&(lo[:,1]>=-28.50025)&(hi[:,1]<=-26.49975)&zz(2.8,17.3),4,'existing_entrance_arch_returns_ochre_proxy_no_added_molding')
 paint(np.all(abs(t[:,:,1]+26.5)<.00025,axis=1)&zz(2.8,17.3),0,'deep_closed_portico_proxy_back_neutral_not_shadow')
 paint((lo[:,0]>=-15.50025)&(hi[:,0]<=15.50025)&(lo[:,1]>=-29.00025)&(hi[:,1]<=-14.99975)&zz(21.3,22.5)&(abs(n[:,2])<.1),4,'existing_coping_vertical_edge_ochre')
 paint((hi[:,1]<=-16.39975)&zz(19.6,20.4),4,'existing_front_horizontal_band_ochre_proxy')
 paint((n[:,2]>.05)&(n[:,1]<-.05)&zz(31.4,38.4),5,'visible_front_main_roof_graybrown_from_historical_wide_photo')
 paint((n[:,2]>.05)&zz(35.5,42.5)&(lo[:,0]>=-15.50025)&(hi[:,0]<=15.50025)&(lo[:,1]>=-19.00025)&(hi[:,1]<=-12.99975),2,'existing_gable_thickness_top_as_cream_edge_proxy')
 paint((lo[:,0]>=-2.10025)&(hi[:,0]<=2.10025)&(lo[:,1]>=-19.50025)&(hi[:,1]<=-18.49975)&zz(34.9,39.1),2,'existing_blank_round_disk_pale_no_logo_or_text')
 paint(hi[:,2]<=2.8001,6,'display_base_not_fountain_or_landscape')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU Museum original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'museum-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NCKU 2021 museum article closeup and historical wide photograph posted 2016 with 2008 exhibition banner; capture dates unverified','scope':'Registered front brick and exact recesses; blank disk has no logo; all unseen roof terraces, rear and sides neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
