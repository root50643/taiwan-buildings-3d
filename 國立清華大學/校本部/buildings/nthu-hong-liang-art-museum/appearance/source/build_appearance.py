"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='461a0db5eeb3a0f423f8b21c40c80a4b48be20f17acdf378e91a2eb6f50111d2'
PALETTE=[('neutral_unknown','#AAA79F'),('cool_silver_metal_panels','#B8C4C5'),('pale_warm_concrete','#C4BFB1'),('dark_graygreen_glazing','#576D66'),('silver_gray_mullions','#9EAEB0'),('muted_red_brick_return','#9B5E4A')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_roof_right_end_rear_and_unregistered_surfaces_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(box(-65,-31,-26,-25.675,16,39),1,'source_left_front_metal_panel_and_same_material_groove_not_glass')
 paint(box(-65,-64.675,-26,26,16,39),1,'source_left_end_metal_panels')
 paint(box(40,68,-20,-19.675,16,39),1,'source_right_front_metal_panels_only')
 paint(plane(1,-28)&xx(-25.5,33.5)&zz(16,39),2,'source_center_gallery_warm_concrete_front')
 # Recessed visible links only on outward front, no black hidden wrapping.
 paint(plane(1,-15.5)&xx(-31.5,-24.5)&zz(3,31),3,'source_visible_left_link_front_glazing')
 paint(plane(1,-11)&xx(33,39)&zz(3,24),3,'source_visible_right_link_front_glazing')
 for y,back,a,b,xs,d in [(-20,-18.7,-60,-26,[-57,-50,-43,-36,-29],3),(-14,-12.5,-21,17,[-19,-9,1,11],3.5),(-8.5,-7.25,41,65,[43,50,57,64],3)]:
  paint(plane(1,back)&xx(a,b)&zz(4,14.5),3,'source_ground_discrete_glazing_back')
  for x in xs:paint(box(x-.55,x+.55,y-d/2,y+d/2,4,14.5),4,'source_existing_silver_ground_mullion')
 paint(plane(0,-60.65)&yy(-18,22)&zz(4,14.5),3,'source_left_end_ground_glazing')
 for y in [-16,-6,4,14,20]:paint(box(-63.6,-60.4,y-.55,y+.55,4,14.5),4,'source_left_end_silver_mullion')
 paint(box(17.5,30.5,-24.5,-5.5,3,16.4),2,'source_warm_concrete_main_pillar_bounded_returns')
 paint(box(-21.4,-18.6,-26.4,-23.6,3,16.5),2,'source_round_concrete_pier_bounded_circumference')
 paint(box(-68.2,-65.8,-18,32,3,10)|box(-68,-60,-19,-15,3,10),5,'source_existing_low_brick_return_bounded_end_top')
 paint(hi[:,2]<=3.0001,0,'original_unsplit_base_not_green_lawn')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU Hong Liang Art Museum original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthuhong-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTHU official attraction photographs, uncalibrated proxies','scope':'Front and source-supported left end: silver metal panel faces, central pale concrete, dark glazing and silver mullions, low brick return. Roof, right end, rear and unregistered returns neutral; no green reflection baked into walls.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
