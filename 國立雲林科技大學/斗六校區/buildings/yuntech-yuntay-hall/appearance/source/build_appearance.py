"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='73602a6aab74bdad2c33cae24543ab33ca4be653ca9943dddb4daa0be28a1c0b'
PALETTE=[('neutral_unseen','#AAA79F'),('light_gray_front_panels','#C1C5C2'),('gray_waist_cornice','#929998'),('dark_horizontal_trim','#535D60'),('dark_glazing_proxy','#36464B'),('warm_front_steps','#C6BDA8'),('display_plinth','#888C88')]
def classify(tri):
 t=tri.copy();t[:,:,:2]+=46
 lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 r=np.linalg.norm(t[:,:,:2],axis=2);rc=np.linalg.norm(c[:,:2],axis=1)
 front=(lo[:,0]>=-.0001)&(lo[:,1]>=-.0001)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_roof_straight_wings_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0001)&(hi[:,2]<=b+.0001)
 # Only the existing quarter-circle facade is registered to this photograph.
 paint(front&(r.min(axis=1)>=106.5)&zz(5.2,32.8)&(n[:,2]<.1),1,'registered_curved_front_light_gray_panel_and_pier')
 paint(front&(r.min(axis=1)>=109.5)&zz(14.7,19.1)&(abs(n[:,2])<.1),2,'existing_broad_waist_band_gray')
 paint(front&(r.min(axis=1)>=109.5)&zz(31.6,32.8)&(abs(n[:,2])<.1),2,'existing_upper_cornice_gray')
 paint(front&(r.min(axis=1)>=109.0)&zz(22.0,23.6)&(abs(n[:,2])<.1),3,'existing_thin_band_above_clerestory_dark_gray')
 # Backed recess planes only. Never color shadows on jambs as dark materials.
 for angle in np.linspace(3.0,87.0,15):
  a=np.deg2rad(angle);u=t[:,:,0]*np.cos(a)+t[:,:,1]*np.sin(a)
  paint(front&np.all(abs(u-106.7)<.00015,axis=1)&zz(5.7,14.2),4,'existing_ground_bay_recess_back_glazing_proxy')
 for angle in np.linspace(3.1,86.9,36):
  a=np.deg2rad(angle);u=t[:,:,0]*np.cos(a)+t[:,:,1]*np.sin(a)
  paint(front&np.all(abs(u-107.65)<.00015,axis=1)&zz(19.1,22),4,'existing_clerestory_recess_back_glazing_proxy')
 paint(front&(r.min(axis=1)>=110.8)&zz(2.6,5.55),5,'existing_curved_forecourt_steps_pale_warm_stone')
 paint(hi[:,2]<=2.8001,6,'display_base_not_real_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'YunTech Yuntay Hall original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'yuntay-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official gallery facade photograph approximations, not measured material swatches','scope':'Quarter-circle public facade only; straight wings, roof, original roof service blocks and solar-array geometry remain neutral. Reference EXIF DateTimeOriginal records 2024-08-12; not a 2026 survey.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
