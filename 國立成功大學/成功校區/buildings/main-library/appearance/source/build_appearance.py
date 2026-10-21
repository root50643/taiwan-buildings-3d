"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='7155baa4b504bdba7eb6f9303fc93b72fc9f87a3af1f454290599b69037158af'
PALETTE=[('neutral_unregistered_roof_rear_base','#AAA79F'),('muted_pinkgray_tile','#B6A1A0'),('silvergray_shade_blades','#A3ACA8'),('warm_offwhite_small_colonnade','#D2D0C5'),('dark_graygreen_glazing_proxy','#5D7470')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_roofs_rear_left_and_base_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.004)&(hi[:,2]<=b+.004)
 def xx(a,b):return (lo[:,0]>=a-.004)&(hi[:,0]<=b+.004)
 def yy(a,b):return (lo[:,1]>=a-.004)&(hi[:,1]<=b+.004)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-45)&xx(-67,51)&zz(24,51),1,'day_source_registered_projecting_pinkgray_tile_front')
 paint(plane(2,24)&xx(-67,51)&yy(-45,-20.5),1,'source_visible_cantilever_soffit_same_tile_system_proxy')
 paint(plane(1,-20.5)&xx(-67,57)&zz(2.9,48.9),1,'registered_recessed_lower_front_tile')
 paint(plane(1,-41)&xx(47,69)&zz(2.9,66.9),1,'registered_pinkgray_stair_tower_front_no_invented_fine_white_lines')
 paint(plane(0,69)&yy(-41,46)&zz(2.9,67),1,'source_day_and_night_registered_right_tower_and_wing_tile')
 paint(plane(1,-12)&xx(45,69)&zz(26,51),1,'source_registered_right_lowwing_front_tile')
 # Lower entrance walls, not its unobserved roof top.
 paint(box(-37,1,-51.5,-24.5,3,17)&(abs(norm[:,2])<.0001),1,'source_low_entry_vertical_pinkgray_tile_shell')
 paint(box(-37.5,1.5,-52,-24,16.5,17.9)&(norm[:,2]<=.0001),1,'source_low_entry_canopy_edge_soffit_not_roof')
 for x in [-64,-44,-24,-4,16,36,48]:
  rr=np.sqrt((t[:,:,0]-x)**2+(t[:,:,1]+37)**2)
  paint(np.all(rr<=1.554,axis=1)&zz(2.9,24.1),1,'large_recessed_support_columns_pink_tile_not_white_foreground_columns')
 for x in [-56,-36,-16,4,24,44]:
  for z in [30,32.5,35,37.5,40,42.5]:paint(box(x-9,x+9,-48.4,-42.6,z,z+1.2),2,'source_existing_projecting_silvergray_shade_blade_no_fake_fine_grid')
  paint(plane(1,-43.1)&xx(x-8,x+8)&zz(30,45),4,'source_upper_glazing_actual_back_only')
  paint(plane(1,-44.1)&xx(x-8,x+8)&zz(25.3,28.4),4,'source_under_shade_window_strip_actual_back')
  for z in [6,16]:paint(plane(1,-19.6)&xx(x-8,x+8)&zz(z,z+6.5),4,'source_lower_window_actual_back_no_invented_mullions')
 for z in [9,20,31,42,55]:paint(plane(1,-40.1)&xx(55.5,60.5)&zz(z,z+5.5),4,'source_stair_tower_small_window_actual_back')
 for y in [1,19,37]:
  for z in [29,38,46]:paint(plane(0,68.1)&yy(y-6.5,y+6.5)&zz(z,z+3.8),4,'source_registered_right_wing_window_back')
 for x in [-31,-18,-5]:paint(plane(1,-50.6)&xx(x-3.5,x+3.5)&zz(4.5,15),4,'source_entry_glass_door_field_proxy_not_opaque_door_panel')
 for x in [-64,-52,-40,13,25,37,49,61]:
  rr=np.sqrt((t[:,:,0]-x)**2+(t[:,:,1]+48)**2)
  paint(np.all(rr<=1.304,axis=1)&zz(3,14.5),3,'source_small_foreground_colonnade_white_tile_component')
 paint(box(-69,69,-50,-43,14,15.8),3,'source_small_foreground_colonnade_white_beam_component_extension')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU Main Library Source Bounded Appearance original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nckulib-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NCKU official library daytime photo camera Original2025-01-13, modified2025-01-20; nighttime used for registration only, no baked yellow illumination','scope':'Registered front and right pinkgray tile, large pink tile support columns, separate small offwhite foreground colonnade, original silvergray shade blades and exact glazing recess backs only. Rear/left/roof/base neutral; fine tower stripes/tile seams/mullions not invented, unseen component faces bounded material extension.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
