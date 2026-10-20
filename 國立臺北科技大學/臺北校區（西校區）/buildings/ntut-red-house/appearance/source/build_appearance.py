"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='5abe643a0f599bd4c032421ca4554a7da47b9c6d95a73a0c9423b8ee5acb2425'
PALETTE=[('neutral_unregistered','#AAA79F'),('orange_red_brick','#AF6048'),('gray_rendered_stone','#999C95'),('pale_frames_and_columns','#D4D4C6'),('dark_glazing_proxy','#53616A'),('dark_main_roof_tiles','#555D5F'),('brown_copper_porch','#825A4A'),('display_plinth','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_positive_x_side_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00015)&(hi[:,2]<=b+.00015)
 registered=(hi[:,1]<=-53.9998)|(lo[:,1]>=61.9998)|(hi[:,0]<=-42.9998)
 paint(registered&zz(10.8,76.2),1,'registered_east_west_and_negative_x_brick')
 paint(registered&zz(3,11.6),2,'registered_stone_foundation')
 paint(registered&zz(72.2,79),2,'existing_gray_frieze_and_cornice')
 # Both photographed end parapets, not the sloping tile planes.
 paint(((hi[:,1]<=-52.9998)|(lo[:,1]>=60.9998))&(lo[:,2]>=76),2,'registered_gray_end_gable_and_coping')
 # Only the photographed negative-X main roof slope; the other slope neutral.
 paint((hi[:,0]<=.0002)&(c[:,1]>-53)&(c[:,1]<61)&(lo[:,2]>=76.5998)&(n[:,2]>.1)&(n[:,0]<-.1),5,'registered_negative_x_tile_slope')
 for y in [-54,62]:
  for x in [-17.3,0,17.3]:
   for z,h in ([(46,21)] if y<0 else [(46,21),(12,18)]):
    reg=(lo[:,0]>=x-4.8502)&(hi[:,0]<=x+4.8502)&zz(z,z+h)&(lo[:,1]>=y-2.1002)&(hi[:,1]<=y+2.1002)
    paint(reg,3,'existing_end_window_frame_and_mullion_pale')
    back=y+(2.1 if y<0 else -2.1)
    paint(reg&np.all(abs(t[:,:,1]-back)<.0002,axis=1),4,'existing_end_recess_back_glazing')
 for y in [-25.25,-5.75,13.75,33.25]:
  for z,h in [(46,21),(12,18)]:
   reg=(lo[:,1]>=y-5.3502)&(hi[:,1]<=y+5.3502)&zz(z,z+h)&(lo[:,0]>=-45.1002)&(hi[:,0]<=-40.8998)
   paint(reg,3,'existing_negative_x_side_window_mullion_pale');paint(reg&np.all(abs(t[:,:,0]+40.9)<.0002,axis=1),4,'existing_negative_x_side_recess_back_glazing')
 for y in [-54.5,62.5]:paint((lo[:,0]>=-9.7002)&(hi[:,0]<=9.7002)&zz(85.7,94.2)&(lo[:,1]>=y-2.2502)&(hi[:,1]<=y+2.2502),3,'existing_paired_pointed_attic_grille_pale')
 door=(lo[:,0]>=-9.0002)&(hi[:,0]<=9.0002)&zz(3.2,31.2)&(lo[:,1]>=-56.2002)&(hi[:,1]<=-51.7998)
 paint(door,3,'existing_east_door_mullions_pale');paint(door&np.all(abs(t[:,:,1]+51.8)<.0002,axis=1),4,'existing_east_door_back_glazing')
 for x in [-18.3,18.3]:paint((lo[:,0]>=x-2.8002)&(hi[:,0]<=x+2.8002)&(lo[:,1]>=-71.3002)&(hi[:,1]<=-65.6998)&zz(3.4,33.2),3,'existing_two_porch_columns_pale')
 paint((lo[:,0]>=-22.0002)&(hi[:,0]<=22.0002)&(hi[:,1]<=-51.9498)&zz(32.6,44.1),6,'existing_porch_copper_roof_and_fascia_brown_not_green')
 paint((hi[:,1]<=-54)&zz(2.9,4.1),2,'existing_porch_platform_stone')
 # Blank tablet stays neutral; no gold board/lettering recreated.
 paint((lo[:,0]>=10.7998)&(hi[:,0]<=15.0002)&(hi[:,1]<=-53.4998)&zz(13.7,28.2),0,'blank_tablet_not_given_invented_text')
 paint(hi[:,2]<=3.0001,7,'display_base_not_real_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTUT Red House original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntut-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated NTUT official restored exterior and Taipei City west-end photograph, capture dates unconfirmed approximations, not measured material swatches','scope':'Registered east entry, west gable and negative-X long side; brown porch roof, gray gables, other long side neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
