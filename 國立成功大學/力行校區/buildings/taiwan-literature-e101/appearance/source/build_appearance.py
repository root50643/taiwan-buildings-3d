"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='72d81558765b571d362bdf0c1d0b22add82966737bbc3a9314be43966dded8e6'
PALETTE=[('neutral_unseen','#AAA79F'),('warm_red_brown_brick','#AA7054'),('warm_offwhite_trim','#CDCEBD'),('graygreen_frames_and_eave','#8B9988'),('muted_window_glazing','#7C8781'),('gray_brown_visible_tile_roof','#6C6B61'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_return_and_far_roof_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 paint(plane(1,-27)&zz(3,30.9),1,'registered_front_brick_field')
 paint((lo[:,0]>=-10.50025)&(hi[:,0]<=10.50025)&(lo[:,1]>=-31.50025)&(hi[:,1]<=-26.49975)&zz(3,42)&(n[:,2]<.1)&(n[:,1]<=0),1,'central_projecting_gable_vertical_brick_surfaces')
 for x in [-54,-36,-18,18,36,54]:
  arch=(lo[:,0]>=x-6.00025)&(hi[:,0]<=x+6.00025)&(lo[:,1]>=-27.00025)&(hi[:,1]<=-25.39975)&zz(6,26)
  paint(arch,1,'existing_arch_returns_and_brick_back_not_all_glazing')
  frame=(lo[:,0]>=x-4.05025)&(hi[:,0]<=x+4.05025)&(lo[:,1]>=-25.40025)&(hi[:,1]<=-24.19975)&zz(9,22.2)
  paint(frame,3,'existing_solid_mullion_strips_and_returns_graygreen_proxy')
  for dx in [-2.3,2.3]:
   for z in [9,13.8,18.6]:paint((lo[:,0]>=x+dx-1.75025)&(hi[:,0]<=x+dx+1.75025)&plane(1,-24.2)&zz(z,z+3.6),4,'existing_pane_recess_back_muted_glazing')
  paint((lo[:,0]>=x-6.25025)&(hi[:,0]<=x+6.25025)&(lo[:,1]>=-28.70025)&(hi[:,1]<=-26.89975)&zz(6,7),2,'existing_front_sill_offwhite')
 for x in [-10,10]:paint((lo[:,0]>=x-1.50025)&(hi[:,0]<=x+1.50025)&(lo[:,1]>=-32.00025)&(hi[:,1]<=-25.99975)&zz(30,37),2,'existing_central_gable_shoulder_offwhite')
 paint((lo[:,0]>=-.90025)&(hi[:,0]<=.90025)&(lo[:,1]>=-32.40025)&(hi[:,1]<=-31.39975)&zz(29,37),2,'existing_central_upright_relief_offwhite')
 paint(zz(30,43)&(n[:,2]>.1)&(n[:,1]<-.1)&(lo[:,0]>=-67.50025)&(hi[:,0]<=67.50025),5,'registered_main_front_roof_slope_graybrown_tile_proxy')
 for x in [-42,-21,21,42]:
  scope=(lo[:,0]>=x-6.00025)&(hi[:,0]<=x+6.00025)&(lo[:,1]>=-19.00025)&(hi[:,1]<=-6.99975)&zz(35,42)
  paint(scope&(n[:,2]>.1),5,'existing_front_dormer_slopes_graybrown')
  paint(scope&plane(1,-19),2,'existing_dormer_front_triangle_offwhite')
  paint(scope&(lo[:,1]>=-19.00025)&(hi[:,1]<=-18.29975)&zz(36.2,40.2),3,'existing_dormer_inner_triangle_graygreen_proxy_not_black_shadow')
 paint(plane(1,-29.65)&zz(29.7,30.9),3,'existing_front_eave_vertical_edge_graygreen')
 paint(plane(1,-29.6)&(lo[:,0]>=-6.00025)&(hi[:,0]<=6.00025)&zz(5.7,26.7),0,'central_entry_back_neutral_no_invented_door_leaf_or_glazing')
 paint(hi[:,2]<=3.0001,6,'display_base_not_plinth_or_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU Taiwan Literature E101 original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'e101-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NCKU photos; EXIF2017-12-21 primary and2010-02-25 cross-check, metadata not independently verified','scope':'Registered front brick, existing white shoulder/sill relief, graygreen window strips and eave, front roof slope only. Rear, small western return and far roof neutral; no fabricated gable edging.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
