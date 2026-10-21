"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='d3c302949f97a36001244b8254d4d3c45a14d6b43861b6c4507d425cdde4ead0'
PALETTE=[('neutral_unknown_or_mixed','#AAA79F'),('warm_cream_masonry','#CFCCBB'),('orange_steel_fins','#AC5D36'),('silver_window_metal','#B6B9AA'),('muted_graygreen_glazing','#74857C'),('dark_brown_canopy_louvers','#55483B'),('blank_relief_wall_gray','#68665B')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_roof_rear_upper_balcony_mixed_back_and_lower_foot_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 def arc(rx,ry):return np.all(abs(((t[:,:,0]+6)/rx)**2+((t[:,:,1]-7)/ry)**2-1)<.002,axis=1)&(hi[:,1]<7)&(abs(norm[:,2])<.0001)
 paint(arc(65,34)&zz(36,40.8),1,'source_front_cream_curved_masonry_whole_faces_not_mixed_foot')
 for x in [-51,-32,-12,8,27]:paint(arc(63.5,32.5)&xx(x-7,x+7)&zz(5,19),4,'source_lower_separate_glazing_backs_simplified_no_added_fine_frames')
 for x in [-43,-31,-19,-7,5,17,29]:
  y=7-29*np.sqrt(max(0,1-((x+6)/60)**2));paint(box(x-.6,x+.6,y-1.25,y+1.25,24,36),3,'source_existing_upper_silver_mullion')
 for x in [12,19,26]:
  y=7-34*np.sqrt(max(0,1-((x+6)/65)**2))-.6;paint(box(x-.9,x+.9,y-2.5,y+2.5,3,44),2,'source_three_orange_steel_ribs_bounded_same_component_returns')
 for z in np.arange(6,38,2):paint(box(-57.5,-54.5,-15.5,3.5,z,z+.8),5,'source_left_louver_brown_metal_bounded_component')
 paint(plane(1,-17.5)&xx(42,60)&zz(16,39),1,'source_entry_upper_cream_frame_masonry')
 paint(plane(1,-16.5)&xx(44.5,57.5)&zz(25,35),4,'source_upper_entry_glass_back')
 paint(box(31.5,64.5,-36.5,-15.5,18,20.2)&(norm[:,2]<.001),5,'source_canopy_dark_brown_edges_soffit_upper_roof_neutral')
 for x in [33,63]:paint(box(x-1.1,x+1.1,-34.1,-31.9,3,19),1,'source_entry_supports_cream_original_simplification')
 paint(plane(1,-19.5)&xx(38,60)&zz(3,16),6,'source_relief_wall_blank_gray_no_portraits_or_text')
 paint(hi[:,2]<=3.0001,0,'unsplit_base_not_lawn')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU Hall of Fame original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthufame-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTHU official alumni photographs, uncalibrated material proxies','scope':'Cream curved facade, three orange fins, silver original mullions, separate lower window backs, dark canopy soffit and left louvers, blank gray relief wall. Upper balcony mixed back and thick solid railing surrogate neutral; unseen roof/rear and mixed foot neutral. No portraits or words.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
