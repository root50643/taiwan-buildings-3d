"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='48e5ffb54c9b12085a444aa9ea7ff4f2e7b32d5e620d22f0ada7ad1fb0dab5e7'
PALETTE=[('neutral_mixed_or_unregistered','#AAA79F'),('warm_light_tile_proxy','#C9C6BC'),('silvergray_trim_columns','#A9AFAC'),('muted_window_field_proxy','#718080'),('gray_steps','#939995')]
def classify(tri):
 t=tri/(150/178);lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_window_spandrels_courtyard_spine_roof_and_unregistered_surfaces_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.004)&(hi[:,2]<=b+.004)
 def xx(a,b):return (lo[:,0]>=a-.004)&(hi[:,0]<=b+.004)
 def yy(a,b):return (lo[:,1]>=a-.004)&(hi[:,1]<=b+.004)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 # Day aerial registers the warm gray/ivory front. Purple cast is not material.
 paint(plane(1,-53)&xx(-58,-14)&zz(34,102),1,'registered_upper_left_front_tile_no_purple_cast')
 paint(plane(1,-55)&xx(16.3,23.3)&zz(34,99.9),1,'registered_front_stair_tower_tile')
 paint(plane(1,-53)&xx(21.5,52.5)&zz(34,98),1,'registered_right_front_tile_between_projecting_windows')
 paint(plane(0,52.5)&yy(-53,59)&zz(36,98),1,'day_aerial_registered_right_outer_tile_between_bands')
 for k in range(6):
  z=35.8+10.1*k
  paint(box(25.5,52.5,-60.25,-49.75,z+8,z+9.3),2,'existing_right_front_projecting_metal_shade')
  paint(box(50.4,55.6,-52,56,z+7.8,z+9.2),2,'registered_right_long_horizontal_shade_component')
  paint(plane(1,-57.8)&xx(28.1,49.9)&zz(z+1.3,z+7.2),3,'registered_right_front_window_field_muted_proxy_not_pane_by_pane_replica')
  paint(plane(0,50.4)&yy(-49,53)&zz(z+1.1,z+7.4),3,'day_aerial_right_ribbon_window_field_muted_proxy')
  for x in [30,36,42,48]:paint(box(x-.5,x+.5,-60.4,-57.6,z+1,z+7.4),2,'existing_right_projecting_window_mullions')
  for y in range(-44,52,8):paint(box(50.25,53.75,y-.525,y+.525,z+.9,z+7.7),2,'existing_right_long_ribbon_mullions')
 # Left projecting bay backs contain solid skirts: deliberately neutral.
 for x in [-48,-26]:
  for z in [49,59.4,69.8,80.2]:
   paint(box(x-7,x+7,-61.7,-49.7,z+8,z+9.2),2,'existing_left_window_shade_only_mixed_bay_back_neutral')
   for q in [x-3.8,x+3.8]:paint(box(q-.525,q+.525,-59.4,-56.6,z+1,z+7.8),2,'existing_left_bay_narrow_metal_frame_only')
 for x,w in [(-54,3.6),(-37,3.6),(-17,3.6),(-43,5.3),(-30,5.3)]:
  for z in [38,90]:paint(plane(1,-52)&xx(x-w/2,x+w/2)&zz(z,z+(6.4 if w==3.6 else 7)),3,'registered_front_discrete_narrow_window_back')
 for y in [-46,-29,-12,5,22,39,51]:paint(box(54,57,y-1.55,y+1.55,13.5,36.5),2,'day_aerial_right_colonnade_gray_columns')
 # Mixed lower long glazing fields and rear round tower backs remain neutral.
 for x in [-21,-7,7,21]:
  rr=np.sqrt((t[:,:,0]-x)**2+(t[:,:,1]+62)**2)
  paint(np.all(rr<=1.554,axis=1)&zz(3,31),2,'source_registered_round_entry_column_whole_component_extension')
 paint(box(-27,27,-63.65,-44.5,30,32),2,'source_registered_perforated_entry_pergola_component')
 paint(box(-15.5,15.5,-68.5,-49.5,13,14.9),2,'source_registered_lower_entry_canopy_component')
 for x in [-13,13]:
  rr=np.sqrt((t[:,:,0]-x)**2+(t[:,:,1]+66.5)**2)
  paint(np.all(rr<=1.354,axis=1)&zz(3,14),2,'source_short_entry_column_component')
 # Rear photo supports tile shell, but not whole mixed glazing galleries.
 paint(plane(1,59)&xx(-58,-14)&zz(34,102),1,'architect_rear_photo_registered_left_tile_end_only')
 paint(plane(1,59)&xx(21.5,52.5)&zz(34,98),1,'architect_rear_photo_registered_right_tile_end_only')
 for z in [38,48.4,58.8,69.2,79.6,90]:
  paint(plane(1,57.5)&xx(-54.5,-33.5)&zz(z,z+6.6),3,'architect_rear_photo_left_discrete_window_field_proxy')
  paint(plane(1,57.5)&xx(27.5,50.5)&zz(z,z+6.4),3,'architect_rear_photo_right_discrete_window_field_proxy')
 rr=np.sqrt((t[:,:,0]+22)**2+(t[:,:,1]-62)**2)
 for k in range(6):paint(np.all(rr<=11.904,axis=1)&zz(43.7+10.2*k,44.95+10.2*k),2,'rear_photo_round_tower_existing_shade_disk_not_glazing')
 for i in range(10):paint(box(-39,21,84.8-i*2.1,87.2-i*2.1,2.8,3.85+i*1.03),4,'source_registered_simplified_rear_gray_stair')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NYCU Yangming Library Research Bounded Appearance original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nycuyangming-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'EDS architect five photographs, capture dates unknown; day aerial supports warm ivory-gray, no purple film cast baked into materials','scope':'Bounded registered front/right/rear tile shell, original separate metal shades/entry columns and right ribbon/narrow/rear window fields only. Left projecting bay mixed skirts, central spine, court galleries, lower mixed glass fields, round tower glazing, rooflights and unseen surfaces neutral. Existing geometry unchanged; window color is low saturation field proxy not measured pure glazing.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
