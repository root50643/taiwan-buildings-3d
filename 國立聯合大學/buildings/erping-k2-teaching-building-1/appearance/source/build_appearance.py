"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='501d32dc430a058083b97ca162f63a64786fe85b285edd67878d62fd87a4a605'
PALETTE=[('neutral_unknown','#AAA79F'),('gray_aggregate_wall_stair','#9C9C94'),('pale_shading_fins_end_frames','#CBC8B7'),('green_window_frames','#698B80'),('muted_gray_green_glazing','#6A7C7A'),('photovoltaic_upper_faces','#354C6C'),('silver_gray_roof_support','#A4ADB0')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_surface_or_base_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.002)&(hi[:,2]<=b+.002)
 def xx(a,b):return (lo[:,0]>=a-.002)&(hi[:,0]<=b+.002)
 def yy(a,b):return (lo[:,1]>=a-.002)&(hi[:,1]<=b+.002)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.002,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(box(-71,67,-20,20,2.3,42.8),1,'documented_gray_aggregate_wall_stair_and_sills')
 for z in [5.8,18.5,31.2]:
  for x in np.arange(-54,55,10.8):
   paint(plane(1,-16.25)&xx(x-4.25,x+4.25)&zz(z,z+7.9),4,'front_discrete_glazing_back')
   for dx in [-2.1,0,2.1]:paint(box(x+dx-.375,x+dx+.375,-17.525,-16.075,z-.1,z+8),3,'existing_front_green_vertical_frame')
   paint(box(x-4.3,x+4.3,-17.525,-16.075,z+5.9,z+6.65),3,'existing_green_horizontal_transom')
   paint(plane(1,16.25)&xx(x-4.35,x+4.35)&zz(z,z+8),4,'documented_opposite_discrete_glazing_back')
   paint(box(x-.4,x+.4,16.075,17.525,z-.1,z+8.1),3,'opposite_existing_frame_green')
  for x in np.arange(-59,60,5.4):paint(box(x-.575,x+.575,16.3,19.3,z-.6,z+9.5),2,'documented_dense_pale_shading_fins')
 for z,h in [(18.5,8.2),(31.2,8.2),(2.8,10.1)]:
  w=4.6 if z>3 else 5.2
  paint(plane(0,59.2)&yy(-w,w)&zz(z,z+h),4,'entrance_end_existing_glazing')
  ys=[-2.3,0,2.3] if z>3 else [-3.3,0,3.3]
  for y in ys:paint(box(59.05,60.55,y-.4,y+.4,z-.1,z+h+.1),2,'pale_entrance_end_frame')
  if z>3:paint(box(59.05,60.55,-4.65,4.65,z+6,z+6.8),2,'pale_end_transom')
 paint(zz(40.9,49)&xx(-60.1,61)&yy(-19,19),6,'roof_cheeks_undersides_supports_silver_gray')
 # Aerial confirms PV on both roof systems; existing coarse grid retained, not exact cell coverage.
 rz=42.4+5.3*(1-(c[:,1]/18.4)**2)
 paint(xx(-60,36.7)&yy(-18.4,18.4)&zz(41,49)&(n[:,2]>.7)&(abs(c[:,2]-rz)<.025),5,'confirmed_main_barrel_roof_PV_top_existing_grid_only')
 ang=np.deg2rad(2.6);localz=-(t[:,:,1])*np.sin(ang)+(t[:,:,2]-44.2)*np.cos(ang)
 paint(xx(36.2,60.8)&yy(-19,19)&np.all(abs(localz-1.5)<.003,axis=1)&(n[:,2]>.9),5,'confirmed_small_sloped_roof_PV_upper_only')
 paint(hi[:,2]<=2.4001,0,'neutral_original_base_no_landscape_invention')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU K2 Teaching Building 1 original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuuk2-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official K2 photos 1,2,3,4; uncalibrated colors','scope':'Gray walls and stairs, pale shading fins and end frames, green long window frames, discrete glazing. Both roof upper surfaces verified PV by aerial; coarse original grid does not reproduce exact panel coverage. Undersides silver gray, unregistered surfaces neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
