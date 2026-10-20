"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='e3d752dd25db18883959510619879ed35ea8fee9d046ebb112d579be29cea751'
PALETTE=[('neutral_unseen','#AAA79F'),('lightgray_front_stone','#C2C4BE'),('dark_window_frames','#3D4549'),('grayblue_glazing_proxy','#687E87'),('dark_art_canopy','#495769'),('display_plinth','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_rear_roof_right_lobby_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0001)&(hi[:,2]<=b+.0001)
 front=44-2375*.017
 # South high facade and stepped center only. Right projecting lobby remains neutral.
 paint((hi[:,1]<=front+.0001)&(n[:,1]<-.9)&zz(2.8,62)&(hi[:,0]<=48.0001),1,'registered_13013_front_stone')
 # Exact existing front recess backs, no generic darkening of shaded faces.
 def bay(x,y,z,w,h,depth):
  mask=(lo[:,0]>=x-w/2-.0001)&(hi[:,0]<=x+w/2+.0001)&zz(z,z+h)
  back=mask&np.all(abs(t[:,:,1]-(y+depth/2))<.00015,axis=1)
  paint(back,3,'registered_existing_recess_back_glazing')
 for x in __import__('numpy').linspace(-57,48,20):bay(x,front-.15,55.2,3.4,4.5,2.2)
 bay(-3,front-.15,47.5,111,5.1,2.7)
 for x in __import__('numpy').linspace(-55,46,22):
  for z,h in [(5.6,7.9),(14.5,7.5),(23,7.5),(31.5,7.5),(40,5.2)]:bay(x,front-.12,z,3.55,h,2.5)
 # Only actual exposed front grid surfaces, using original detail bounds.
 for x in __import__('numpy').linspace(-57,49,23):
  paint((lo[:,0]>=x-.5001)&(hi[:,0]<=x+.5001)&(lo[:,1]>=front+.3499)&(hi[:,1]<=front+1.5501)&zz(5.5,45.3),2,'existing_exposed_tall_glazing_mullion')
 for z in [13.5,22,30.5,39]:
  paint((lo[:,0]>=-58.5001)&(hi[:,0]<=50.5001)&(lo[:,1]>=front+.3499)&(hi[:,1]<=front+1.5501)&zz(z,z+1),2,'existing_exposed_tall_glazing_transom')
 for x in __import__('numpy').linspace(-57,49,22):
  paint((lo[:,0]>=x-.4501)&(hi[:,0]<=x+.4501)&(lo[:,1]>=front+.3499)&(hi[:,1]<=front+1.5501)&zz(47.5,52.6),2,'existing_upper_ribbon_mullion')
 for yc,zmax,x0,x1 in [(2675,44,1195,5245),(3400,36,1195,5245),(4100,28,1195,4570)]:
  y=44-yc*.017
  for cm in __import__('numpy').arange(x0+260,x1-150,550):
   x=cm*.017-66
   for z,h in [(5.2,9.3),(19.5,5),(29.5,5)]:
    if z+h<zmax:bay(x,y-.12,z,3.8,h,2)
   if zmax>=36:bay(x,y-.12,zmax-5,1.5,1.7,2)
 paint((lo[:,0]>=-66.0001)&(hi[:,0]<=-51.9999)&(lo[:,1]>=front-5.2501)&(hi[:,1]<=front+1.2501)&zz(14.4,15.9),4,'13013_left_art_center_existing_canopy')
 bay(-59,front-1,3.9,7,10.2,2.5)
 paint(hi[:,2]<=2.8001,5,'display_base_not_real_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'YunTech Library Art Center original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'library-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official 2008 gallery facade photograph approximations, not measured material swatches','scope':'Registered 13013 historical front only; roof, rear and obscured right lobby neutral; 13012 not mirrored.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
