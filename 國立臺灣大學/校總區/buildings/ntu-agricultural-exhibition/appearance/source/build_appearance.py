"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='85353c0383c69b73511f5037f94245375f016aad560129f8dc6adcae2e980724'
PALETTE=[('neutral_unknown','#AAA79F'),('ivory_white_ceramic_screen','#D7D7C9'),('warm_gray_concrete_bands_piers','#999B8E'),('warm_gray_ceramic_inner_walls','#AB9B83'),('neutral_backed_hole_NOT_glass','#969086'),('pale_graygreen_lower_glass_proxy','#B6C1B6')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_side_rear_roof_and_mixed_lower_surround_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-17)&xx(-69,69)&zz(13.5,41.8),1,'source_existing_white_screen_surface_not_exact_tile_count')
 for floor in [15,28]:
  for bay in range(10):
   center=-62.1+13.8*bay
   for row in range(4):
    for col in range(4):
     x=center-4.6+col*3.05;z=floor+1.6+row*2.6
     mask=box(x-.86,x+.86,-17,-16,z-.86,z+.86)
     paint(mask&~plane(1,-17),3,'source_warm_ceramic_hole_inner_wall_uncalibrated_proxy')
     paint(mask&plane(1,-16),4,'backed_dimple_neutral_NOT_blue_glass_NOT_true_through_hole')
 for z in [13,26.4,40]:paint(box(-70,70,-18.4,-16.4,z,z+1.7),2,'source_concrete_horizontal_band_no_weathering')
 for x in [-69,-55.2,-41.4,-27.6,-13.8,0,13.8,27.6,41.4,55.2,69]:paint(box(x-.6,x+.6,-18.45,-16.95,14,40),1,'source_white_existing_vertical_divider')
 for x in [-66,-52.8,-39.6,-26.4,-13.2,0,13.2,26.4,39.6,52.8,66]:paint(box(x-1.1,x+1.1,-19.75,-16.25,3,14),2,'source_ground_concrete_pier')
 for x in [-57,-44,-31,-18,-5,8,21,34,47,60]:paint(plane(1,-12.9)&xx(x-4.5,x+4.5)&zz(4,11.5),5,'coarse_lower_glass_proxy_missing_redbrown_frames_disclosed')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Agricultural Exhibition original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntuagexh-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTU official visitor-center exterior photograph, capture date unknown; uncalibrated proxies','scope':'Ivory coarse circular screen, warm ceramic interiors and neutral backed dimples not glass, gray concrete bands/piers, pale lower glazing proxy. Missing redbrown frames and red entry subdivision omitted rather than invented; unknown sides/rear/roof neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
