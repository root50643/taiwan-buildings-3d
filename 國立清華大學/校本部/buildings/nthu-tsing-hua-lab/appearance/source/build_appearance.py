"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='08cf7b5915d3a6956266e7aee58791991abe907b00a7cbc5f9d7ea294448e225'
PALETTE=[('neutral_unknown_or_mixed','#AAA79F'),('dark_brown_lower_masonry','#61534C'),('offwhite_end_frame','#D0D0C8'),('pale_taupe_opaque_core','#B39D94'),('pale_aluminum_shading','#B9B9AF'),('muted_bluegray_glazing','#7B9093')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_front_pink_white_strips_and_unregistered_roof_rear_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint((plane(1,-38)|plane(0,59))&zz(2.8,31),1,'source_registered_front_right_dark_masonry_base')
 paint(plane(0,61)&zz(31,109),2,'source_white_perforated_right_wings')
 paint(plane(0,63)&yy(-10,12)&zz(29,114),3,'source_opaque_taupe_center_core_not_glazing')
 paint((plane(1,-10)|plane(1,12))&xx(61,63)&zz(31,114),3,'bounded_visible_core_returns_taupe')
 for z in [34,46,58,70,82,94]:
  paint(plane(1,-37.75)&xx(-56.5,56.5)&zz(z,z+9.5),5,'source_separate_front_glazing_behind_existing_shades')
  for x in [-53,-35,-17,1,19,37,55]:paint(box(x-.65,x+.65,-42.5,-37.5,z,z+9.5),4,'source_original_pale_vertical_shade_supports')
  for z1 in [z+1.4,z+4.1,z+6.8]:paint(box(-56.5,56.5,-42.5,-37.5,z1,z1+1.2),4,'source_original_pale_horizontal_shade_slats')
 for z in [35,47,59,71,83,95]:
  for y in [-29,-18,21,32]:paint(plane(0,58.75)&yy(y-3.4,y+3.4)&zz(z,z+7.5),5,'source_right_discrete_window_back_red_reveals_not_modeled_omitted')
 for x in [-49,-31,-13,5,23,41,53]:paint(plane(1,-36.5)&xx(x-3,x+3)&zz(19,22.5),5,'source_lower_small_window_back')
 paint(plane(1,-36.5)&xx(-45,23)&zz(7,13),5,'source_lower_long_window_back')
 for y in [-29,-16,19,31]:
  for z in [7,19]:paint(plane(0,57.5)&yy(y-3,y+3)&zz(z,z+5),5,'source_lower_right_discrete_window_back')
 paint(hi[:,2]<=3.0001,0,'unsplit_base_neutral_no_site_lawn')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU Tsing Hua Laboratory original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthulab-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Architect supplied public exterior aerial and NTHU library photographs, uncalibrated material proxies','scope':'Registered front/right dark masonry plinth, white perforated right wings, taupe opaque core, pale original shading and separate window backs. Missing red reveal details omitted; mixed pink/white front strips neutral. Unknown rear and all roof tops neutral; no plant or lab interior reconstructed.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
