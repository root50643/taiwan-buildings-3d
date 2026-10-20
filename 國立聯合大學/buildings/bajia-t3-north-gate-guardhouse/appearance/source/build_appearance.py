"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='03d2946862654c01a411cf3011a7334c5b1588613af650583f55343aec047cb5'
PALETTE=[('neutral_unseen','#AAA79F'),('pale_gray_stone','#B5BAB5'),('salmon_brick','#B57C69'),('turquoise_waterproofing','#5EAAA5'),('muted_booth_glazing','#536A76'),('blank_pale_plaque','#C6C4AF'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unobserved_rear_and_unknown_surface_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def xx(a,b):return (lo[:,0]>=a-.00025)&(hi[:,0]<=b+.00025)
 def yy(a,b):return (lo[:,1]>=a-.00025)&(hi[:,1]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 paint(xx(51,63)&yy(-7,15)&zz(2.4,59.3)&(n[:,1]<.1),1,'source_visible_right_tower_front_sides_top_stone_back_neutral')
 paint(xx(-63.5,-56.5)&yy(-8.5,14.5)&zz(2.4,36.3)&(n[:,1]<.1),1,'source_left_outer_wall_stone_front_and_sides')
 paint(xx(-58,-52)&yy(-7.5,13.5)&zz(2.4,33.3)&(plane(0,-52)|plane(1,-7.5)),2,'source_narrow_inner_left_wall_brick_visible_planes_only')
 paint(xx(46.5,65.5)&yy(-10.5,-5.5)&zz(2.4,27.3)&(plane(1,-10.5)|plane(0,46.5)),2,'source_low_right_wall_brick_not_tall_tower')
 # Cylinders visibly gray. Circumferential material continuity is bounded proxy.
 for x in [-44,40]:
  for y in [-8,12]:paint(xx(x-1.7,x+1.7)&yy(y-1.7,y+1.7)&zz(2.4,34.2),1,'existing_gate_cylinder_gray_material_continuity_proxy')
 paint(xx(-8,8)&yy(-11,9)&zz(2.4,21.3)&(n[:,1]<.1),1,'booth_front_and_sides_gray_frame_unknown_back_neutral')
 paint(xx(-6.5,6.5)&plane(1,-10.4)&zz(8,18),4,'original_front_booth_recess_glazing_only_no_new_mullions')
 paint(xx(-10,10)&yy(-13,11)&zz(21.1,23.1),1,'existing_booth_cap_gray_edges')
 paint(xx(-10,10)&yy(-13,11)&plane(2,23.1),3,'observed_booth_cap_top_turquoise_only')
 for x in [-7,7]:
  for y in [-8,8]:paint(xx(x-1.15,x+1.15)&yy(y-1.15,y+1.15)&zz(22.8,34.4),1,'existing_short_canopy_supports_gray')
 paint(zz(34,38)&(n[:,2]>=-.1),1,'observed_canopy_ribs_and_top_gray_underside_neutral')
 paint(plane(2,35.5),3,'observed_coffer_horizontal_floors_turquoise_not_ribs')
 paint(xx(48,64)&yy(-11.7,-10.3)&zz(11,15.3),5,'existing_low_name_plaque_blank_no_letters')
 paint(xx(53,61)&yy(-7.7,-6.7)&zz(42,54),5,'existing_tower_plaque_blank_no_letters')
 paint(hi[:,2]<=2.4001,6,'display_base_not_road_markings_or_site_surface')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU Bajia North Gate And Guardhouse original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuugate-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated NUU official north gate photo6; EXIF2025-03-02 not independently verified','scope':'Existing gate and booth ensemble only. Gray stone tower/ribs, visible low brick walls, turquoise coffer floors and booth cap top, front booth recess glazing. Unseen rear neutral; cylinder/support material continuity explicitly bounded. Blank plaques no lettering.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
