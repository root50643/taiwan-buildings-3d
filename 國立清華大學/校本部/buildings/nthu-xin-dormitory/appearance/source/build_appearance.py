"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='b2e1d1ba92c36a14e296f1400752af00738c6df3cc83256686be89ae5fd5e676'
PALETTE=[('neutral_unknown_or_mixed','#AAA79F'),('dusty_mauve_brick_infill','#967F88'),('pale_ivory_tile_ribs','#D0CFC1'),('muted_grayblue_window_proxy','#718080')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_mixed_or_unregistered_surfaces_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 for x,y,angle in [(-57,-1,24),(-30,8,12),(-5,12,0),(31,8,-12),(58,-1,-24)]:
  a=np.deg2rad(angle);dx=t[:,:,0]-x;dy=t[:,:,1]-y;u=dx*np.cos(a)+dy*np.sin(a);v=-dx*np.sin(a)+dy*np.cos(a)
  def uu(a,b):return (u.min(axis=1)>=a-.004)&(u.max(axis=1)<=b+.004)
  def vv(a,b):return (v.min(axis=1)>=a-.004)&(v.max(axis=1)<=b+.004)
  def vp(a):return np.all(abs(v-a)<.004,axis=1)
  paint(vp(-14.2)&uu(-6.25,6.25)&zz(9,103),1,'registered_front_fold_bounded_mauve_brick_recess_not_entire_wing')
  for z in [13,25,37,49,61,73,85,97]:
   for w in [-3.4,3.4]:paint(vp(-12.2)&uu(w-2.1,w+2.1)&zz(z,z+7.4),3,'discrete_window_back_muted_proxy_no_frames_or_AC_added')
  for w in [-7.5,0,7.5]:paint(uu(w-.75,w+.75)&vv(-17.25,-13.75)&zz(3,107),2,'three_existing_ivory_front_ribs_component_bounded_extension')
  paint(vp(-15.5)&uu(-8.5,8.5)&zz(103,107),2,'existing_complete_top_front_header')
 paint(hi[:,2]<=3.0001,0,'unsplit_base_and_forecourt_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU Xin Dormitory Bounded Appearance original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthuxin-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official public NTHU housing photos, EXIF Original 2026-06-03 camera metadata, not independently authenticated; uncalibrated surface proxies','scope':'Only five registered front folded bays: bounded mauve infill, pale ribs and complete top header faces, discrete muted window backs. Mixed circular portal, linking gallery backs, forecourt, rear and roof neutral; no air conditioners, text or private detail.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
