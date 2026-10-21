"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='1c1565c68a7ec17f8ba6421fff0154e74dc830c510592781f668c674cec88b7f'
PALETTE=[('neutral_roofs_mixed_fascia_cutoff_and_unknown','#AAA79F'),('offwhite_walls_frames_and_steel','#D6D7CD'),('gray_exposed_octagonal_columns','#9B9C8E'),('charcoal_plinth','#424943'),('muted_rust_museum_board','#965E45'),('muted_window_proxy','#63736D')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_roof_mixed_fascia_cutoff_ground_door_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.003,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(((plane(1,-9)|plane(1,21))&xx(-60,60)|plane(0,60)&yy(-9,21))&zz(4.5,27),1,'source_registered_white_wall_planes_only_not_roofs_or_mixed_fascia')
 for x in [-58,-38,-18,2,22,42,59]:paint(box(x-1.7,x+1.7,19.6,22.4,4.3,28.7),1,'source_outer_wall_white_pilaster_component')
 for y in [-9,21]:paint(box(58,62,y-2,y+2,4.5,30.2),1,'source_south_white_corner_pier_above_black_foot')
 for x in [-49,-29,-9,31,50]:
  paint(box(x-.625,x+.625,-9.75,-7.05,8.5,22.3),1,'source_white_arcade_window_vertical_muntin')
  for z in [12.4,17,20.5]:paint(box(x-5.9,x+5.9,-9.75,-7.05,z,z+1),1,'source_white_arcade_window_horizontal_muntin')
  paint(box(x-6.4,x+6.4,-10.55,-7.45,7.3,8.5),1,'source_white_arcade_sill')
  paint(plane(1,-6.95)&xx(x-5.5,x+5.5)&zz(8.5,22.3)&(norm[:,1]<0),5,'source_arcade_window_back_glass_curtain_proxy')
 for x in [-48,-28,-8,12,32,50]:
  paint(box(x-.625,x+.625,19.1,21.9,8.5,22.5),1,'source_outer_white_window_vertical_muntin')
  for z in [12.4,17,20.4]:paint(box(x-6,x+6,19.1,21.9,z,z+1),1,'source_outer_white_window_horizontal_muntin')
  paint(box(x-6.5,x+6.5,19.4,22.6,7.2,8.5),1,'source_outer_white_sill')
  paint(plane(1,19.05)&xx(x-5.6,x+5.6)&zz(8.5,22.5)&(norm[:,1]>0),5,'source_outer_window_back_proxy')
 paint(box(58,60.8,5.375,6.625,8.5,22.5),1,'source_south_window_white_vertical_muntin')
 for z in [12.4,17,20.4]:paint(box(58,60.8,0,12,z,z+1),1,'source_south_window_white_horizontal_muntin')
 paint(box(58.4,61.6,-.5,12.5,7.2,8.5),1,'source_south_window_white_sill')
 paint(plane(0,57.9)&yy(.4,11.6)&zz(8.5,22.5)&(norm[:,0]>0),5,'source_south_window_back_proxy')
 # Actual original octagon side planes; not bounding-box recolor near white canopy.
 for x in [-59,-39,-19,1,21,41,61]:
  for r,z,h in [(1.65,3.6,20.8),(2.15,3.4,1.5),(2.2,22.9,1.6)]:
   for angle in np.arange(8)*np.pi/4+np.pi/4:
    n=np.array([np.cos(angle),np.sin(angle)]);d=(t[:,:,:2]-np.array([x,-21.3]))@n
    paint(np.all(abs(d-r*np.cos(np.pi/8))<.003,axis=1)&box(x-r,x+r,-21.3-r,-21.3+r,z,z+h),2,'restored_photo_gray_octagonal_column_exact_side_planes_no_mottled_texture')
 for x in [61,69]:
  for y in [-22,22]:paint(box(x-.9,x+.9,y-.9,y+.9,3,25.8),1,'source_white_steel_canopy_post_distinct_from_gray_columns')
 for y in [-22,22]:paint(box(60,70,y-1,y+1,24.3,26.2),1,'source_white_steel_canopy_crossbeam')
 for x in [61,69]:
  edge_low=27.2-(3/23)*abs(t[:,:,1]);inside=np.all((t[:,:,2]>=edge_low-.003)&(t[:,:,2]<=edge_low+1.9+.003),axis=1)
  paint(box(x-1,x+1,-23,23,24.2,29.1)&inside,1,'source_white_steel_canopy_gable_beams_exact_profile_bounds')
 paint(box(60,70,-.9,.9,27.3,29),1,'source_white_steel_canopy_ridge')
 paint(((plane(1,-9.5)|plane(1,21.5))&xx(-60.5,60.5)|plane(0,60.5)&yy(-9.5,21.5))&zz(3,4.5),3,'source_independent_black_plinth_vertical_facets_only')
 paint(box(61.5,62.7,-10.75,-7.25,11.2,22.4),4,'source_rust_museum_board_existing_relief_no_letters')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTUT Yida Restored Southern Section Bounded Appearance original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntutyida-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official restored Yida wide photograph and official review PDF p97 undated top close photograph; PDF2026creation and2024-11-22opening are not its capture date. White restored walls/steel, exposedgray octagonal columns, independent black plinth and rust museum board','scope':'Original southern six-bay section only. Source-supported wall/window planes and separate components, no letter/texture additions. Roof tops, mixedweatheredfascia, northcutoff, ground and arched doorway remain neutral. Older yellow-column historical photos explicitly not used for restored palette.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
