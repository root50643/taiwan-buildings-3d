"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='e0efff925d6cbb46a0765f500d8048e8fb74f3895411f6ce0cf4f4b3d26857be'
PALETTE=[('neutral_unknown','#AAA79F'),('salmon_brick_courtyard','#B4897E'),('blue_slate_roof_tile','#566B7B'),('gray_existing_lintels_canopy','#99A5A3'),('muted_green_gray_glazing_proxy','#6D8581')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_outer_long_rear_flatroof_and_unsplit_courtyard_base_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.001)&(hi[:,2]<=b+.001)
 def xx(a,b):return (lo[:,0]>=a-.001)&(hi[:,0]<=b+.001)
 def yy(a,b):return (lo[:,1]>=a-.001)&(hi[:,1]<=b+.001)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.001,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,30.5)&xx(-40,40)&zz(4.7,67.7),1,'observed_courtyard_crossbar_front_salmon_brick')
 paint(box(-9,9,24.5,30.5,4.7,77.7)&(n[:,1]<-.1),1,'central_projecting_tower_front_brick')
 paint(plane(1,24)&xx(-11,11)&zz(77,84),1,'observed_central_front_gable_brick')
 for side in [-1,1]:
  paint(plane(0,side*40)&yy(-57.5,30.5)&zz(4.7,67.7),1,'observed_inner_wing_brick_wall')
  paint(plane(1,-57.5)&xx(side*53-13,side*53+13)&zz(4.7,67.7),1,'documented_front_endwall_brick')
  for y in [-47,-35,-23,-11,1,13,25]:
   x=side*39.5;paint(box(x-1.6,x+1.6,y-4.4,y+4.4,7,64.2),1,'existing_inner_bay_masonry_brick_not_all_glass')
   for row in range(5):
    z=8+row*11.4
    paint(plane(0,side*39)&yy(y-3.35,y+3.35)&zz(z,z+7.3),4,'inner_projecting_bay_discrete_recess_back')
    q=side*37.9;paint(box(q-1.9,q+1.9,y-4.75,y+4.75,z+7.3,z+8.4),3,'original_inner_bay_lintel_gray')
  for z in [9,20.4,31.8,43.2,54.6]:paint(plane(1,-56.5)&xx(side*53-2,side*53+2)&zz(z,z+5),4,'front_endwall_narrow_window_recess')
 for row in range(5):
  z=8+row*11.4
  for x in [-34,-23,-12,12,23,34]:
   paint(plane(1,31.5)&xx(x-2.9,x+2.9)&zz(z,z+6.8),4,'crossbar_discrete_window_recess')
   paint(box(x-3.8,x+3.8,28.7,31.5,z+6.8,z+7.8),3,'crossbar_existing_lintel_gray')
 for z in [8,19.4,30.8,42.2,53.6,65]:
  paint(plane(1,25.5)&xx(-7,7)&zz(z,z+7.2),4,'central_stack_discrete_window_recess')
  paint(box(-9.25,9.25,23.1,25.7,z+7.2,z+8.2),3,'central_existing_lintel_gray')
 paint(box(-12,12,12,26,13.4,14.9),3,'existing_central_entrance_canopy_gray')
 for x in [-53,53]:
  paint(box(x-14.2,x+14.2,-58.7,58.7,67.4,77.8)&(n[:,2]>.1),2,'source_blue_slate_hip_roof_tiles_NOT_PV_bounded_same_roof_material')
  for y in [-35,0,35]:
   for side in [-1,1]:
    q=x+side*7.7
    paint(box(q-5,q+5,y-7,y+7,69.2,75.2)&(abs(n[:,2])<.1),1,'dormer_masonry_same_system_bounded_extension')
    paint(box(q-5.7,q+5.7,y-7.5,y+7.5,75,79)&(n[:,2]>.1),2,'existing_dormer_sloped_tile_roof')
    paint(plane(0,q+side*4.2)&yy(y-5,y+5)&zz(70.6,74),4,'existing_dormer_window_back_proxy')
 paint(box(-11,11,24,44,77,84)&(n[:,2]>.1),2,'central_gable_sloped_tile_roof')
 paint(hi[:,2]<=4.8001,0,'neutral_original_base_no_grass_paving_or_trees_invented')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU M6 Sixth Dormitory original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuum6-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official M6 Sixth Dormitory complete photos1 and3; uncalibrated proxies','scope':'U courtyard and front endwalls salmon brick, existing gray lintels, discrete graygreen window backs and slate tiled roofs NOT PV. Same roof and dormer material extension bounded. Outer long walls rear and flatroof courtyard base neutral; no round dining hall or greenery.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
