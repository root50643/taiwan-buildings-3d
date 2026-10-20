"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='ea6bb1b32454b3fe0fcb1685f20011ebd3cb1fd8312ce6cbefeeadaf09a1abf0'
PALETTE=[('neutral_unseen','#AAA79F'),('red_ochre_exterior','#B74F38'),('warm_white_corridor_and_rails','#D0CCB8'),('muted_short_end_glazing','#84918D'),('gray_entry_canopy','#A9AAA0'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_opposite_end_and_roof_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 paint(plane(1,-31)&zz(3,36.9),1,'registered_long_front_red_ochre_exterior')
 paint(plane(0,-66)&zz(3,36.9),1,'registered_small_window_short_end_red_ochre_proxy')
 for x in range(-55,56,11):
  opening=(lo[:,0]>=x-4.00025)&(hi[:,0]<=x+4.00025)&(lo[:,1]>=-31.00025)&(hi[:,1]<=-26.09975)
  paint(opening&(zz(3.5,16.4)|zz(23,33.7)|zz(19,21.5)),1,'existing_front_portico_opening_returns_red_ochre')
  paint(opening&plane(1,-26.1),2,'deep_portico_back_warm_white_wall_not_glass_or_shadow')
  paint(opening&zz(21.5,23),2,'existing_thickened_upper_railing_strip_white_proxy')
 paint((lo[:,0]>=-66.50025)&(hi[:,0]<=66.50025)&(lo[:,1]>=-34.20025)&(hi[:,1]<=-30.79975)&zz(18,19.2),2,'existing_front_horizontal_band_white_proxy')
 for y in [-20,0,20]:
  mask=(lo[:,1]>=y-3.25025)&(hi[:,1]<=y+3.25025)&(lo[:,0]>=-66.00025)&(hi[:,0]<=-64.99975)
  paint(mask&zz(5,15),1,'short_end_lower_aperture_returns_red');paint(mask&zz(5,15)&plane(0,-65),2,'short_end_lower_aperture_back_white_wall_proxy')
  paint(mask&zz(25,30),2,'existing_upper_short_end_window_returns_pale_proxy');paint(mask&zz(25,30)&plane(0,-65),3,'upper_short_end_window_recess_back_muted_glazing')
 paint((lo[:,0]>=-26.00025)&(hi[:,0]<=-5.99975)&(lo[:,1]>=-40.00025)&(hi[:,1]<=-29.99975)&zz(16.5,17.8),4,'existing_entry_canopy_gray_proxy_no_equipment')
 paint(hi[:,2]<=3.0001,5,'display_base_not_street_or_foundation')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU Military Training Building original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'military-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NCKU map photos 38136 and 38137; capture date unknown','scope':'Registered red long front and small-window short end, pale corridor backs and existing rail strips; unseen roof, rear and opposite end neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
