"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='de53f0275d25d018607d01b13a2a9a77f12fde0171d9d7d496da94021f505b88'
PALETTE=[('neutral_unknown','#AAA79F'),('gray_aggregate_wall','#AFB1AB'),('warm_pale_vertical_piers','#D0CCBD'),('muted_gray_blue_glazing','#6B8088'),('silver_roof_framework','#A7B0B3'),('confirmed_PV_tops','#354F73'),('turquoise_lift_panes','#609AA7'),('muted_green_lift_cap','#7BA394')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_plain_rear_farend_base_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.003,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,13)&xx(-20,58)&zz(6,73),1,'observed_courtyard_front_gray_wall')
 paint(plane(0,-34)&yy(-58,42)&zz(6,73),1,'observed_plain_inner_wing_gray_wall')
 paint(plane(0,-66)&yy(-58,42)&zz(6,73),1,'observed_outer_left_long_wall')
 paint(box(-36,-20,-3.5,15.5,6,73),1,'observed_circulation_connector_gray_wall')
 for row in range(5):
  z=10+row*12.2
  for x in np.linspace(-10,51,9):
   for z0,h in [(z,7.3),(z+8.2,1.7)]:paint(plane(1,13.8)&xx(x-2.5,x+2.5)&zz(z0,z0+h),3,'courtyard_discrete_window_back')
   paint(box(x-2.65,x+2.65,11.7,13.9,z+6,z+6.85),2,'existing_courtyard_pale_transom')
  for y in np.linspace(-46,30,10):
   if y < -40:continue
   for z0,h in [(z,7.3),(z+8.2,1.7)]:paint(plane(0,-65)&yy(y-2.5,y+2.5)&zz(z0,z0+h),3,'source_outer_left_discrete_window_back')
  paint(plane(1,-2.5)&xx(-34,-22)&zz(z+3,z+7.8),3,'connector_original_discrete_window_back')
 for x in np.linspace(-14,55,10):paint(box(x-.65,x+.65,11.1,13.5,6,70),2,'source_pale_courtyard_vertical_pier')
 for y in np.linspace(-50,34,11):paint(box(-67.6,-65.2,y-.65,y+.65,6,70),2,'source_pale_outer_left_vertical_pier')
 paint(box(-71,-63,-57.5,-40.5,17.5,72.3),1,'visible_outside_corner_projecting_bay_gray')
 for z in [22,34.2,46.4,58.6]:paint(plane(0,-70)&yy(-55.5,-42.5)&zz(z,z+5.3),3,'outside_corner_bay_window_back')
 paint(plane(1,-2.7)&xx(-34,-22)&zz(7.2,17.2),3,'entry_door_glazing_proxy')
 paint(box(-37,53,14,42,74,78.9)|box(-64,-36,-52,12,74,78.9),4,'original_PV_canopy_support_and_seams_silver')
 paint(plane(2,78.9)&(box(-37,53,14,42,78.9,78.9)|box(-64,-36,-52,12,78.9,78.9)),5,'both_roof_array_tops_confirmed_in_aerial')
 paint(box(-35,-23,23.5,36.5,73,89),4,'lift_tower_existing_frame_silver')
 for z in [75,80,85]:
  paint(plane(1,24.5)&xx(-33.75,-24.25)&zz(z,z+3.2),6,'observed_turquoise_lift_front_pane')
  paint(plane(0,-34)&yy(25,35)&zz(z,z+3.2),6,'observed_turquoise_lift_side_pane')
 paint(box(-35.4,-22.6,23.1,36.9,89,90.2),7,'observed_muted_green_lift_cap')
 paint(hi[:,2]<=2.4001,0,'neutral_original_base_not_lawn')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU M7 Shuangdian Dormitory original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuum7-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official M7 complete entrance and aerial photos; uncalibrated proxies','scope':'Gray courtyard and outer-left walls, pale original piers and discrete window backs; both roof arrays confirmed PV top only. Silver supports and turquoise lift panes/green cap; far end and unseen rear remain neutral. Coarse panels and rhythm retained, no added equipment.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
