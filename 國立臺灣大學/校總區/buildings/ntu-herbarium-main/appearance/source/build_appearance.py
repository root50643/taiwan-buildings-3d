"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='2cff1b6eb73f9cfb419d7298460adef5379b08bcc1ab73ef1a481b16546b7e17'
PALETTE=[('neutral_unresolved','#AAA79F'),('muted_ochre_brown_brick','#A38B68'),('gray_stone_frames_and_bands','#92978D'),('dark_window_frames','#625F50'),('lower_window_glazing','#6A8075'),('warm_timber_entry','#AC7D45'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unresolved_tall_window_spandrel_glass_boundary_or_unseen_ends_roof_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def xx(a,b):return (lo[:,0]>=a-.00025)&(hi[:,0]<=b+.00025)
 def yy(a,b):return (lo[:,1]>=a-.00025)&(hi[:,1]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 paint((plane(1,-19)|plane(1,23))&zz(3,58.8),1,'registered_street_and_garden_long_wall_brick')
 for y in [-19,23]:
  front=y<0;back=y+1.5 if front else y-1.5
  for x in [-57.75+i*10.5 for i in range(12)]:
   if y==23 and abs(x+26)<16:continue
   # Raised arch surround and returns; all tall backing stays neutral because
   # source triangles cross z24..53 without a separable stone/glass boundary.
   paint(xx(x-4.35,x+4.35)&yy(y-.85,y+.85)&zz(24,56.85)&~plane(1,y),2,'original_tall_arch_stone_surround_only')
   paint(xx(x-3.5,x+3.5)&plane(1,back)&zz(24,56),0,'entire_tall_back_neutral_no_false_diagonal_spandrel_glass_split')
   yc=y+.3 if front else y-.3
   for z in [34,44]:paint(xx(x-3.75,x+3.75)&yy(yc-1,yc+1)&zz(z,z+.9),3,'existing_tall_window_horizontal_frame_dark')
   paint(xx(x-.45,x+.45)&yy(yc-1,yc+1)&zz(24,51),3,'existing_tall_window_vertical_frame_dark_original_geometry')
   if not(front and abs(x)<12):
    paint(xx(x-3.25,x+3.25)&plane(1,back)&zz(7,20),4,'lower_rectangle_existing_back_glazing')
    paint(xx(x-.5,x+.5)&yy(yc-1,yc+1)&zz(7,20),3,'existing_lower_window_vertical_frame')
    paint(xx(x-3.5,x+3.5)&yy(yc-1,yc+1)&zz(15,15.9),3,'existing_lower_window_horizontal_frame')
 for y in [-19.3,23.3]:
  for z in [3,21.5,57]:paint(xx(-68.5,68.5)&yy(y-.75,y+.75)&zz(z,z+1.5),2,'existing_long_stone_band_no_fake_full_plinth')
 paint(xx(-12.5,12.5)&yy(-28.5,-17.5)&zz(24,25.5),2,'original_concrete_entry_canopy_gray')
 paint(xx(-9.5,9.5)&plane(1,-17.5)&zz(3.5,24.5),5,'existing_door_back_timber_proxy_no_added_glass_panels')
 for x in [-6,0,6]:paint(xx(x-.5,x+.5)&yy(-19.5,-17.5)&zz(3,24.5),5,'existing_door_mullions_timber')
 paint(xx(-38.5,-13.5)&plane(1,28)&zz(3,60.5),1,'garden_projected_bay_front_brick')
 paint(xx(-30.85,-21.15)&yy(27.15,28.85)&zz(30,56.85)&~plane(1,28),2,'garden_upper_existing_arch_trim_gray')
 for z in [39,47]:paint(xx(-30.25,-21.75)&yy(26.7,28.7)&zz(z,z+.9),3,'garden_projected_bay_existing_window_crossbars')
 paint(xx(-33,-19)&plane(1,26.5)&zz(4,26),0,'garden_door_recess_neutral_not_glass')
 paint(hi[:,2]<=3.0001,6,'display_base_not_site_surface')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Herbarium Main Building original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'herbarium-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated Open House, Taipei City and original photographer street/garden photos; dates not independently verified','scope':'Observed long walls ochre brick, existing stone arch trims/bands, dark frame members and timber entry. All tall window backs neutral because original triangles cross solid stone spandrels and glazing; not a restored material boundary. Lower window backs only glazing. Ends and roof neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
