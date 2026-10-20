"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='942763d15936f2e908229036293b8089e634478a1a88e1d1c5795a5d31c41a43'
PALETTE=[('neutral_unseen','#AAA79F'),('gray_concrete','#A0A5A3'),('turquoise_tile','#71ADB0'),('pale_yellow_infill','#D6D09A'),('offwhite_ribs_stairs','#C7CBC6'),('muted_window_PV','#637D89'),('dark_gray_rails','#5D6B6D'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unobserved_rear_roof_or_unregistered_surface_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def xx(a,b):return (lo[:,0]>=a-.00025)&(hi[:,0]<=b+.00025)
 def yy(a,b):return (lo[:,1]>=a-.00025)&(hi[:,1]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 paint(xx(1.5,62.5)&yy(-7.5,25.5)&zz(2.4,57.3)&((n[:,1]<-.1)|(n[:,0]>.1)),1,'observed_right_front_and_stair_side_concrete')
 paint(xx(-72.5,-2.5)&yy(-4.5,2.25)&zz(2.4,43.3),1,'observed_left_front_gray_structure_and_corridor_not_glass')
 paint(xx(-72.5,-2.5)&yy(-4.5,2.25)&zz(31.85,39)&(n[:,1]<-.1),3,'existing_upper_left_infill_pale_yellow_whole_triangles_only')
 for z in [5,13.5,22,30.5,39]:paint(xx(-72,-4)&yy(.1,1.7)&zz(z,z+1.35),1,'existing_left_floor_bands_gray_not_yellow')
 for x in [-69,-51,-33,-15,-4]:paint(xx(x-.85,x+.85)&yy(-.2,1.6)&zz(4,42),1,'existing_left_front_piers_gray')
 # Only top-floor existing window backs; lower bays represent open corridors.
 for x in [-61,-42,-23,-7]:
  for xp in [x-3,x+3]:
   y=-3.75 if xp>-19.5 else 2.25
   paint(xx(xp-2.05,xp+2.05)&plane(1,y)&zz(33,37.5),5,'source_top_left_window_recess_back_only')
 for x in [14,29,44]:paint(xx(x-2.6,x+2.6)&yy(-9.45,-7.15)&zz(15,55),2,'existing_tall_front_fins_turquoise_tile')
 for x in [19,34,49]:
  for z in np.arange(17,53,2.8):paint(xx(x-1.3,x+1.3)&yy(-8.95,-7.25)&zz(z,z+.85),1,'existing_louver_relief_gray_not_turquoise')
 for x in [7,21.5,36.5,52]:
  for z in [8,17,26,35,44,51]:paint(xx(x-2.25,x+2.25)&plane(1,-6.75)&zz(z,z+4.4),5,'existing_right_front_window_back')
 for z in [6,14]:paint(xx(2,62)&yy(-8.9,-7.1)&zz(z,z+1.5),1,'existing_lower_right_bands_gray')
 paint(xx(-6.15,6.15)&yy(-15.9,-4)&zz(2.4,64)&(n[:,1]<.1),1,'observed_stair_tower_gray_not_curtain_glass')
 for x in [-4.2,-2.8,2.8,4.2]:paint(xx(x-.45,x+.45)&yy(-15.75,-14.35)&zz(3.5,63.3),4,'existing_vertical_stair_tower_ribs_offwhite')
 for z in [8,17,26,35,44,53]:paint(xx(-3.45,3.45)&plane(1,-14.5)&zz(z,z+5.8),0,'open_stair_tower_recess_neutral_not_glass')
 paint(xx(-57,-9)&yy(-30,-18)&zz(3,16.7)&(abs(n[:,2])<.1),2,'source_visible_low_lobby_front_turquoise_no_added_panel_frames')
 paint(xx(-58,-8)&yy(-31,-5)&zz(16.2,19.4)&(n[:,2]>-.1),1,'existing_low_lobby_parapet_rim_and_terrace_gray')
 paint(xx(-45.5,-20.5)&yy(-35.2,-30)&zz(2.4,4.2),1,'existing_entry_steps_gray')
 # Stair planes/slabs pale; protruding outer rails separately dark.
 paint(xx(61,69.8)&yy(-9,20)&zz(2.4,54),4,'observed_existing_external_stair_slabs_posts_pale')
 paint(xx(68.6,69.9)&yy(-8,19)&zz(4.8,54),6,'outer_existing_rail_region_dark_gray_not_all_stair_slab')
 for x in [16,39]:
  paint(xx(x-10.5,x+10.5)&yy(-1.5,20.5)&zz(60.1,61.2),5,'source_existing_roof_PV_pads_grayblue_grid_preserved')
  for y in [1,18]:paint(xx(x-.8,x+.8)&yy(y-.8,y+.8)&zz(57.5,60.6),1,'existing_PV_supports_gray')
 paint(hi[:,2]<=2.4001,7,'neutral_display_base_not_site_paving')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU Bajia B3 Photonics Engineering original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuub3-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official NUU album1098 photos12/13/15 visibly identify B3 photonics, not B4','scope':'Observed front wings, tower ribs, low lobby and external stair only; unknown rear/roof neutral. Open corridors/stair recesses not glass. Existing source-window and panel simplifications remain; no new lettering or equipment.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
