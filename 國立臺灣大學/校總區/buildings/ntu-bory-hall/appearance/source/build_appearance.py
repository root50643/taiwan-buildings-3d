"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='eff769ae90d85b19884af0c950d684f4af963d48339f71f6ea0898122f8c57af'
PALETTE=[('neutral_unknown','#AAA79F'),('warm_gray_brown_wall','#A29C90'),('pale_ivory_bands','#D1D0BE'),('light_blue_gray_large_panes','#8EA7B0'),('dark_gray_narrow_panes','#647476'),('silver_gray_existing_frames','#AFBAB8'),('charcoal_roof_edge','#555D5D')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_roof_rear_right_passage_and_mixed_core_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-20.5)&xx(-69,69)&zz(2.8,103.8),1,'documented_front_warm_gray_brown_wall_panels')
 paint(plane(0,-69)&yy(-20.5,32.5)&zz(2.8,103.8),1,'documented_left_end_warm_gray_wall')
 paint(plane(1,-17.5)&xx(-37.5,37.5)&zz(32,75),3,'source_central_glazed_field_existing_back_only')
 paint(plane(1,-17.5)&xx(-37.4,-18.6)&zz(3,32.3),3,'source_lower_left_glazed_extension_existing_back')
 for x in [-28,-14,0,14,28]:paint(box(x-.425,x+.425,-20.3,-16.9,32,75),5,'original_central_vertical_mullions')
 for z,h in [(33,1.6),(47,1.6),(61,1.6),(74,1.6),(40,.8),(54,.8),(68,.8)]:paint(box(-37.5,37.5,-20.3,-16.9,z,z+h),5,'original_central_horizontal_mullions')
 for x in [-34,-28,-22]:paint(box(x-.425,x+.425,-20.3,-16.9,3,32),5,'original_lower_left_vertical_mullions')
 for z in [10,20,30]:paint(box(-36.5,-19.5,-20.3,-16.9,z,z+.8),5,'original_lower_left_horizontal_mullions')
 for z in [6,20,34,48,62,76,90]:
  xs=list(range(-63,64,7)) if z>=76 else [-63,-56,-49,-42,42,49,56,63]
  for x in xs:paint(plane(1,-18.9)&xx(x-1.55,x+1.55)&zz(z,z+9.2),4,'source_front_narrow_window_back')
  for y in [-12,-6,0]:paint(plane(0,-67.5)&yy(y-1.3,y+1.3)&zz(z,z+9.2),4,'source_left_end_narrow_window_back')
 for z in range(6,102,4):
  for x in [-54,54]:paint(box(x-15,x+15,-21.2,-20.2,z,z+.75),2,'documented_existing_front_light_horizontal_bands')
  if z>=76:paint(box(-69,69,-21.2,-20.2,z,z+.75),2,'documented_existing_upper_front_light_band')
  paint(box(-69.5,-68.5,-21,33,z,z+.75),2,'documented_existing_left_end_light_band')
 paint((plane(1,-22.5)|plane(0,-71))&box(-71,71,-22.5,34.5,103,104.7),6,'source_visible_dark_roof_cap_fascia_NOT_roof_top')
 # Core has a pale lower tile belt, with no original horizontal face boundary;
 # keep the complete mixed cylindrical side neutral rather than false diagonal.
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Bory Hall original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntubory-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTU 2010 public exterior photographs and contractor project image; uncalibrated proxies','scope':'Visible front/left warm gray panels, pale bands, separate light central glass/dark narrow panes, silver original mullions and dark visible fascia. Mixed cylinder silver/white belt lacks mesh boundary and stays neutral, as do passage, right, rear and roof top.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
