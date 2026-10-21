"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='a3f3e5b64154d98a714b70e74f4a575286905b887442eb60bf117f574df30d86'
PALETTE=[('neutral_unknown','#AAA79F'),('pale_white_gray_structure','#D4D6D0'),('muted_blue_teal_window_backs','#527F8F'),('silver_gray_existing_mullions','#A6B1B2'),('warm_sandstone_colonnade','#B9A17C')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_roof_rear_rightside_entry_mixed_back_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.003,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-61.5)&xx(-44,2)&zz(2.8,81.8),1,'observed_tall_front_white_frame_and_spandrels')
 paint(plane(0,-44)&yy(-61.5,61.5)&zz(2.8,81.8),1,'observed_long_left_pale_structure')
 paint(box(-39.5,3.5,-61.5,-50.5,80,84.4)&(abs(n[:,2])<.1),1,'observed_high_front_portal_vertical_faces')
 for z in [21,35,49,63,77.5]:paint(box(-45.8,-43.6,-62,62,z,z+1.45),1,'observed_long_side_white_sunshade_bands')
 paint(box(-45,-43.4,-62.5,62.5,80.5,82)&(abs(n[:,2])<.1),1,'visible_left_coping_vertical_only')
 for y in [-49,-29,-9,11,31,51]:
  for z in [23,37,51,65]:
   paint(plane(0,-43.2)&yy(y-8.4,y+8.4)&zz(z,z+11.5),2,'source_long_side_discrete_window_backs')
   for yy0 in [y-5.4,y,y+5.4]:paint(box(-44.3,-42.9,yy0-.5,yy0+.5,z,z+11.5),3,'original_long_side_mullion_silver_gray')
 for x,w in [(-39,6.5),(-15,18.0)]:
  for z in [22,36,50,64]:
   paint(plane(1,-60.7)&xx(x-w/2,x+w/2)&zz(z,z+11.8),2,'source_front_discrete_pane_backs')
   for x0 in np.arange(x-w/2+3,x+w/2,3.6):paint(box(x0-.5,x0+.5,-62.5,-60.7,z,z+11.8),3,'original_front_mullions_silver_gray')
 for z in [22,36,50,64]:paint(plane(1,-60.7)&xx(.2,1.8)&zz(z,z+11.8),2,'source_visible_narrow_front_edge_strip')
 for x in [-41,-1.5]:paint(box(x-1.65,x+1.65,-62.5,-59.5,3,21),1,'observed_front_white_columns')
 # Lower side relief backs mix openings and walls: do not invent all-glass bays.
 paint(plane(0,-44)&yy(-61.5,61.5)&zz(3,20),4,'source_warm_stone_long_side_piers_between_neutral_relief_backs')
 paint(plane(1,-54)&xx(1,59)&zz(2.8,31.8),1,'source_low_wing_front_pale_spandrels')
 for z in [6,19]:
  paint(plane(1,-53.2)&xx(7.5,56.5)&zz(z,z+9.8),2,'source_low_wing_front_discrete_window_backs')
  for x in np.arange(11,56,7.5):paint(box(x-.5,x+.5,-54.95,-53.15,z,z+9.8),3,'existing_low_wing_front_silver_mullions')
 paint(hi[:,2]<=3.0001,0,'original_ground_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NHRI Zhunan Biologics Pilot Main Exterior original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nhribio-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'CDC 2014 historical exterior figure and NHRI 2017 spring panorama thumbnail; uncalibrated proxies','scope':'Visible front and left white structure, discrete blue-teal recess backs, gray mullions and lower sandstone side piers. Mixed ground-floor recesses, unobserved right/rear/roof remain neutral. No internal layout or equipment inference.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
