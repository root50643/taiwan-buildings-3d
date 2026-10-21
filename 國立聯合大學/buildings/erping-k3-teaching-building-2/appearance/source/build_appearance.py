"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='42a6fe43719062167e2b11dfec74c17ddf107c3dc74ad2f62b4ae6a2c03b0ddc'
PALETTE=[('neutral_unknown','#AAA79F'),('gray_wall_stair_hood','#A2A29A'),('pale_rooftop_parapet','#C1C1B8'),('green_window_frame','#557C6D'),('muted_gray_green_glazing','#687A78'),('photovoltaic_upper_faces','#354C6C'),('silver_gray_canopy_support','#A4ADB0')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_surface_or_base_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.002)&(hi[:,2]<=b+.002)
 def xx(a,b):return (lo[:,0]>=a-.002)&(hi[:,0]<=b+.002)
 def yy(a,b):return (lo[:,1]>=a-.002)&(hi[:,1]<=b+.002)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.002,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(box(-71,60,-17,21,2.3,54.5),1,'documented_gray_structure_stairs_hoods_and_open_corridor_not_glass')
 for z in [5.2,17.2,29.2,41.2]:
  for x in np.arange(-52.5,53,10.5):
   paint(plane(1,-13.7)&xx(x-4.35,x+4.35)&zz(z,z+7.5),4,'front_discrete_window_recess')
   for dx in [-2.2,0,2.2]:paint(box(x+dx-.4,x+dx+.4,-15.1,-13.5,z-.1,z+7.6),3,'existing_green_frame')
   paint(box(x-4.4,x+4.4,-15.1,-13.5,z+5.7,z+6.5),3,'existing_green_transom')
 # Behind open corridor only physically recessed window backs; keep shadows/whole corridor gray.
 for z in [4.4,16.4,28.4,40.4]:
  for x in [-47,-23.5,0,23.5,47]:
   paint(plane(1,13.7)&xx(x-5,x+5)&zz(z,z+8.2),4,'existing_inner_corridor_window_back_bounded_same_window_system')
 paint(box(-59,59,-14.75,-13.25,50.4,54.5),2,'pale_front_rooftop_parapet')
 paint(box(57.75,59.25,-14.5,19.5,50.4,54.5),2,'pale_end_rooftop_parapet')
 paint(zz(54.5,61)&xx(-60.5,60.5)&yy(-17,22),6,'documented_roof_support_edge_and_underside_silver_gray')
 # Lower portions of original canopy posts above terrace, but not masonry parapets.
 for x in np.arange(-57,59,9.5):
  for y in [-13,18.5]:paint(box(x-.75,x+.75,y-.75,y+.75,50.4,59.1),6,'existing_silver_canopy_post')
 ang=np.deg2rad(3.7);lz=-(t[:,:,1]-2.5)*np.sin(ang)+(t[:,:,2]-57.1)*np.cos(ang)
 paint(xx(-60.5,60.5)&np.all(abs(lz-1.7)<.003,axis=1)&(n[:,2]>.9),5,'aerial_confirmed_single_slope_PV_top_original_coarse_grid')
 paint(hi[:,2]<=2.4001,0,'neutral_original_unsplit_base')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU K3 Teaching Building 2 original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuuk3-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official K3 photos 1,2,3; uncalibrated colors','scope':'Gray concrete walls stairs hoods and open corridors, green front frames and discrete glazing; inner corridor window material bounded same-system extension, not whole corridor glass. Aerial-confirmed single-slope PV upper faces only, coarse grid not exact coverage. No adjacent K2 or signs.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
