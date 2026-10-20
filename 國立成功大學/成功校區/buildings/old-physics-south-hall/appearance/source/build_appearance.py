"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='9863599d487c595e276ad781dd44943b86451ff5c20ef3a8c7871788b90d944f'
PALETTE=[('neutral_unseen','#AAA79F'),('redbrown_brick','#AB775E'),('pale_warm_gray_eaves','#BEB9A5'),('teal_green_frames_and_door','#528F7C'),('muted_glazing_proxy','#6E8483'),('warm_ochre_canopy','#A48C66'),('gray_entry_steps','#969B94'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_ends_and_roof_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 paint(np.all(abs(t[:,:,1]+18)<.00025,axis=1)&zz(3,29.9),1,'registered_front_redbrown_brick_field')
 for x in [-63,-54,-45,-36,-27,-18,0,9,18,27,36,45,54,63]:
  frame=(lo[:,0]>=x-2.77525)&(hi[:,0]<=x+2.77525)&(lo[:,1]>=-18.00025)&(hi[:,1]<=-17.24975)
  paint(frame&(zz(7,18.8)|zz(21,26.3)),3,'existing_window_recess_returns_and_solid_mullion_strips_teal')
  for dx in [-1.55,1.55]:
   scope=(lo[:,0]>=x+dx-1.22525)&(hi[:,0]<=x+dx+1.22525)&np.all(abs(t[:,:,1]+17.25)<.00025,axis=1)
   for z,h in [(7,5.5),(13.2,5.6),(21,2.3),(24,2.3)]:paint(scope&zz(z,z+h),4,'existing_pane_recess_back_muted_glazing_not_photo_black_shadow')
 paint((lo[:,0]>=-12.25025)&(hi[:,0]<=-5.74975)&(lo[:,1]>=-18.00025)&(hi[:,1]<=-17.09975)&zz(5.5,21.5),3,'existing_center_door_recess_teal_proxy_no_invented_leaf_or_panels')
 paint((lo[:,0]>=-14.50025)&(hi[:,0]<=-3.49975)&(lo[:,1]>=-23.00025)&(hi[:,1]<=-16.99975)&zz(22,23.3),5,'existing_entry_canopy_ochre')
 paint((lo[:,0]>=-14.50025)&(hi[:,0]<=-3.49975)&(lo[:,1]>=-25.00025)&(hi[:,1]<=-16.99975)&zz(3,5.9),6,'existing_entry_steps_gray')
 paint(np.all(abs(t[:,:,1]+20)<.00025,axis=1)&zz(28.6,30.4),2,'existing_front_eave_vertical_edge_pale_warm_gray')
 paint(hi[:,2]<=3.0001,7,'display_base_not_ground_or_plinth')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU Old Physics South Hall original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'physics-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NCKU front and doorway photos posted 2023-11-13; embedded DateTimeOriginal 2023-11-12, timezone and exact capture date unverified','scope':'Registered single-storey front brick and teal frames/door, existing ochre canopy; back repetition and all roof remain neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
