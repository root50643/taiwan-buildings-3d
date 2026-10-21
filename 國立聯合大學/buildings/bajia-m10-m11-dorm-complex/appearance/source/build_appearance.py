"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='104fd23d439f48bc6638eeb16e5f1ea905a918f255f6683fe2787a6f80f6d028'
PALETTE=[('neutral_unknown','#AAA79F'),('pale_gray_vertical_fins','#C7CDD0'),('gray_lilac_front_infill','#A2A3AC'),('medium_gray_endwalls','#A5ABB2'),('muted_dark_glazing_proxy','#53636E'),('offwhite_service_enclosure','#D6D7D0')]
def classify(tri):
 t=tri;n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_rear_roof_unsplit_ground_and_undercroft_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 for side in [-1,1]:
  ang=np.deg2rad(-side*24);q=t.copy();q[:,:,0]-=side*38;q[:,:,1]-=8
  u=q.copy();u[:,:,0]=q[:,:,0]*np.cos(ang)+q[:,:,1]*np.sin(ang);u[:,:,1]=-q[:,:,0]*np.sin(ang)+q[:,:,1]*np.cos(ang)
  lo=u.min(axis=1);hi=u.max(axis=1)
  def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
  def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
  def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
  def plane(i,v):return np.all(abs(u[:,:,i]-v)<.003,axis=1)
  def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
  paint(plane(1,-10.5)&xx(-32.5,32.5)&zz(9.3,58),2,'documented_front_solid_infill_not_glass')
  for x in np.linspace(-30.5,30.5,27):paint(box(x-.5,x+.5,-12.25,-9.75,9.1,59.2),1,'front_existing_pale_vertical_fins_only')
  for row in range(6):
   z=11+row*7.5
   for x in np.linspace(-29.33,29.33,26):paint(plane(1,-9.7)&xx(x-.7,x+.7)&zz(z,z+4.8),4,'front_discrete_narrow_recess_glazing')
  x=side*32;paint(box(x-.8,x+.8,-11.4,10.8,4,59.2),3,'documented_outer_endwall_gray')
  for x in [-24,-8,8,24]:paint(box(x-1.05,x+1.05,-10.75,-8.65,4,9.7),1,'visible_undercroft_column_not_dark_glass')
  x=side*24
  paint(box(x-6,x+6,-6,9,59.1,65.9)&(abs(n[:,2])<.1),5,'service_enclosure_vertical_faces_bounded_same_material')
  paint(plane(1,-5)&xx(x-2.5,x+2.5)&zz(61,63),4,'existing_service_enclosure_recess_no_equipment')
 # Central link is explicitly open; only masonry frame fronts are pale gray.
 lo=t.min(axis=1);hi=t.max(axis=1)
 paint((lo[:,0]>=-8.501)&(hi[:,0]<=8.501)&(lo[:,1]>=12.499)&(hi[:,1]<=13.551)&(lo[:,2]>=9.199)&(hi[:,2]<=59.701),1,'central_open_link_front_structure_not_infilled')
 paint(hi[:,2]<=4.1001,0,'unsplit_landscape_base_neutral_no_fake_grass')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU M10 M11 Dormitory Complex original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuum1011-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official M10 M11 complete front aerial photos 10 and 11; uncalibrated proxies','scope':'Front pale fins and gray lilac infill, narrow discrete window backs and gray outer ends. Service enclosure same-material vertical extension bounded. Rear walls main roof and unsplit landscaped base neutral; undercroft not glazing; central original straight open connector retained.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
