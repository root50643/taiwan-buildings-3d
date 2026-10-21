"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='9e1da09414c48e445598abe41ed5f8027a793f9e455bb69a7fe1dc50fd8e7be6'
PALETTE=[('neutral_mixed_or_unseen','#AAA79F'),('pale_ivory_structural_ribs','#D2D0C2'),('muted_blue_center_glazing','#5D8794'),('silvery_gray_center_mullions','#989E9B'),('muted_grayblue_wing_windows','#738083')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_facade_gray_sill_and_ivory_wall_or_unknown_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.004)&(hi[:,2]<=b+.004)
 def xx(a,b):return (lo[:,0]>=a-.004)&(hi[:,0]<=b+.004)
 def yy(a,b):return (lo[:,1]>=a-.004)&(hi[:,1]<=b+.004)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 for side in [-1,1]:
  x=side*34;y=3;a=np.deg2rad(-side*12);dx=t[:,:,0]-x;dy=t[:,:,1]-y;u=dx*np.cos(a)+dy*np.sin(a);v=-dx*np.sin(a)+dy*np.cos(a)
  def uu(a,b):return (u.min(axis=1)>=a-.004)&(u.max(axis=1)<=b+.004)
  def vv(a,b):return (v.min(axis=1)>=a-.004)&(v.max(axis=1)<=b+.004)
  def vp(a):return np.all(abs(v-a)<.004,axis=1)
  for w in [-28,-9,10,28]:paint(uu(w-.9,w+.9)&vv(-18.8,-14.8)&zz(3,123),1,'source_photo3_registered_AB_large_ivory_front_ribs_component_extension')
  for z in range(8,109,10):
   for w in [-22,-13,-4,5,14,23]:paint(vp(-14.5)&uu(w-3.5,w+3.5)&zz(z,z+5.8),4,'discrete_wing_windows_muted_proxy_no_blind_or_AC_reproduction')
 paint(plane(1,-19)&xx(-5.75,5.75)&zz(8,119),2,'photo3_AB_narrow_center_seam_blue_glass_not_other_wide_tower')
 for z in range(9,120,5):paint(box(-6,6,-22.25,-18.75,z,z+1),3,'existing_center_horizontal_silver_mullions')
 for x in [-3,3]:paint(box(x-.55,x+.55,-22.25,-18.75,8,119),3,'existing_center_vertical_silver_mullions')
 paint(box(-11,11,-31,-19,14,16)&(norm[:,2]<.0001),1,'visible_entry_canopy_edges_and_soffit_not_unseen_top')
 for x in [-9,9]:paint(box(x-.9,x+.9,-29,-27,3,14.3),1,'photo3_entry_canopy_posts')
 # No black semicircle: the source railing is not separate geometry from the original ledge.
 paint(hi[:,2]<=3.0001,0,'unsplit_base_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU Qing AB Limited Glazing and Structure Appearance original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthuqing-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTHU official housing photo3 independently registered to A/B labels; 2026-07-15 camera Original metadata, not independently authenticated; uncalibrated proxies','scope':'Limited front center blue seam and silver mullions, pale large wing ribs, discrete subdued windows and canopy edges. Broad wing faces cross unmodeled ivory/gray bands and stay neutral; round ledges are not black railings; other wide glazed towers not substituted; rear/roof neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
