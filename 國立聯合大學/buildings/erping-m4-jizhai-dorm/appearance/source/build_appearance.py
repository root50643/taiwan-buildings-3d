"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='2b60f8dd64ccb3e82ae213b5747ed141ee07fa43534bb2b7bcc664a775e2c1ef'
PALETTE=[('neutral_unknown','#AAA79F'),('light_pebble_gray_wall','#B5B8B4'),('pale_cornice_frame','#D0D4CF'),('muted_blue_gray_glazing','#6D828B'),('confirmed_PV_upper_faces','#354F72'),('silver_metal_framework_plates','#A2ACAE'),('muted_green_entry_canopy','#82A69B')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_left_back_flatroof_and_base_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.003,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(box(-27,27,-53.25,-52.8,2.3,48.3),1,'observed_short_front_pebble_wall_seams_not_shadows')
 paint(plane(0,27)&yy(-53,69)&zz(2.3,48.3),1,'observed_right_long_wall')
 for z in [19,33.2]:
  paint(plane(1,-52.45)&xx(-3.55,3.55)&zz(z,z+12.4),3,'front_stack_discrete_pane_back')
  for k in [1,2,3]:
   x=-3.55+7.1*k/4;paint(box(x-.4,x+.4,-53.775,-52.325,z-.05,z+12.45),5,'existing_front_stack_silver_mullion')
  for zz0 in [z+8.928,z+3.4,z+7.3]:paint(box(-3.6,3.6,-53.85,-52.325,zz0,zz0+.8),5,'existing_front_stack_transom')
 paint(box(-4.05,4.05,-54.55,-52.75,30.6,33.1),1,'existing_solid_center_band_not_glass')
 for y in [-43,-31,-19,-7,5,17,29,41,53,63]:
  for z in [6,20.2,34.4]:
   paint(plane(0,26.4)&yy(y-3.75,y+3.75)&zz(z,z+8.8),3,'right_discrete_pane_back_source_lower_occlusion_simplification')
   for y0 in [y-2.4,y,y+2.4]:paint(box(26.25,27.75,y0-.4,y0+.4,z-.1,z+8.9),5,'existing_right_silver_mullion')
   paint(box(26.25,27.75,y-3.8,y+3.8,z+6.3,z+7.1),5,'existing_right_silver_transom')
 paint(plane(1,-52.45)&xx(-5.15,5.15)&zz(2.7,15),5,'door_recess_neutral_metal_where_glass_boundary_unresolved')
 paint(plane(1,-52.45)&xx(-1.075,4.575)&zz(11.45,15),3,'existing_separable_upper_door_pane_only')
 for x in [-5,-1.5,5]:paint(box(x-.425,x+.425,-53.95,-52.35,2.6,15.1),5,'original_silver_door_frame')
 paint(box(-5.2,5.2,-53.95,-52.35,10.6,11.45),5,'original_door_transom')
 paint(box(-6.55,6.55,-55.7,-52.3,15.2,16.6),6,'close_photo_muted_green_canopy')
 for x,w,z,h in [(16.8,18,8,5.8),(7.8,7.4,22,2.8)]:paint(box(x-w/2,x+w/2,-54.5,-52.85,z,z+h),5,'blank_silver_plaque_no_gold_letters')
 paint(box(-29,29,-55,71,48,49.6),2,'source_pale_projecting_cornice_same_element_bounded')
 paint(box(-25,25,-47,66,54,64),5,'canopy_existing_edges_seams_underside_silver')
 for y in [-43,-22,-1,20,41,62]:
  for x in [-22,0,22]:paint(box(x-.75,x+.75,y-.75,y+.75,49.5,61),5,'existing_silver_PV_support')
 ang=np.deg2rad(2);lz=-(t[:,:,1]-9.5)*np.sin(ang)+(t[:,:,2]-58.8)*np.cos(ang)
 paint(xx(-25,25)&np.all(abs(lz-1.4)<.003,axis=1)&(n[:,2]>.9),4,'aerial_confirmed_PV_top_only_original_open_patch_preserved')
 paint(hi[:,2]<=2.4001,0,'neutral_original_ground_base')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU M4 Jizhai Dormitory original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuum4-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official M4 complete aerial and close entrance photos; uncalibrated proxies','scope':'Light gray front/right walls, silver frames/blank plaques, discrete panes, muted green canopy. Aerial verifies PV upper faces with original opening; no tank added, coarse grid not exact coverage. Unseen left/rear and flat roof neutral; cornice same-element extension bounded; unresolved lower door remains metal.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
