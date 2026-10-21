"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='812aec55c6eca33e588f0c594b6b95928a2e8d9c95f9ac5a8bbecd4b6132076e'
PALETTE=[('neutral_mixed_or_unknown','#AAA79F'),('bluegray_plaster','#9BA8AE'),('reddish_brown_wood_frames','#79564A'),('subdued_gray_glass','#77868A'),('gray_concrete_stairs','#969B98'),('charcoal_low_hip_roof','#666D70')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_ground_plaster_and_gray_foot_unseen_rear_main_roof_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 # Upper wall only: full ground faces cross gray foot and plaster, left neutral.
 paint(plane(1,-14)&xx(-64,42)&zz(19.3,40.8),1,'source_upper_front_bluegray_plaster_inside_existing_band_boundary')
 for z,h in [(18,1.3),(36.8,1.3)]:paint(box(-65,43,-16.5,-13.5,z,z+h),1,'source_bluegray_existing_horizontal_band')
 for x in range(-63,44,12):paint(box(x-.65,x+.65,-15.8,-13.8,19.3,40),1,'source_upper_existing_bluegray_pier_ground_mixed_foot_neutral')
 for x in range(-57,40,12):
  for z,h in [(6,11),(26,10)]:
   paint(plane(1,-12.75)&xx(x-3.7,x+3.7)&zz(z,z+h),3,'source_tall_window_glass_back')
   paint(box(x-.5,x+.5,-14.85,-13.15,z,z+h),2,'source_existing_wood_vertical_frame')
   paint(box(x-3.7,x+3.7,-14.85,-13.15,z+h/2,z+h/2+.9),2,'source_existing_wood_crossbar')
 for x in [49,60]:paint(plane(1,-12.75)&xx(x-3.5,x+3.5)&zz(5,16),3,'source_low_wing_window_back_NOT_brown_frame_missing_in_geometry')
 # The source supports low hip roof only; main roof remains neutral.
 paint(box(40,70,-16,30,23,30)&(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])[:,2]>0),5,'source_2024_exterior_low_hip_roof_charcoal_tiles_no_texture')
 for i in range(15):
  x=33-i*2.5;h=(i+1)*1.25
  paint(box(x-1.4,x+1.4,-33.5,-20.5,2.8,2.8+h+1.2),4,'source_existing_solid_concrete_stair_and_stepped_parapets')
 paint(box(-9,1,-32.5,-15.5,20.5,22),4,'source_concrete_landing')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Engineering Museum Retained Building original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntuemuseum-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTU Mechanical Engineering official 2023/2024/2025 sources, uncalibrated proxies','scope':'Retained museum block only: upper bluegray plaster, existing wood frames, glass backs, concrete stairs, low hip roof. Mixed ground plaster and foot, side/rear and main roof neutral. Small vents NOT glass; no invented low-wing wood frames.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
