"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='98fb990a7022ba6d1e75fbf80bd52ff07e5b2f5daf5a17f8a529b2b4d8acb8e6'
PALETTE=[('neutral_unknown','#AAA79F'),('pale_gray_north_cladding','#C7C9C6'),('warm_sandstone_colonnade','#B99277'),('dark_recessed_glazing_proxy','#53616A')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_ends_roof_ground_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def between(v,a,b):return np.all((v>=a-.003)&(v<=b+.003),axis=1)
 def plane(v,a):return np.all(abs(v-a)<.003,axis=1)
 X=t[:,:,0];Y=t[:,:,1];Z=t[:,:,2]
 for cx,cy,w,d,h,angle,end in [(-46,2,43,23,32,0,4),(-1,2,49,24,37,0,5),(46,-1.2,43,23,33,-8,4)]:
  a=np.deg2rad(angle);u=(X-cx)*np.cos(a)+(Y-cy)*np.sin(a);v=-(X-cx)*np.sin(a)+(Y-cy)*np.cos(a)
  paint(between(u,-w/2,w/2)&between(v,-d/2-.6,-d/2+.55)&between(Z,2.4,2.4+h),1,'north_visible_pale_gray_cladding_and_integral_ribs')
  n=max(4,round((w-2*end)/6.4));pitch=(w-2*end)/n
  for i in range(n):
   x=-w/2+end+pitch*(i+.5)
   for j in range(4):
    z=10+j*6.1
    if z+4.5<2.4+h-2:paint(plane(v,-d/2+.55)&between(u,x-(pitch-1.25)/2,x+(pitch-1.25)/2)&between(Z,z,z+4.5),3,'north_existing_recess_back_dark_glazing_proxy')
  for x in np.arange(-w/2+2,w/2-1,6.1):paint(between(u,x-.8,x+.8)&between(v,-d/2-3.9,-d/2-2.1)&between(Z,2.35,10.15),2,'photo_warm_stone_colonnade_pier_not_ground_wall')
  paint(between(u,-w/2,w/2)&between(v,-d/2-4.05,-d/2-1.95)&between(Z,9.2,10.3),2,'photo_warm_stone_colonnade_beam')
 paint(between(X,-24.8,-21.2)&between(Y,-10.3,-10)&between(Z,2.35,42.75),1,'documented_high_pale_middle_margin')
 paint(plane(Y,-10.6)&between(X,21.5,26.5)&between(Z,2.35,32.85),1,'front_connecting_seam_pale_frame')
 for z in np.arange(5,31,3):paint(plane(Y,-10.05)&between(X,22.4,25.6)&between(Z,z,z+2.1),3,'connector_existing_glazing_back_proxy')
 # Entrance in old geometry is approximate; no new lettering, security or equipment.
 paint(between(X,-12.5,-3.5)&between(Y,-11.65,-10.55)&between(Z,2.35,9.85),1,'existing_entry_pale_frame_proxy')
 for x in [-10,-6]:paint(plane(Y,-11.2)&between(X,x-1.35,x+1.35)&between(Z,3.1,9),3,'existing_entry_door_back_proxy')
 paint(hi[:,2]<=2.4001,0,'original_ground_base_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NHRI Zhunan Administration original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nhriadmin-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Taiwan Green Building Council association case photo explicitly captioned Administration north side; uncalibrated proxies','scope':'Pale north cladding and ribs, warm stone only colonnade piers/beams, dark existing window backs. Simplified wing spacing and recessed glazing preserved; unknown roof, ends, rear and ground neutral. Association publication 2014, capture unknown; not NHRI current-condition evidence.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
