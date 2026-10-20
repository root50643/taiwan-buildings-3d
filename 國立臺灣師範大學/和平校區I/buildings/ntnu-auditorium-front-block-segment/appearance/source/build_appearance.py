"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='d34b42ed9d423aae22e582488c4c17c94775d21cde894f4a03a4a905c20f11bb'
PALETTE=[('neutral_unseen','#AAA79F'),('muted_brick_red','#A75B50'),('warmgray_stone','#B4ADA2'),('redbrown_window_frames','#804643'),('muted_glazing_proxy','#65797D'),('display_plinth','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_roof_back_sides_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0001)&(hi[:,2]<=b+.0001)
 paint((hi[:,1]<=-3.4999)&(n[:,1]<-.5)&zz(3,96),1,'registered_front_brick_surface')
 for x in [-57,57]:
  tower=(lo[:,0]>=x-14.5001)&(hi[:,0]<=x+14.5001)&(hi[:,1]<=-11.4999)
  paint(tower&zz(9.6,43),2,'existing_lower_tower_continuous_stone_panel_field')
  paint(tower&zz(3,9.6),2,'tower_low_stone_base')
  paint(tower&zz(74,76.1),2,'tower_front_top_cornice')
  for xx in [x-12,x+12]:paint((lo[:,0]>=xx-1.2501)&(hi[:,0]<=xx+1.2501)&(hi[:,1]<=-10.3499)&zz(3,75),2,'existing_tower_front_stone_corner_band')
  for z in [8,17,26]:paint(tower&zz(z,z+1.6),2,'existing_lower_stone_horizontal_band')
  for xx in [x-5.8,x+5.8]:
   paint((lo[:,0]>=xx-3.6501)&(hi[:,0]<=xx+3.6501)&(hi[:,1]<=-10.5999)&zz(12,38),2,'lower_paired_tower_recess_is_stone_panel_not_window')
  paint(tower&zz(62,72)&(hi[:,1]<=-11.2999),2,'existing_simplified_tower_diamond_stone_relief')
 def window(x,y,z,w,h):
  region=(lo[:,0]>=x-w/2-1.0001)&(hi[:,0]<=x+w/2+1.0001)&zz(z,z+h)&(lo[:,1]>=y-1.0501)&(hi[:,1]<=y+1.2501)
  paint(region,2,'existing_window_stone_surround')
  back=(lo[:,0]>=x-w/2-.0001)&(hi[:,0]<=x+w/2+.0001)&zz(z,z+h)&np.all(abs(t[:,:,1]-(y+1.25))<.00015,axis=1)
  paint(back,4,'existing_actual_window_back_glazing')
  inner=(lo[:,0]>=x-w/2-.0001)&(hi[:,0]<=x+w/2+.0001)&zz(z,z+h)&(lo[:,1]>=y-.2501)&(hi[:,1]<=y+1.1501)&~back
  paint(inner,3,'existing_actual_window_mullion_redbrown')
 for x in [-57,57]:
  for xx in [x-5.8,x+5.8]:window(xx,-11.6,43,7.3,19)
 for x in [-28,0,28]:
  hood=(lo[:,0]>=x-12.0001)&(hi[:,0]<=x+12.0001)&(hi[:,1]<=-3.0499)&zz(53.4,69)
  paint(hood,2,'existing_paired_tudor_hood_stone')
  for xx in [x-5.2,x+5.2]:
   window(xx,-3.5,43,7.4,10)
   back=(lo[:,0]>=xx-3.7001)&(hi[:,0]<=xx+3.7001)&zz(56,66)&np.all(abs(t[:,:,1]+2.25)<.00015,axis=1)
   paint(back,4,'existing_arch_window_back_glazing')
   paint((lo[:,0]>=xx-.5001)&(hi[:,0]<=xx+.5001)&(lo[:,1]>=-4.4001)&(hi[:,1]<=-2.9999)&zz(56,65),3,'existing_arch_mullion_redbrown')
 window(0,-3.5,81,5.3,10)
 for z in [83,87,91]:paint((hi[:,1]<=-2.9499)&zz(z,z+1.1)&(lo[:,0]>=-38.0001)&(hi[:,0]<=38.0001),2,'existing_clipped_gable_stone_band')
 for x in [-14,14]:
  rr=np.sqrt((t[:,:,0]-x)**2+(t[:,:,2]-73)**2)
  paint((rr.max(axis=1)<=2.8002)&(hi[:,1]<=-3.1499),2,'existing_round_stone_relief_no_added_carving')
 # Entrance void stays open; only real piers/lintels colored stone, never shadow black.
 for x in [-42,-14,14,42]:paint((lo[:,0]>=x-2.2001)&(hi[:,0]<=x+2.2001)&(lo[:,1]>=-26.0001)&(hi[:,1]<=-19.9999)&zz(3,32),2,'existing_open_portico_stone_pier')
 paint((lo[:,0]>=-44.0001)&(hi[:,0]<=44.0001)&(hi[:,1]<=-23.8499)&(zz(29,31.2)|zz(39,44.5)),2,'existing_portico_stone_lintel_and_peaked_caps')
 for x in [-14,14]:paint((lo[:,0]>=x-1.9001)&(hi[:,0]<=x+1.9001)&(hi[:,1]<=-24.5999)&zz(32.8,38.2),2,'existing_portico_stone_diamond')
 paint((hi[:,1]<=-25.3499)&zz(2.8,5.7),2,'existing_foyer_stone_steps')
 paint(hi[:,2]<=3.0001,5,'display_base_not_real_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTNU Auditorium Front Block original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'auditorium-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NTNU fundraising photograph and Rotary 2022 historical article approximations, not measured material swatches','scope':'Source-bounded auditorium front only; lower tower recesses stone not glass; open portico not painted shadow; roof/back neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
