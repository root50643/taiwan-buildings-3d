"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='1caa581a06c6f94604afb535df04d23742230a8b75914ff81b8f00daefbd2fb1'
PALETTE=[('neutral_unseen','#AAA79F'),('gray_concrete','#A4ABAA'),('pale_louvers','#CDD0C8'),('sage_blank_sign','#9DB7A5'),('muted_green_glazing','#668F87'),('blue_PV','#5A738F'),('silver_frames','#BAC6BE'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_roof_ends_and_unresolved_upper_channel_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def xx(a,b):return (lo[:,0]>=a-.00025)&(hi[:,0]<=b+.00025)
 def local(x):
  ang=np.arctan(20*x/4900);d=t[:,:,:2]-np.array([x,-8+10*(x/70)**2]);return d@np.array([np.cos(ang),np.sin(ang)]),d@np.array([-np.sin(ang),np.cos(ang)])
 def boxmask(x,off,z,w,d,h):
  u,v=local(x);a=np.arctan(20*x/4900);u=u-off*np.sin(a);v=v-off*np.cos(a);return np.all(abs(u)<=w/2+.0003,axis=1)&np.all(abs(v)<=d/2+.0003,axis=1)&zz(z,z+h)
 def localplane(x,v0,w,z,h):
  u,v=local(x);return np.all(abs(u)<=w/2+.0003,axis=1)&np.all(abs(v-v0)<.0003,axis=1)&zz(z,z+h)
 off=t[:,:,1]-(-8+10*(t[:,:,0]/70)**2)
 paint(np.all((off>=-.002)&(off<=.002),axis=1)&zz(2.4,35.1)&(n[:,1]<-.1),1,'observed_curved_front_concrete_surface_only')
 # Upper channels mix yellow wall and window zones in photos, but original has continuous unsplit backs: neutral, not glass/yellow blanket.
 for x in np.arange(-52,50,7.5):paint(boxmask(x,.4,21.6,1.8,4,13.8),1,'existing_front_vertical_structure_gray')
 for x in [-53,-34,-12,24,39]:
  for z in [16,22.2,28.5]:paint(boxmask(x,.4,z,1.8,3.8,4.5),2,'existing_louver_columns_pale_preserve_grooves')
 for z in [9,15.4]:
  for x in np.arange(-65,49,5.4):
   if not(z==9 and -39<x<-13):paint(localplane(x,.9,4.3,z,2.6),4,'original_lower_ribbon_window_recess_back')
 for x,z,h,w in [(-42,3.4,31,5.8),(8,4,24.2,8.1)]:
  paint(localplane(x,1.1-.4*np.cos(np.arctan(20*x/4900)),w+.1,z,h),4,'source_distinct_tall_glazed_bay_back')
  for dx in [-w/2,0,w/2]:paint(boxmask(x+dx,.15,z,.75,1.5,h),6,'existing_tall_glazing_integral_mullions')
  for z0 in np.arange(z+2.9,z+h,3.7):paint(boxmask(x,.1,z0,w,1.5,.7),6,'existing_tall_glazing_cross_bars')
 for z in [3.6,9.1]:
  paint(xx(8,37)&zz(z,z+4.8)&np.all(abs(off-.9)<.002,axis=1),4,'source_lower_front_right_glazing_ribbon_back')
  for x in np.arange(8,39,4):paint(boxmask(x,.2,z,.7,1.3,4.8),6,'existing_lower_glazing_vertical_mullions')
  paint(xx(8,37)&zz(z+2.3,z+2.95)&np.all((off>=-.352)&(off<=.752),axis=1),6,'existing_lower_glazing_curved_crossbar')
 paint(boxmask(-26,-.55,8.7,23,1.6,4.1),3,'source_sage_sign_backing_blank_no_gold_letters')
 paint(boxmask(53,-1.1,2.4,9.4,7.7,36.3)&(n[:,1]<.1),1,'observed_front_stair_tower_concrete_not_glass')
 paint(boxmask(53,-1.2,38.2,10.5,8.3,.9),1,'observed_stair_tower_cap_gray')
 for z in [4,11,18,25,32]:paint(localplane(53,2-4.5*np.cos(np.arctan(20*53/4900)),7,z,4.9),0,'open_stair_recess_neutral_not_glass')
 for k in range(10):paint(boxmask(-66+k*.67,1.5,23+k*.53,1,7,1.1),1,'existing_left_stair_flight_gray')
 # Existing front roof edge only; rear rim and service headhouse remain unregistered neutral.
 paint(xx(-70,70)&zz(36,37.1)&np.all((off>=-.302)&(off<=.702),axis=1),1,'observed_front_roof_parapet_gray')
 for x1,x2,o,d in [(-53,2,.7,7.2),(12,33,.8,7.2),(-2,23,10,7.1),(61,69,10,7)]:
  paint(xx(x1,x2)&zz(36,36.9)&np.all((off>=o-.002)&(off<=o+d+.002),axis=1),5,'existing_PV_slab_surface_only_grid_preserved')
 paint(xx(-7,28)&zz(2.4,3.9)&np.all(off<-2,axis=1),1,'existing_compressed_entry_steps_gray')
 paint(hi[:,2]<=2.4001,7,'neutral_display_base_not_site_road')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU Bajia B2 Electronics Engineering original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuub2-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official NUU B2 photo22 EXIF2025; uncalibrated source proxy','scope':'Curved observed front only. Existing tall/lower glazing backs, pale louver relief, sage blank sign and PV pads. Continuous upper channel backs neutral because unsplit wall/window mixture, not all glass or invented yellow segmentation. Rear/ends neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
