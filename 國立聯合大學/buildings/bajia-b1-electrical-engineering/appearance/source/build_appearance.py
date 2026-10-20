"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='589c9726bdcb16a4223526bb177169a861018c898572503b97ccda10086699af'
PALETTE=[('neutral_unseen','#AAA79F'),('sage_lower_wall','#A3B9AC'),('deep_sage_sign_wall','#6E9991'),('offwhite_structure','#C4C8C2'),('gray_structure','#969F9F'),('cream_bridge_screen','#D5CEAF'),('muted_glazing_and_PV','#637888'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_outer_rear_and_unregistered_surface_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def xx(a,b):return (lo[:,0]>=a-.00025)&(hi[:,0]<=b+.00025)
 def yy(a,b):return (lo[:,1]>=a-.00025)&(hi[:,1]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 # Observed left flank and front, not unknown rear/right exterior.
 paint(xx(-54.5,-23)&yy(-65.5,60)&zz(2.4,83.3)&(n[:,0]<-.1),3,'observed_left_flank_offwhite_upper_structure')
 paint(xx(-52.7,-51.3)&yy(-60,60)&zz(2.4,39),1,'observed_lower_left_flank_pale_sage_only_whole_triangles')
 paint(xx(-52,-24)&plane(1,-60)&zz(66.3,82.3),3,'upper_front_left_wing_offwhite')
 paint(xx(-52.5,-23.5)&yy(-67,-65)&zz(2.4,66.7)&(n[:,1]<.1),2,'observed_broad_front_sign_wall_deep_sage_no_letters')
 paint(xx(28,52)&yy(-67.4,-29)&zz(2.4,73.3)&(n[:,1]<.1),3,'observed_front_right_stair_masses_offwhite')
 # Recesses below bridge are open corridors; neutral gray backing not blue glass.
 paint(xx(-26,26)&yy(-54,-43.5)&zz(2.4,67.3)&(n[:,1]<.1),3,'existing_front_corridor_piers_and_bands_offwhite')
 for z in [20,33,46]:paint(xx(-23.5,23.5)&plane(1,-50.9)&zz(z,z+10),4,'open_corridor_solid_model_backing_gray_not_glass')
 paint(xx(-26,26)&yy(-52.95,-49.45)&zz(56,68)&(n[:,1]<.1),5,'observed_upper_bridge_translucent_cream_screen_proxy')
 paint(xx(-26.2,26.2)&yy(-53.55,-52.6)&zz(56.3,63.1)&(lo[:,1]<-52.951),4,'existing_cross_brace_relief_gray_not_shadow_texture')
 paint(xx(-25.5,25.5)&yy(-63.5,-50.5)&zz(17.5,19.5),4,'observed_low_entry_canopy_gray')
 paint(xx(-24,24)&yy(-72,-50.5)&zz(2.4,17.5),4,'original_solid_entry_support_and_compressed_steps_gray_proxy')
 # Deep left upper bays stay gray behind pale fins; window backs only are glass.
 for y in [-43,-26,-9,8,25,42]:
  paint(plane(0,-52)&yy(y+.75,y+16.25)&zz(39,82.3),4,'observed_upper_flank_recess_gray_not_baked_shadow')
  paint(xx(-54.5,-51.5)&yy(y-.75,y+.75)&zz(39,83),3,'existing_upper_flank_fins_offwhite')
  for z in [39,53,67]:paint(xx(-53.5,-51.1)&yy(y-.3,y+14.7)&zz(z,z+1.4),3,'existing_upper_flank_cross_bands_offwhite')
  for z in [43,57,71]:paint(plane(0,-51.3)&yy(y+3.5,y+9.5)&zz(z,z+7),6,'observed_upper_flank_window_recess_back')
 for y in [-44,-29,-14,1,16,31,46]:
  for z in [8,20,32]:paint(plane(0,-51.3)&yy(y-4,y+4)&zz(z,z+5),6,'observed_lower_flank_window_back')
 paint(xx(-56.5,-51.5)&yy(48.5,57.5)&zz(2.4,90.3)&(n[:,1]<.1),3,'observed_left_tall_slit_tower_offwhite')
 paint(plane(0,-55.7)&yy(50,56)&zz(8,85),4,'tall_slit_back_gray_not_all_glass')
 paint(xx(-54.5,-25.5)&yy(48.5,59.5)&zz(83,90)&(n[:,1]<.1),3,'observed_left_roof_headroom_offwhite')
 paint(plane(1,-64.25)&xx(38.5,43.5)&zz(8,64),6,'front_right_original_vertical_glazed_recess_back')
 for z in [18,32,46]:
  paint(xx(36,50)&yy(-67.4,-64.2)&zz(z,z+1.4),4,'existing_front_balcony_slab_gray')
  paint(plane(1,-64.3)&xx(42,46)&zz(z+2,z+9),6,'existing_front_right_small_window_back')
 paint(plane(1,-59.3)&xx(-41.5,-34.5)&zz(71,78),6,'observed_upper_front_left_window_back')
 # Aerial-visible court walls are pale; no coloring unknown outer rear.
 paint((plane(0,-24)|plane(0,28)|plane(1,40))&zz(2.4,81.3),3,'aerial_visible_courtyard_wall_offwhite')
 # Conservative: courtyard window backs neutral because original window_x cut direction differs by side.
 for x,y,w,d,z in [(-38,-24,25,48,83.2),(-38,29,25,44,83.2),(0,53,47,23,81.7),(40,26,21,65,79.7)]:
  paint(xx(x-w/2,x+w/2)&yy(y-d/2,y+d/2)&zz(z,z+.85),6,'source_observed_existing_PV_pads_grid_preserved_no_new_panels')
 paint(hi[:,2]<=2.4001,7,'neutral_display_base_not_site_vegetation')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU Bajia B1 Electrical Engineering original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuub1-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated NUU official B1 photos19 and20; embedded2025 evidence not2026current','scope':'Observed front and left flank, courtyard pale walls and roof PV. Corridor backs gray not glazing; unknown outer rear/right neutral. No lettering or equipment added.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
