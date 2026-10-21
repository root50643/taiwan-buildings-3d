"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='5eabfa142fe335ac9bc0d78344aff36eeeee23553c9370dcc46e1f257b64df94'
PALETTE=[('neutral_unknown','#AAA79F'),('warm_gray_columns','#AAA99E'),('pale_gray_spandrels','#C5C8C0'),('silver_white_frames','#C9D0CB'),('muted_gray_glass','#8A9695'),('cool_gray_steps_canopy','#B1B7B3')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_or_unregistered_side_wall_recess_right_rear_roof_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-29)&xx(-66,66)&zz(2.8,77.8),2,'source_front_pale_gray_solid_spandrels')
 for x in [-66.5,-47.5,-28.5,-9.5,9.5,28.5,47.5,66.5]:paint(box(x-1.25,x+1.25,-31,-28,3,78),1,'source_front_warm_gray_columns')
 for x in [-57,-38,-19,0,19,38,57]:
  for z,h in [(7,9),(22,11),(39,6),(50,12)]:
   paint(plane(1,-27.5)&xx(x-7.5,x+7.5)&zz(z,z+h),4,'source_discrete_front_window_back_only')
   paint(box(x-.5,x+.5,-29.5,-27.5,z,z+h),3,'source_original_window_vertical_frame')
   if h>9:paint(box(x-7.5,x+7.5,-29.5,-27.5,z+h/2,z+h/2+.9),3,'source_original_window_horizontal_frame')
  paint(plane(1,-27.5)&xx(x-7.5,x+7.5)&zz(65,76),4,'source_pointed_upper_window_back')
  for dx in [-3.8,0,3.8]:paint(box(x+dx-.45,x+dx+.45,-29.5,-27.5,65,74),3,'source_original_pointed_window_vertical_frame')
  paint(box(x-7.5,x+7.5,-29.5,-27.5,69.5,70.4),3,'source_original_pointed_window_horizontal_frame')
 paint(box(-11.5,11.5,-37,-27,34,35.7),5,'source_gray_canopy_same_material_bounded_top')
 paint(box(-13.1,13.1,-49.75,-29.04,2.8,23.32),5,'source_external_steps_and_original_thick_sidewalls_no_added_handrails')
 for y in [-22,-9,4,17,30,41]:paint(box(-67.75,-64.25,y-.8,y+.8,18,77),2,'source_left_side_existing_pale_fin_only')
 paint(hi[:,2]<=3.0001,0,'original_unsplit_ground_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Library Information Science original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntulis-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTU official 2010 M9 photos with LIS website image metadata dating2003 as supplement; uncalibrated proxies','scope':'Front gray columns/spandrels, separated gray window backs and silver frames, gray steps/canopy, visible left fins. Mixed side walls and recesses, unknown right/rear/roof neutral. No air conditioners or missing handrails added.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
