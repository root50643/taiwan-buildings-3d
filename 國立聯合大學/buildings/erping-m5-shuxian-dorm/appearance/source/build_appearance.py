"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='6de5a9a8dda58b3d3293e2364d796387a12dc3fc1f8497907ec18701d9c6d890'
PALETTE=[('neutral_unknown','#AAA79F'),('warm_pale_tiled_wall','#C7BFAA'),('cream_louvers_frames_column','#D2CDBD'),('muted_gray_blue_glazing','#74888A'),('dark_slate_corner_cladding','#4D606C'),('silver_canopy_proxy','#A8B1B3'),('wood_brown_blank_plaque','#966C4D')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_right_back_flatroof_base_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.003,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(box(-65,65,-14,-6.5,5,68),1,'front_pale_tile_bounded_repetitive_material_extension')
 paint(box(-69.5,-62.5,-7,35,5,68),1,'visible_left_circulation_strip_pale_wall')
 paint(box(-65.5,-36.5,-14.5,24.5,55.5,68),4,'observed_dark_upper_left_cladding')
 for row in range(5):
  z=7+row*12
  for j,x in enumerate([-57,-46,-35,-24,-13,-2,9,20,31,42,53]):
   if row<2 and x< -25:continue
   for zz0,h in [(z,6.3),(z+7.3,2)]:
    paint(plane(1,-13)&xx(x-3.65,x+3.65)&zz(zz0,zz0+h),3,'discrete_existing_window_back_only')
   paint(box(x-4.15,x+4.15,-15.15,-12.85,z+6.35,z+7.25),2,'original_pale_window_transom')
   if (j+row)%3!=0:paint(box(x-3.7,x+3.7,-16.2,-13.8,z-.2,z+3.6),2,'existing_solid_louver_ridges_not_glass')
 for x in [-57,-46]:paint(plane(1,-13.2)&xx(x-3.65,x+3.65)&zz(56,65),3,'reclad_corner_discrete_window_back')
 for z in [8,20,32,44,56]:
  paint(plane(0,-68.5)&yy(-.5,28.5)&zz(z,z+6.5),3,'left_strip_window_back')
  paint(box(-70.6,-68.4,-1,29,z+4.2,z+5.05),2,'left_strip_original_transom')
 paint(box(-61.6,-56.4,-21.1,-15.9,2.3,30.3),2,'documented_pale_cylindrical_column')
 paint(box(-61.5,-26.5,-20.5,-7.5,28.8,30.2),2,'existing_porch_white_ceiling_grid')
 paint(box(-60,-28,-7.8,-5.6,16.8,21),1,'pale_solid_sign_band_not_glass')
 for z,h in [(6,10.1),(22.2,7)]:
  paint(plane(1,-5.6)&xx(-57.5,-30.5)&zz(z,z+h),3,'porch_existing_glazing_back')
 for x in [-55,-49,-43,-37,-31]:
  for z,h in [(6,10.3),(22.1,7.2)]:paint(box(x-.425,x+.425,-7.8,-5.6,z,z+h),2,'existing_pale_porch_mullion')
 paint(box(-51,-37,-8.6,-7.4,18,20),6,'blank_wood_plaque_no_invented_letters')
 paint(zz(68.5,73.4),5,'canopy_silver_proxy_only_underside_seen_top_not_confirmed_PV')
 paint(hi[:,2]<=2.4001,0,'neutral_original_base')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU M5 Shuxian Dormitory original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuum5-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official M5 approach and close entrance photos; uncalibrated proxies','scope':'Pale tile frontage bounded same-system extension; cream louvers, discrete glazing, dark upper-left cladding and blank wood plaque. Canopy silver including unseen top proxy: PV not confirmed. Right/rear and base neutral; geometry unchanged.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
