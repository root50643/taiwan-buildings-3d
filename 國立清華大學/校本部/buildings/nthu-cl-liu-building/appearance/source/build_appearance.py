"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='0e8e28b8b1fa8a6e96ee1859b7c445de0a4135bb980f68e03607aac9d6439260'
PALETTE=[('neutral_unknown','#AAA79F'),('warm_white_wall','#D0D1C9'),('pale_silver_mesh_grid','#C3CBC8'),('charcoal_bronze_sunshades','#5A5952'),('muted_shadowed_window_proxy','#7A827D'),('gray_stone_steps','#969D97')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_roof_caps_far_rear_and_unregistered_surfaces_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 # Registered courtyard and both source-supported outer wings only.
 for side,h in [(-1,72),(1,104)]:
  paint((plane(0,side*31.5)|plane(0,side*62.5))&yy(-45,51)&zz(3,h),1,'source_white_courtyard_and_outer_wall')
  a,b=sorted([side*31.5,side*62.5]);paint(plane(1,-45)&xx(a,b)&zz(3,h),1,'source_white_wing_front_end')
  zs=[10,23,36,49,62] if side<0 else [10,23,36,49,62,75,88]
  for z in zs:
   for y in [-35,-20,-5,10,25]:
    paint(plane(0,side*33.25)&yy(y-5,y+5)&zz(z,z+9),4,'source_window_mesh_merged_recess_muted_proxy_NOT_all_exposed_glass')
    a,b=sorted([side*31.5-2,side*31.5+2]);paint(box(a,b,y-.6,y+.6,z,z+9)|box(a,b,y-5,y+5,z+4.5,z+5.6),2,'source_original_pale_window_crossbars')
  for z in range(10,h-7,13):
   for y in [-31,-15,1,17,33]:
    paint(plane(0,side*61)&yy(y-5,y+5)&zz(z,z+9),4,'source_outer_window_mesh_merged_recess_muted_proxy')
    a,b=sorted([side*62.5-1.75,side*62.5+1.75]);paint(box(a,b,y-.6,y+.6,z,z+9),2,'source_outer_existing_window_grid')
 paint(plane(1,29.5)&xx(-54,54)&zz(3,104),1,'source_white_courtyard_crossbody')
 for z in [10,23,36,49,62,75,88]:
  for x in [-26,-13,13,26]:
   paint(plane(1,31.25)&xx(x-4.5,x+4.5)&zz(z,z+9),4,'source_center_window_recess_muted_proxy')
   paint(box(x-.55,x+.55,27.5,31.5,z,z+9)|box(x-4.5,x+4.5,27.5,31.5,z+4.5,z+5.6),2,'source_original_center_silver_crossbars')
 paint(box(-7,7,25,30,28,110),2,'source_center_mesh_strip_proxy_weave_omitted')
 for z in [29,66,97]:
  for zz0 in [z,z+2]:
   paint(box(-33.5,33.5,23,29,zz0,zz0+1.4),3,'source_dark_center_sunshade_rib')
   for side,h in [(-1,72),(1,104)]:
    if z<h:
     paint(box(side*30-3,side*30+3,-41.5,43.5,zz0,zz0+1.4),3,'source_dark_courtyard_sunshade_rib')
     paint(box(side*63-2,side*63+2,-44,48,zz0,zz0+1.4),3,'source_dark_outer_sunshade_rib')
 for x in [-16,16]:paint(box(x-1.75,x+1.75,8.5,15.5,3,21),1,'source_white_entry_portal_pier')
 paint(box(-18,18,8.5,15.5,20,23),1,'source_white_entry_portal_header')
 paint(plane(1,23)&xx(-7.5,7.5)&zz(5,18),4,'source_shadowed_entry_back_proxy')
 paint(box(-12,12,4,28,23,45),2,'source_original_tilted_open_cube_silver_proxy')
 paint(box(-1.1,1.1,14.9,17.1,22,35),2,'source_cube_existing_support')
 for i in range(7):
  for x in [-11,11]:paint(box(x-9,x+9,-35.5+i*6,-28.5+i*6,3,4+i*1.8),5,'source_gray_split_stairs')
 for z in [12,25,38,51,64]:paint(box(-65,-51,-51,-37,z,z+1.8),1,'source_pale_halfround_stair_slab_proxy')
 paint(hi[:,2]<=3.0001,0,'unsplit_base_not_planted_center_strip')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU C L Liu Building original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthuliu-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTHU night identity and designer daylight post-renovation photographs, uncalibrated proxies','scope':'Source-supported white courtyard and outer wings, charcoal bronze sunshade ribs, pale original grids and center mesh/artwork, muted merged window/mesh recess proxy. Unknown roof cones and far back neutral. No night illumination colors or added mesh weave.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
