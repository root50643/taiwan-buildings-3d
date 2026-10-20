"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='a091c3fc636aa734e3a8e780e2444df3f755bf19ffaf4c3b0af8aeb1d37e2bf8'
PALETTE=[('neutral_unseen','#AAA79F'),('terracotta_facade','#B87966'),('ivory_structure','#C4C4B8'),('silver_frames_equipment','#ACB4B3'),('muted_bluegray_glazing','#647985'),('mauve_entry_fascia','#B4A3A4'),('redbrown_stair_tile','#976858'),('gray_metal_canopy','#969E9E')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_rear_or_unsplit_cross_color_surface_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0004)&(hi[:,2]<=b+.0004)
 def xx(a,b):return (lo[:,0]>=a-.0004)&(hi[:,0]<=b+.0004)
 def yy(a,b):return (lo[:,1]>=a-.0004)&(hi[:,1]<=b+.0004)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.0004,axis=1)
 def box(x,y,z,w,d,h):return xx(x,x+w)&yy(y,y+d)&zz(z,z+h)
 wall=(plane(1,-43)&xx(-70,70))|(plane(0,70)&yy(-43,49))
 paint(wall&zz(23.7,89.7),1,'bounded_middle_front_right_terracotta_only')
 paint(wall&(zz(3,16.6)|zz(89.7,117)),2,'bounded_lower_and_upper_two_storeys_ivory')
 for i in range(14):paint(box(-68+i*10.35,-43.65,3,1.35,.8,113),2,'original_continuous_front_pier_ivory')
 for i in range(11):paint(box(69.65,-41+i*8.5,3,.8,1.25,113),2,'original_continuous_right_pier_ivory')
 for floor in range(8):
  z=10+floor*13.7
  for bay in range(13):
   x=-66.2+bay*10.35
   if floor==0 and bay in (5,6,7):continue
   paint(box(x,-43,z,8.5,.9,6.6),3,'existing_front_reveal_silver_proxy')
   paint(box(x,-43,z,8.5,.9,6.6)&plane(1,-42.1),4,'front_discrete_window_back_only')
   paint(box(x+4,-43.6,z,.65,1,6.6),3,'original_bonded_mullion_silver')
   paint(box(x,-43.7,z,8.5,1.1,.7),3,'original_sill_silver')
   paint(box(x+.5,-44,z+.5,2.5,1.35,2.4),3,'original_simplified_AC_mass_not_glass')
  for bay in range(10):
   y=-39+bay*8.5
   paint(box(69.1,y,z,.9,6.8,6.6),3,'existing_right_reveal_silver_proxy')
   paint(box(69.1,y,z,.9,6.8,6.6)&plane(0,69.1),4,'right_discrete_window_back_only')
   paint(box(69,y+3,z,1,.65,6.6),3,'original_right_bonded_mullion_silver')
   paint(box(69,y,z,1.1,6.8,.7),3,'original_right_sill_silver')
   paint(box(69.05,y+.45,z+.5,1.35,2.2,2.3),3,'original_right_simplified_AC_mass')
 for z in [89.7,103.4]:
  paint(box(-70,-43.8,z,140,1,2),2,'original_upper_storey_relief_ivory')
  paint(box(69.8,-43,z,1,92,2),2,'original_right_upper_storey_relief_ivory')
 paint(box(-25,-48,7,3,6,29)|box(22,-48,7,3,6,29)|box(-16,-47,18,32,4.5,2.4),2,'observed_entry_supports_and_lower_lintel_ivory')
 paint(box(-26,-48,33,52,6,5.6),5,'observed_blank_fascia_mauve_tile_no_letters')
 for i in range(9):
  paint(box(-18,-61+i*1.7,3,36,18-i*1.7,.5*(i+1))&(n[:,2]>.9),6,'existing_stair_tread_redbrown_tile')
  for x in [-21,18]:paint(box(x,-61+i*1.7,3,3,1.9,.5*(i+1)+1),2,'existing_step_cheeks_ivory')
 paint(box(-68,-41,116.5,136,88,3.4)&(n[:,2]>.1),7,'original_solid_backed_roof_metal_canopy_not_PV')
 paint(hi[:,2]<=3.0001,0,'neutral_display_base_not_site_paving')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU Erping C1 Lide original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuuc1-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official C1 2025 photos1/4 plus undated archive upper-story registration; uncalibrated proxies','scope':'Only bounded middle terracotta faces, pale piers, individual window backs, existing equipment/mullions, mauve blank fascia and redbrown treads. Gray metal canopy is NOT identified as photovoltaic. Unsplittable mixed boundaries and unseen rear neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
