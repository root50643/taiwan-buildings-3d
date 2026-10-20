"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='1835376abf92fd7d961d43567fd4cf221e7478eba42176e4507cea165a7bab28'
PALETTE=[('neutral_unseen','#AAA79F'),('pale_tile','#C6CECB'),('taupe_tile','#817C77'),('dark_projecting_frame','#3F535B'),('muted_cyan_glazing','#72999E'),('silver_entry_frames','#BEC9C7'),('gray_structure','#979F9C'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_roof_and_unresolved_material_boundaries_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0003)&(hi[:,2]<=b+.0003)
 def xx(a,b):return (lo[:,0]>=a-.0003)&(hi[:,0]<=b+.0003)
 def yy(a,b):return (lo[:,1]>=a-.0003)&(hi[:,1]<=b+.0003)
 def plane(y):return np.all(abs(t[:,:,1]-y)<.0003,axis=1)
 front=hi[:,1]<=.0003
 paint(front&zz(4.8,51.4)&(n[:,2]<.01),1,'observed_front_half_pale_tile_body_and_recess_returns')
 paint(front&zz(56,58),1,'observed_front_half_pale_oval_ring')
 paint(front&zz(50.5,56),6,'observed_front_ring_supports_gray')
 paint(xx(-50.75,-33.25)&yy(-34,-10)&zz(3.55,61.05)&(n[:,1]<.01)&(n[:,2]<.01),2,'observed_front_left_taupe_tower_no_letters')
 paint(xx(-43,1)&yy(-41.5,-32.5)&zz(21.95,24.45),2,'observed_taupe_entry_fascia')
 # Existing projecting frame is a solid block, not a separately meshed perimeter.
 # Keep broad front infill pale. Only wholly supported side/perimeter triangles get dark.
 frame=xx(15.75,36.25)&yy(-32.75,-24.25)&zz(23.25,42.95)
 paint(frame,1,'projecting_frame_broad_central_infill_pale_not_all_black')
 edge=(hi[:,0]<=17.75)|(lo[:,0]>=34.25)|(hi[:,2]<=24.75)|(lo[:,2]>=41.45)
 paint(frame&((abs(n[:,0])>.99)|(abs(n[:,2])>.99)|edge),3,'existing_projecting_outer_sides_and_fully_contained_edge_triangles_dark')
 for x in [21.5,26,30.5]:
  for z in [28.5,36.8]:paint(xx(x-1.85,x+1.85)&zz(z-3.25,z+3.25)&plane(-32),4,'projecting_feature_window_recess_back_only')
 for z in np.arange(9,56,5):paint(xx(-48.9,-47.1)&zz(z-2.15,z+2.15)&plane(-33.25),4,'tower_existing_window_back_not_whole_strip')
 for x in np.arange(-39,-3,4):paint(xx(x-1.6,x+1.6)&zz(5.45,20.95)&plane(-36.25),4,'entry_original_glazing_back')
 paint(xx(-42,-2)&yy(-37.001,-36.999)&zz(4.7,22.7),5,'entry_front_integral_frame_surface_silver')
 for xs,z in [([-28,-24,-20,-16,-12],36.5),([-9,-5,-1,3,7],36.5),([-28,-24,-20,-16,-12],28)]:
  for x in xs:
   y=-31*np.sqrt(1-(x/62)**2)
   paint(xx(x-1.65,x+1.65)&zz(z-1.25,z+1.25)&plane(y+.9),4,'existing_front_horizontal_window_back_no_curtain_texture')
 for x,z,h in [(12,35,6),(18,27,5),(7,23,5),(-2,25,5)]:
  y=-31*np.sqrt(1-(x/62)**2);paint(xx(x-.7,x+.7)&zz(z-h/2,z+h/2)&plane(y+.8),4,'existing_narrow_front_window_back')
 for x in [39,42,45]:
  y=-31*np.sqrt(1-(x/62)**2)
  for z in [26,30,34,38]:paint(xx(x-1.125,x+1.125)&zz(z-1.6,z+1.6)&plane(y+.8),4,'existing_right_curtain_panel_recess_back')
 for count,zs,w in [(100,[(47.9,2.8),(21,3.4),(29,3.4),(37,3.4)],2.7),(74,[(10.6,7.4)],3.7)]:
  for a in np.linspace(0,2*np.pi,count,endpoint=False):
   if np.sin(a)>=-.05:continue
   normal=np.array([np.cos(a)/62,np.sin(a)/31]);normal/=np.linalg.norm(normal);tangent=np.array([-normal[1],normal[0]]);d=t[:,:,:2]-np.array([62*np.cos(a),31*np.sin(a)]);u=d@normal;v=d@tangent
   width=min(w,.70*2*np.pi/100*np.sqrt((62*np.sin(a))**2+(31*np.cos(a))**2))
   for z,h in zs:paint(np.all(abs(u+.8)<.0004,axis=1)&np.all(abs(v)<=width/2+.0004,axis=1)&zz(z-h/2,z+h/2),4,'registered_front_half_radial_window_recess_back_only')
 paint(xx(-43.5,45.5)&yy(-42,-34)&zz(14.55,16.05),0,'thin_lower_canopy_not_confused_with_taupe_upper_fascia')
 paint(front&zz(3,5)&(n[:,2]>.5),6,'existing_front_terrace_and_compressed_steps_gray')
 paint(hi[:,2]<=3.0001,7,'neutral_display_base_not_actual_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU Guoding Library original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuulib-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official NUU Guoding Library photos5/7/10 EXIF2025; uncalibrated proxies','scope':'Front half pale tile, taupe tower and upper entry fascia, dark projecting outer sides not central infill, existing glazing backs. Unsplit front perimeter triangles conservatively pale. Rear and roof neutral; no absent PV, text or curtains invented.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
