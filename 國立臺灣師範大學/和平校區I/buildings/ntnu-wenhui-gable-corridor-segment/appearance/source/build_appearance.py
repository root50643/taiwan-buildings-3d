"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='b9d4bd923b530d2ce1cca72748c607223e1b905a017f1ef39d987b166a1202cb'
PALETTE=[('neutral_unseen','#AAA79F'),('orange_red_brick','#A64E38'),('gray_stone_trim','#A3A59B'),('muted_green_frames','#757F70'),('dark_glazing_proxy','#303B38'),('display_plinth','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_left_roof_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0001)&(hi[:,2]<=b+.0001)
 front=hi[:,1]<=-24.4999
 paint(front&zz(9.5,82.5)&(n[:,1]<-.5)&(hi[:,0]<=40.0001),1,'registered_front_gable_brick')
 paint(front&zz(3,9.8),2,'existing_raised_front_stone_base')
 for x in [-29,9]:
  pier=(lo[:,0]>=x-2.1001)&(hi[:,0]<=x+2.1001)&(lo[:,1]>=-26.9001)&(hi[:,1]<=-23.4999)&zz(10,44)
  paint(pier,1,'existing_front_brick_pier')
  paint((lo[:,0]>=x-3.0001)&(hi[:,0]<=x+3.0001)&(hi[:,1]<=-23.4999)&zz(44,47),2,'existing_pier_stone_cap')
 paint((lo[:,0]>=-28.0001)&(hi[:,0]<=2.0001)&(hi[:,1]<=-23.9499)&zz(41.4,45.75),2,'existing_decorated_lintel_and_six_simplified_round_reliefs')
 for x in [-43,-19,-7,25]:
  outer=(lo[:,0]>=x-5.1001)&(hi[:,0]<=x+5.1001)&(lo[:,1]>=-25.5501)&(hi[:,1]<=-22.9499)&zz(12,41)
  paint(outer,2,'existing_tall_opening_stone_surround')
  back=(lo[:,0]>=x-4.1001)&(hi[:,0]<=x+4.1001)&zz(12,41)&np.all(abs(t[:,:,1]+23.25)<.00015,axis=1)
  paint(back,4,'existing_tall_window_recess_back')
  frame=(lo[:,0]>=x-4.1001)&(hi[:,0]<=x+4.1001)&zz(12,41)&(lo[:,1]>=-24.7501)&(hi[:,1]<=-23.3499)
  paint(frame,3,'existing_window_mullion_green_gray')
 r=np.sqrt((t[:,:,0]+11)**2+(t[:,:,2]-64)**2)
 ring=(r.max(axis=1)<=7.6002)&(r.min(axis=1)>=6.3998)&(hi[:,1]<=-24.3499)
 paint(ring,2,'existing_round_window_stone_border')
 paint((r.max(axis=1)<=6.4002)&np.all(abs(t[:,:,1]+23.7)<.00015,axis=1),4,'existing_round_recess_back')
 paint((r.max(axis=1)<=6.4002)&(lo[:,1]>=-25.1001)&(hi[:,1]<=-23.0999)&~np.all(abs(t[:,:,1]+23.7)<.00015,axis=1),3,'existing_six_point_motif_green_gray_no_new_ornament')
 # Only actual front roof fascia, not the unseen full roof surface.
 paint(np.all(abs(t[:,:,1]+27)<.00015,axis=1)&zz(39,85),2,'existing_front_fascia_light_stone_proxy_no_separate_tile_edge')
 # Visible frontmost arcade stone column only; deeper corridor and roof remain neutral.
 paint((lo[:,0]>=55.0999)&(hi[:,0]<=62.9001)&(lo[:,1]>=-23.9001)&(hi[:,1]<=-16.0999)&zz(3,43),2,'frontmost_arcade_stone_column')
 paint(hi[:,2]<=3.0001,5,'display_base_not_real_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTNU Wenhui Gable Corridor original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'wenhui-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NTNU 2011 and 2023 photographs approximations, not measured material swatches','scope':'2011 and 2023 registered gable front; roof top, rear, left and deeper corridor neutral; original simplified ornaments retained.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
