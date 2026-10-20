"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='d9cf4cdf30717b38c4020395a48a407ad5f97ba61d403871e322fe502021bdd3'
PALETTE=[('neutral_unseen','#AAA79F'),('tan_tile','#BDA68F'),('charcoal_mosaic_proxy','#636662'),('pale_frames','#D0D2C8'),('orange_curved_wall','#C97C50'),('salmon_terrace_cheeks','#BD866B'),('muted_glazing','#688B8D'),('existing_PV','#617D94')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_right_roof_terrace_and_display_base_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0003)&(hi[:,2]<=b+.0003)
 def xx(a,b):return (lo[:,0]>=a-.0003)&(hi[:,0]<=b+.0003)
 def yy(a,b):return (lo[:,1]>=a-.0003)&(hi[:,1]<=b+.0003)
 def plane(y):return np.all(abs(t[:,:,1]-y)<.0003,axis=1)
 def box(x,y,z,w,d,h):return xx(x-w/2,x+w/2)&yy(y-d/2,y+d/2)&zz(z,z+h)
 paint(box(-19,8,2.3,76,52,95.1)&((n[:,1]<-.99)|(n[:,0]<-.99)),1,'observed_front_and_left_main_tan_tile')
 paint(box(0,-23.7,2.3,28,12.2,84)&(n[:,1]<.01)&(n[:,2]<.01),2,'observed_front_charcoal_tower_no_mosaic_texture_or_letters')
 for x in [-12.1,12.1]:paint(box(x,-22.5,85.5,3.2,11,7.9),2,'top_loggia_existing_piers_not_glass')
 paint(box(0,-22.5,92.1,32,16,2.1),2,'top_loggia_cap_dark_proxy')
 for x in [3.4,5.5,7.6,9.7,11.8,13.9]:paint(box(x,-30.8,12,1,3,72),3,'existing_six_white_vertical_fins')
 for z in [11.6,34.3]:paint(box(8.6,-31.1,z,12.5,2.9,2.2),3,'existing_white_fin_bands')
 paint(box(27,-21.5,2.3,26,12.5,24.5)&(n[:,1]<.01),3,'observed_low_right_pale_screen_relief_not_glass')
 paint(box(-60.2,-19.6,2.3,3.2,26,61),3,'observed_large_left_pale_frame')
 paint(xx(-61.8,-12.8)&yy(-32.5,-6.8)&zz(59,67),3,'observed_sloping_pale_soffit')
 for x in [-12.8,13.8]:paint(box(x,-34,2.3,3.7,5.3,15.3),3,'existing_pale_entry_jambs')
 paint(box(.5,-34,15.8,30.3,5.3,5.7),3,'existing_pale_entry_lintel_no_fake_letters')
 # The original curved body's full-height slots do not match source small window panels.
 # Orange recess backs proxy opaque wall; existing narrow outward ribs pale. No fake tall glazing.
 d=t[:,:,:2]-np.array([-39,-20]);r=np.sqrt((d[:,:,0]/18.5)**2+(d[:,:,1]/12.58)**2)
 curved=xx(-57.5,-20.5)&yy(-32.58,-20)&zz(2.3,35.3)
 paint(curved,4,'orange_front_curved_wall_including_exaggerated_original_slot_backs')
 paint(curved&np.all(r>.997,axis=1),3,'existing_outer_curved_fins_pale_proxy')
 paint(xx(-58.4,-19.6)&yy(-33.192,-20)&zz(34.6,36.2),3,'existing_front_curved_cap_pale')
 for x in [-49,-41,15]:paint(xx(x-1.45,x+1.45)&zz(61,69.7)&plane(-17.2),6,'front_upper_window_back')
 for x in [-45,-37]:paint(xx(x-1.4,x+1.4)&zz(41.5,50.2)&plane(-17.2),6,'front_lower_window_back')
 for z in [21.5,43.5,63]:paint(xx(13.45,16.55)&zz(z,z+8.1)&plane(-17.2),6,'front_right_window_back')
 for z in [65.5,84]:
  for y,w in [(-3,2.1),(1.5,2.1),(6,2.1),(10.5,2.1),(21,10)]:paint(np.all(abs(t[:,:,0]+56.2)<.0003,axis=1)&yy(y-w/2,y+w/2)&zz(z,z+8.3),6,'registered_left_elevation_window_back')
 paint(box(48,33.8,15.2,45.8,1.5,3.2)|box(66.8,14,15.2,1.5,40,3.2),5,'observed_R1_salmon_terrace_parapets')
 for x in [52.3,65.7]:paint(xx(x,x+1.5)&yy(-34,-7)&zz(2.3,18.8),5,'observed_R1_salmon_sloping_stair_cheeks')
 for x in [-28,0]:paint(xx(x-13.5,x+13.5)&yy(-1.6,28.6)&zz(100.8,104),7,'existing_two_PV_canopy_panels_only')
 paint(hi[:,2]<=2.4001,0,'neutral_display_base_not_site_paving')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU I1 Information and R1 Conference Segment original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuui1-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official NUU I1/R1 photos1/3 EXIF2025; uncalibrated proxies','scope':'Observed front and left only. Tan main body, dark front tower, pale existing fins and portal, orange curved wall with exaggerated original slots NOT full-height glass, salmon R1 cheeks, existing PV. Unknown rear/right and planted terrace strips neutral; L1 library excluded.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
