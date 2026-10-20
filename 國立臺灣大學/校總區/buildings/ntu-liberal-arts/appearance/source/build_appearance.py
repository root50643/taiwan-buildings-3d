"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='5f78a0f6ffc52ce5edcf7f99a7393780bbb3a4f35ecf91609b2dab363c001e93'
PALETTE=[('neutral_unseen','#AAA79F'),('warm_brown_brick','#A88970'),('light_gray_stone_relief','#BEBEB3'),('bluegray_window_recess','#65797D'),('charcoal_roof','#505552'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_side_rear_roof_and_deep_portico_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0002)&(hi[:,2]<=b+.0002)
 # Visible front of the historic wall and existing shallow pilasters only.
 paint((hi[:,1]<=-13.9998)&zz(4,28.8)&(lo[:,0]>=-68.001)&(hi[:,0]<=68.001),1,'registered_front_brick_wall_and_pilasters')
 paint((hi[:,1]<=-19.4998)&zz(3,40)&(lo[:,0]>=-17.501)&(hi[:,0]<=17.501),1,'registered_central_front_gable_and_portico_brick')
 paint(np.all(abs(t[:,:,1]+25)<.0002,axis=1)&zz(3.1,15.1),0,'deep_lower_portico_closed_proxy_back_neutral_not_shadow_paint')
 # Relief arch rings, excluding the separate brick pilasters and recessed backs.
 for x in [-61,-53,-45,-37,-29,-21,21,29,37,45,53,61]:
  scope=(lo[:,0]>=x-3.1502)&(hi[:,0]<=x+3.1502)
  paint(scope&(lo[:,1]<-14.0002)&zz(18,27.85),2,'existing_upper_wing_arch_relief_pale_stone')
  for z,h in [(5,8),(18,9)]:paint(scope&np.all(abs(t[:,:,1]+13.2)<.0002,axis=1)&zz(z,z+h),3,'existing_wing_window_recess_back_bluegray')
 for x in [-9,0,9]:
  scope=(lo[:,0]>=x-3.8502)&(hi[:,0]<=x+3.8502)
  paint(scope&(lo[:,1]<-19.5002)&zz(20,29.85),2,'existing_upper_central_arch_relief_pale_stone')
  paint(scope&np.all(abs(t[:,:,1]+18.3)<.0002,axis=1)&zz(20,29),2,'central_upper_open_arcade_back_is_neutral_light_finish_not_glass')
 paint((hi[:,1]<=-14.4998)&zz(3,4),2,'registered_front_foundation_band_pale_gray')
 paint((hi[:,1]<-27.8)&zz(2.8,4.9),2,'existing_entry_steps_gray_stone')
 paint((n[:,2]>.05)&(n[:,1]<-.05)&(lo[:,2]>=27.9998)&(hi[:,2]<=34.0002),4,'source_visible_front_main_roof_slope_charcoal')
 paint((n[:,2]>.05)&(lo[:,2]>=30.9998)&(hi[:,2]<=40.0002)&(hi[:,1]<=-10.4998)&(lo[:,0]>=-17.501)&(hi[:,0]<=17.501),2,'existing_central_gable_top_edge_gray_proxy_not_new_detail')
 paint(hi[:,2]<=3.0001,5,'display_base_not_landscape')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Liberal Arts original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'liberal-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NTU student counseling location photograph; embedded DateTimeOriginal 2022-03-11 10:42:43, timezone unprovided and not independently verified approximations, not measured material swatches','scope':'Source-registered front brick, pale arch relief and wing glazing; central upper open arcade is not glass; rear neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
