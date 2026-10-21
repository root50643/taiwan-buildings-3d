"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='0e3847ed2b9b2872275f247a28d9ea0bb077d2c6bde62551a153fbfefbe77839'
PALETTE=[('neutral_unknown','#AAA79F'),('charcoal_gray_tile_roof','#626461'),('weathered_graybrown_left_wood','#92887C'),('pale_bluegray_posts_frames','#A6B7B3'),('muted_graygreen_window_door_proxy','#829C95'),('gray_stone_veranda','#B0B3AA')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_front_rear_wall_gable_overhang_and_unseen_annex_wall_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(box(-71.5,71.5,-23,23,21,31)&(n[:,2]>.05)&(n[:,2]<.999),1,'two_official_views_support_both_main_tiled_roof_slopes')
 paint(box(44,72,10.5,35.5,16.5,22)&(n[:,2]>.05)&(n[:,2]<.999),1,'official_reverse_view_supports_annex_tiled_roof_slopes')
 paint(plane(0,-68)&yy(-7,19)&zz(2.8,21.3),2,'source_left_weatherboard_wall_coarse_original_relief')
 for z in [6,9,12,15,18]:paint(box(-68.6,-67.4,-7,19,z,z+.8),2,'source_left_wood_horizontal_relief_NOT_brick')
 for y in [-5,0,5,10,15]:paint(box(-68.45,-67.55,y-.45,y+.45,3,21),2,'source_left_wood_vertical_relief')
 for x in [-66,-51,-36,-21,-6,9,24,39,54,67]:paint(box(x-.85,x+.85,-21.85,-20.15,4.5,21.5),3,'source_veranda_pale_bluegray_posts')
 paint(box(-69.5,69.5,-22,-20,20,21.5),3,'source_veranda_pale_bluegray_beam')
 paint(box(-70,70,-23.5,-6.5,2.8,4.6),5,'source_original_stone_veranda_platform')
 for x in [-57,-42,-27,-12,3,18,33,48,61]:
  if x in [-42,3,48]:paint(plane(1,-5.75)&xx(x-3,x+3)&zz(4.5,17),4,'source_coarse_front_door_back_proxy_not_interior')
  else:
   paint(plane(1,-5.75)&xx(x-4,x+4)&zz(9,15.5),4,'source_discrete_front_window_back')
   paint(box(x-.5,x+.5,-7.55,-5.85,9,15.5),3,'source_original_front_window_vertical_frame')
   paint(box(x-4.2,x+4.2,-7.55,-5.85,12.5,13.4),3,'source_original_front_window_horizontal_frame')
 paint(plane(0,-66.75)&yy(2.5,9.5)&zz(10,15),4,'source_left_end_window_back')
 for x in [-56,-39,-22,-5,12,29]:
  if x in [-22,12]:paint(plane(1,17.75)&xx(x-3.25,x+3.25)&zz(3.5,16.5),4,'official_reverse_view_coarse_rear_door_proxy')
  else:paint(plane(1,17.75)&xx(x-4,x+4)&zz(9,16),4,'official_reverse_view_rear_window_back')
 paint(hi[:,2]<=3.0001,0,'unsplit_ground_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Iso Cottage Pre Restoration original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntuiso-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Two official NTU museum/GA historical pre-restoration photos, capture dates unknown; uncalibrated proxies','scope':'Both main and annex gray tile roof slopes, graybrown left weatherboard, pale veranda posts, discrete front/rear window and door proxies. Mixed front/rear solid walls and unknown annex walls remain neutral; no invented rear brown stripes, roof tiles, braces, or restoration completion claim.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
