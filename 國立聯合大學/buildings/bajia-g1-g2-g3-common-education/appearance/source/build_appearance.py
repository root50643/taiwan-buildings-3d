"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='c476be899203e050a5f35e5d4f2224f6f92a4761ca9556cf111c7efc7b0c5d90'
PALETTE=[('neutral_unseen','#AAA79F'),('warm_gray_structure','#ABA99F'),('cream_towers','#C8C2AF'),('pale_bluegray_concrete','#9EB5BB'),('muted_grayblue_glazing','#627A83'),('navy_PV','#4D6683'),('brown_rail_proxy','#8A7770'),('gray_paving','#B7B8AF')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_rear_mixed_corridor_and_unsplit_brick_grass_regions_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.001)&(hi[:,2]<=b+.001)
 def xx(a,b):return (lo[:,0]>=a-.001)&(hi[:,0]<=b+.001)
 def yy(a,b):return (lo[:,1]>=a-.001)&(hi[:,1]<=b+.001)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.001,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-14)&xx(-49,48)&zz(4.8,37),1,'observed_G2_warmgray_front_structure_not_corridor_glass')
 paint(plane(1,27)&xx(-49,45)&zz(7.8,47),1,'observed_G3_warmgray_front_structure_not_corridor_glass')
 paint(box(-49,-37,-17,7,4.8,51)&(plane(1,-17)|plane(0,-49)|plane(0,-37)),2,'observed_G2_cream_tower_exterior')
 paint(box(37,48,23,46,7.8,56)&(plane(1,23)|plane(0,37)|plane(0,48)),2,'observed_G3_cream_tower_exterior')
 for z in [18,29,40]:
  paint(box(-53,-48,-15,6,z,z+1.5),7,'original_G2_side_landing_gray')
  paint(box(-53,-51.8,-15,6,z+1.4,z+2.7),6,'original_G2_solid_rail_proxy_brown')
 for z in [16,27,38]:
  paint(box(47,54,24,43,z,z+1.5),7,'original_G3_side_landing_gray')
  paint(box(52.7,54,24,43,z+1.3,z+2.7),6,'original_G3_solid_rail_proxy_brown')
 for a,b,c,d,e,f in [(47,49,-21,8,4.8,35),(61,63,-21,8,4.8,25),(53,55,-18,8,24.8,35),(47,55,-18,8,34,36)]+[(47,63,-21,8,z,z+1.7) for z in [5,15,25]]:
  paint(box(a,b,c,d,e,f),3,'observed_G2_shifted_stair_frame_bluegray_CONCRETE_not_glass')
 for z in [6.5,16.5]:
  for i in range(12):paint(box(49+i,50.1+i,-20.8,-14.5,z-.2,z+.8+i*.75)&(n[:,2]>.9),7,'original_G2_stair_tread_gray')
 for i in range(8):paint(box(49+i*.5,49.6+i*.5,-17.8,-12,26.5,27.3+i*.95)&(n[:,2]>.9),7,'original_upper_stair_tread_gray')
 paint(box(-17,5,-19,-13,14,15.5)|box(-17,-15.5,-19,-13,4.8,15)|box(3.5,5,-19,-13,4.8,15),1,'original_entry_canopy_and_piers_gray_no_lettering')
 paint(xx(-62,-52)&zz(8,14)&plane(1,-17.8),4,'original_G2_lower_pavilion_window_back_only')
 paint(xx(-59,-51)&zz(13,22)&plane(1,20),4,'original_G3_lower_pavilion_window_back_only')
 for region in [box(-65.5,-64.2,-20,10,18,19.5),box(-65.5,-49,-20,-18.8,18,19.5),box(-62.5,-61.2,18.5,46,28,29.6),box(-62.5,-47,18.5,19.8,28,29.6)]:paint(region,6,'original_low_pavilion_thick_parapet_brown_proxy')
 for a,b,y,zbase,top in [(-49,48,-14,4.8,37),(-49,45,27,7.8,47)]:
  for z in np.arange(zbase+2.5,top-6,10):
   for x in np.arange(a+2,b-5,14):paint(box(x,min(x+11,b-2),y+.05,y+1,z-.15,z+1),6,'original_corridor_low_rail_proxy_not_glass')
 # G1: only original front pocket backs. No large terrace grass guess.
 for i in range(20):
  x=-49+i*4.7;front=-43+3.3*((x+2)/47)**2
  paint(box(x,x+4.85,front-.001,front+.001,2.8,12),1,'observed_G1_segmented_gray_front')
  paint(box(x,x+4.85,front-.4,front+.8,13,14.2),6,'original_G1_solid_front_rail_proxy')
  if i%4!=3:paint(xx(x+.55,x+4.1)&zz(5.2,10.1)&plane(1,front+1.05),4,'original_G1_discrete_window_back')
 for i in range(26):
  x=-46+i*3.4;y=-32+5*np.sin((x+46)/88*np.pi)
  paint(box(x,x+3.6,y,y+2.2,12.5,13.25)&(n[:,2]>.9),7,'original_curved_paving_relief_gray_no_fake_grass_divisions')
 for x,y,r in [(-29,-29,3.3),(-3,-31,3.4),(23,-28,3.0)]:paint(box(x-r,x+r,y-r,y+r,12.7,13.9),6,'original_round_planter_disk_proxy_no_tree_geometry')
 paint(box(-59,-50,-45,-19,3,13)&(n[:,2]>.9),7,'original_front_access_stair_treads_gray')
 paint(box(-64,-57,6,19,3,14)&(n[:,2]>.9),7,'original_rear_access_stair_treads_gray')
 for a,b,c,d,z,h,cols in [(-33,-2,-11,7,37,3.5,6),(12,30,-11,7,37,3.5,4),(-48,-22,28,45,47,3.6,5),(-7,32,28,45,47,3.6,8)]:
  for i in range(cols):
   for j in range(3):
    x=a+(b-a)*i/cols;y=c+(d-c)*j/3;dy=(d-c)/3-.5;z0=z+.9+(h-.9)*(y-c)/(d-c);h2=.65+(h-.9)*dy/(d-c)
    predicted=z0+.68+(h2-.9)*(t[:,:,1]-y)/dy
    paint(xx(x,x+(b-a)/cols-.55)&yy(y,y+dy)&np.all(abs(t[:,:,2]-predicted)<.001,axis=1)&(n[:,2]>.8),5,'original_PV_wedge_tile_top_plane_only_not_roof_backing')
 paint(hi[:,2]<=3.0001,0,'neutral_display_base')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU G1 G2 G3 Common Education original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuug-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official G1 G2 G3 2025 gallery photos11/7; uncalibrated proxies','scope':'Warmgray fronts, cream towers, pale bluegray CONCRETE stair frames, original small pane backs and PV top planes only. Broad mixed corridors are NOT glazing. Unsplittable brick/gray and grass/paved terrace boundaries neutral; no false red doors, trees or letters.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
