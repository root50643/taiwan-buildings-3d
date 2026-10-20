"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='5bc1851c2b6cd1a8128a371ccd3005952f02c7f67d47b415094462e7bac41fe2'
PALETTE=[('neutral_unseen','#AAA79F'),('brick_piers_and_spandrels','#AF7157'),('cream_arcade_and_pediment','#D0CEBD'),('gray_stone_columns_and_balustrades','#A5AAA1'),('muted_redbrown_pediment_recess','#7D655C'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_short_ends_roof_and_unregistered_faces_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 for yy in [-11.5,17.5]:paint(np.all(abs(t[:,:,1]-yy)<.00025,axis=1)&zz(2.8,30.2),1,'source_registered_long_facade_brick_field')
 # Both long elevations are photographed. Recesses represent open arcades, not glass.
 for side,yy,back,xs in [('front',-11.5,-10.5,[-63,-54,-45,-36,-27,27,36,45,54,63]),('rear',17.5,16.5,[-63,-54,-45,-36,-27,-18,-9,0,9,18,27,36,45,54,63])]:
  for x in xs:
   scope=(lo[:,0]>=x-3.55025)&(hi[:,0]<=x+3.55025)&(lo[:,1]>=min(yy,back)-.00025)&(hi[:,1]<=max(yy,back)+.00025)
   for z,h in [(5,10.7),(19,10.8)]:paint(scope&zz(z,z+h),2,'existing_'+side+'_open_arcade_recess_cream_not_glass')
   rail_y=-12 if side=='front' else 18
   paint((lo[:,0]>=x-3.90025)&(hi[:,0]<=x+3.90025)&(lo[:,1]>=rail_y-.65025)&(hi[:,1]<=rail_y+.65025)&zz(17.4,19.5),3,'existing_'+side+'_solid_balustrade_proxy_gray')
 for x in [-12,0,12]:
  scope=(lo[:,0]>=x-4.25025)&(hi[:,0]<=x+4.25025)&(lo[:,1]>=-11.50025)&(hi[:,1]<=-10.49975)
  for z,h in [(5,10.7),(19,10.8)]:paint(scope&zz(z,z+h),2,'existing_arcade_behind_portico_cream_not_glass')
 paint((lo[:,0]>=-19.00025)&(hi[:,0]<=19.00025)&(lo[:,1]>=-12.65025)&(hi[:,1]<=-11.34975)&zz(17.4,19.5),3,'existing_front_central_solid_balustrade_proxy_gray')
 for x in [-17,-10.2,-3.4,3.4,10.2,17]:
  paint((lo[:,0]>=x-1.55025)&(hi[:,0]<=x+1.55025)&(lo[:,1]>=-18.55025)&(hi[:,1]<=-15.44975)&zz(5.8,28.9),3,'six_existing_stone_columns_gray')
  paint((lo[:,0]>=x-2.05025)&(hi[:,0]<=x+2.05025)&(lo[:,1]>=-19.05025)&(hi[:,1]<=-14.94975)&(zz(3.9,6.2)|zz(28.1,29.5)),3,'existing_column_bases_and_capitals_gray')
 paint((lo[:,0]>=-20.00025)&(hi[:,0]<=20.00025)&(lo[:,1]>=-20.35025)&(hi[:,1]<=-7.64975)&zz(29.2,31.4),3,'existing_portico_entablature_gray')
 paint(np.all(abs(t[:,:,1]+20.35)<.00025,axis=1)&zz(31.3,40.3),2,'source_front_pediment_plaster_cream_no_invented_border')
 paint((lo[:,0]>=-2.75025)&(hi[:,0]<=2.75025)&np.all(abs(t[:,:,1]+19.55)<.00025,axis=1)&zz(32.3,37.9),4,'existing_pediment_window_recess_muted_redbrown')
 paint((lo[:,0]>=-19.50025)&(hi[:,0]<=19.50025)&(lo[:,1]>=-21.50025)&(hi[:,1]<=-7.99975)&zz(2.8,4.1),3,'existing_portico_steps_and_plinth_gray')
 paint((np.all(abs(t[:,:,1]+12.5)<.00025,axis=1)|np.all(abs(t[:,:,1]-18.5)<.00025,axis=1))&zz(29.9,32.3),3,'existing_long_elevation_cornice_vertical_face_gray')
 paint((lo[:,0]>=-5.00025)&(hi[:,0]<=5.00025)&(lo[:,1]>=16.99975)&(hi[:,1]<=19.00025)&zz(3.5,18),3,'existing_modest_rear_entry_frame_gray')
 paint((lo[:,0]>=-5.50025)&(hi[:,0]<=5.50025)&(lo[:,1]>=17.19975)&(hi[:,1]<=20.20025)&zz(18,19.2),3,'existing_rear_entry_lintel_gray')
 paint(np.all(abs(t[:,:,1]-18.1)<.00025,axis=1)&(lo[:,0]>=-3.50025)&(hi[:,0]<=3.50025)&zz(5,15),2,'rear_entry_recess_neutral_cream_not_dark_glass')
 paint(hi[:,2]<=2.8001,5,'display_base_not_landscape')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU Dacheng Hall original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nckudacheng-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NCKU 2019 conference front photograph and rear photo posted 2025; exact capture dates unverified','scope':'Registered two long elevations: open arcade recesses cream, never glass; six stone columns, solid balustrade proxies; roof and short ends neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
