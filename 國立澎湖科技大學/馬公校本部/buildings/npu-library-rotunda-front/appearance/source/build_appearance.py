"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='e0ea088d1f0731101ec94be59c75105435bcfb5ba3c80fc0429eec612dbc6b3e'
PALETTE=[('neutral_unverified_surfaces_and_existing_frames','#AAA79F'),('muted_gray_blue_window_backs','#5C6B6E'),('medium_gray_existing_plinth_exterior','#70706B')]
def classify(tri):
 t=tri;z=t[:,:,2];xy=t[:,:,:2];eps=.002
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'neutral_unverified_or_unsegmented_surface',dtype=object)
 def radial(a):
  q=np.deg2rad(a);return xy@np.array([np.cos(q),np.sin(q)]),xy@np.array([-np.sin(q),np.cos(q)])
 for a in [-150,-120,-90,-60,-30]:
  r,u=radial(a)
  for z0 in [52,76]:
   m=np.all((abs(r-51.5)<eps)&(abs(u)<=6.25+eps)&(z>=z0-eps)&(z<=z0+13.2+eps),axis=1)
   assert m.sum()==8
   color[m]=1;why[m]='whole_original_window_back_a%s_z%s'%(a,z0)
 for a in [-165,-135,-105,-75,-45,-15]:
  r,u=radial(a)
  bounds=np.all((z>=3-eps)&(z<=11.3+eps)&(abs(u)<=5.8+eps)&(r>=45.4-eps)&(r<=54.6+eps),axis=1)
  external=np.all(abs(r-54.6)<eps,axis=1)|np.all(abs(u-5.8)<eps,axis=1)|np.all(abs(u+5.8)<eps,axis=1)
  m=bounds&external;assert m.sum()==6 and np.all(color[m]==0)
  color[m]=2;why[m]='whole_existing_plinth_outer_vertical_faces_a%s'%a
 assert (color==1).sum()==80 and (color==2).sum()==36
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NPU Library partial rotunda entrance original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'npu-library-rotunda-front-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official NPU front and side photographs, capture dates unknown; uncalibrated display proxies, not current condition proof','scope':'Only 80 complete window-back triangles and 36 complete existing plinth exterior triangles; all other faces neutral. Continuous awning held neutral because original geometry lacks real segmented boundaries.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
