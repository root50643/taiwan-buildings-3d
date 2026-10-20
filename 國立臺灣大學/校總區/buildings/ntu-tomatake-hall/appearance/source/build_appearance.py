"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='2ba44177087b169f85d0245a9102eaf3f65bde3e979c19213f2fd25015f96d49'
PALETTE=[('neutral_unseen','#AAA79F'),('warm_ochre_brick','#A58B68'),('light_gray_structure','#ADB1A7'),('dark_gray_window_frames','#747B73'),('muted_glazing','#607770'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_left_rear_roof_and_round_opening_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def xx(a,b):return (lo[:,0]>=a-.00025)&(hi[:,0]<=b+.00025)
 def yy(a,b):return (lo[:,1]>=a-.00025)&(hi[:,1]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 paint((plane(1,-19)|plane(0,68))&zz(3,56.8),1,'registered_front_and_photo_right_xplus_wall_brick')
 for z in [3,15,28,41,54]:
  paint(xx(-69,69)&yy(-20.6,-18.6)&zz(z,z+2.3),2,'existing_front_gray_horizontal_band')
  paint(xx(67.1,68.9)&yy(-19,29)&zz(z,z+2.3),2,'existing_observed_right_gray_horizontal_band')
 for x in [-67,-43,-19,19,43,67]:paint(xx(x-1.15,x+1.15)&yy(-21.8,-18.4)&zz(3,57),2,'existing_continuous_front_gray_piers')
 paint(xx(-20,20)&yy(-21.4,-17.4)&zz(55,61.5)&(n[:,2]<.1),2,'existing_central_cap_gray_vertical_faces')
 paint(xx(-2.2,2.2)&plane(1,-19)&zz(56.1,60.5),0,'round_opening_back_neutral_not_clock_or_sign')
 for x,w in [(-55,16),(-31,15),(0,22),(31,15),(55,16)]:
  for z in [6,19,32,45]:
   if x==0 and z in [6,19]:continue
   paint(xx(x-w/2,x+w/2)&plane(1,-17.5)&zz(z,z+8),4,'existing_front_window_recess_back_glazing')
   for center in [x-w/4,x+w/4]:paint(xx(center-.5,center+.5)&yy(-19.6,-17.6)&zz(z,z+8),3,'existing_window_vertical_frame_dark_gray')
   paint(xx(x-w/2-.3,x+w/2+.3)&yy(-19.6,-17.6)&zz(z+4.5,z+5.5),3,'existing_window_horizontal_frame_dark_gray')
 paint(xx(-19,19)&yy(-30.5,-16.5)&zz(3,20)&(n[:,2]<.1),2,'existing_portal_arch_fascia_gray')
 for a,b in [(-19,-15),(15,19)]:paint(xx(a,b)&yy(-30.5,-16.5)&zz(3,19),1,'existing_outer_projecting_portal_piers_only_brick' )
 paint(xx(-21,21)&yy(-31.5,-16.5)&zz(19,21),2,'existing_portal_top_slab_gray')
 paint(xx(-21,21)&yy(-31.45,-29.75)&zz(20,25),2,'existing_front_portal_parapet_gray')
 # The blind shallow entrance back is not registered as actual door glazing.
 paint(xx(-11.5,11.5)&plane(1,-27.75)&zz(3.3,15.3),0,'portal_recess_back_neutral_not_invented_door')
 paint(hi[:,2]<=3.0001,5,'display_base_not_site_surface')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Tomatake Hall original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'tomatake-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NTU archive IMG5969 front and IMG5975 right oblique; capture dates not independently verified','scope':'Observed front and right x+ side ochre brick with existing gray structure, portal fascia and parapet; original window backs muted glazing. Left/rear/roof and blind entrance back neutral; no invented clock or text.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
