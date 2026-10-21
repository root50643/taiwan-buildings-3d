"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='55416fcc20a3eccf1a7fabc89bf98536ee480b3bbe29811909240edab37b857d'
PALETTE=[('neutral_scope_cut_unseen','#AAA79F'),('warm_lightgray_tile_proxy','#C2BCAF'),('muted_dark_glazing_proxy','#626F70'),('silvery_window_frames','#A6ACA7'),('gray_entry_steps','#8F9692')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'rear_scope_cut_and_unknown_roof_side_surfaces_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.004)&(hi[:,2]<=b+.004)
 def xx(a,b):return (lo[:,0]>=a-.004)&(hi[:,0]<=b+.004)
 def yy(a,b):return (lo[:,1]>=a-.004)&(hi[:,1]<=b+.004)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-18)&xx(-69,65)&zz(3,96),1,'day_tile_palette_bounded_to_registered_plaza_front_no_night_yellow')
 paint(plane(1,-19)&xx(-70,64)&zz(95.3,97),1,'source_front_cap_vertical_tile_edge_not_roof_top')
 paint(plane(1,-10)&xx(61.5,70.5)&zz(3,97),1,'source_registered_service_block_front_only')
 for x,y in [(-45,-12),(-21,-12),(24,-12),(48,-12),(-43,7),(46,7)]:
  rad=np.sqrt((t[:,:,0]-x)**2+(t[:,:,1]-y)**2)
  paint(np.all(rad<=2.151,axis=1)&zz(3,35.2),1,'day_source_round_tiled_columns_whole_existing_component')
 # Column hall soffit visibly cream; source thickness and tile seams not re-created.
 paint(plane(2,34.6)&xx(-69,63)&yy(-18,24),1,'day_source_colonnade_soffit_same_tile_system_bounded')
 for z in [38.6,49.8,61.,72.2]:
  paint(box(-68,62,-20.6,-17.4,z+7.1,z+8.55),1,'registered_existing_horizontal_facade_band_same_tile_palette')
  paint(plane(1,-16.25)&xx(-66,60)&zz(z,z+6.7),2,'night_geometry_only_four_window_ribbon_backs_day_muted_glass_proxy')
  for x in range(-64,62,6):paint(box(x-.5,x+.5,-19.65,-15.95,z-.1,z+6.9),3,'existing_front_ribbon_window_frames_silver_proxy')
 # Curved glazed lobby skeleton and discrete original cut backs.
 dx=t[:,:,0]+1;dy=t[:,:,1]-21;rr=np.sqrt(dx*dx+dy*dy);ang=(np.degrees(np.arctan2(dy,dx))+360)%360
 paint(np.all((rr>=26.94)&(rr<=27.004)&(ang>=197.9)&(ang<=344.1),axis=1)&zz(3,34.8),1,'source_day_curved_lobby_tiled_skeleton_not_whole_glass_cylinder')
 for a in range(198,344,12):
  r=np.deg2rad(a);u=dx*np.cos(r)+dy*np.sin(r);v=-dx*np.sin(r)+dy*np.cos(r)
  paint(np.all(abs(u-25.65)<.004,axis=1)&np.all(abs(v)<=2.104,axis=1)&zz(6.4,29.9),2,'source_day_discrete_curved_lobby_glazing_recess')
 paint(plane(1,-4)&xx(-7,7)&zz(3,12),2,'existing_front_middle_door_back_glazing_proxy')
 paint(box(4,44,-28,-16,25,36.3)&(norm[:,2]<.0001),1,'registered_projecting_entry_bay_tile_edges_soffit_not_top')
 paint(plane(1,-26.15)&xx(7.5,40.5)&zz(28,33.8),2,'registered_projecting_entry_window_back')
 for x in [11,19,27,35]:paint(box(x-.55,x+.55,-28.5,-25.5,28,33.8),3,'existing_projecting_entry_window_frames')
 for x in [5.4,42.6]:paint(box(x-1.4,x+1.4,-29,-19,3,25.2),1,'same_registered_entry_support_component_tile_proxy')
 paint(box(2.5,45.5,-37.5,-20.5,23.4,25.3)&(norm[:,2]<.0001),1,'visible_entry_canopy_edge_soffit_not_unseen_top')
 for i in range(6):paint(box(-15.5,63.5,-40.175+i*2,-37.825+i*2,3,2.8+.65*(i+1)),4,'registered_simplified_gray_approach_steps')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NYCU Haoran Plaza Facade Segment Appearance original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nycuhaoran-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NYCU Museum daytime colonnade and nighttime facade, camera Original 2020-06-22; day-derived tile/glass proxies, no yellow night light baked in','scope':'Plaza facade segment only. Registered tile front and columns, four window ribbons and separate curved lobby/entry recess backs. Top gallery is open not glazing. Rear scope-cut, roof tops and unsupported sidewall neutral; bounded same-system material extension explicit, not complete building.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
