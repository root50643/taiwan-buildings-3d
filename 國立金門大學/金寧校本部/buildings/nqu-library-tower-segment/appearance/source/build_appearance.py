"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='5ad3e706ccff2624837ef436f6670cde090fa49231c5ba8a3e409a3a03ae5ee0'
PALETTE=[('neutral_unseen','#AAA79F'),('terracotta_brick','#AB6856'),('pale_stone_trim','#C5C3B7'),('charcoal_tile_roof','#565D61'),('dark_glazing_proxy','#52636B'),('gray_stone_plinth','#8D9393'),('display_plinth','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_and_unreviewed_left_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00015)&(hi[:,2]<=b+.00015)
 front=(hi[:,1]<=-18.9998)&(n[:,1]<-.5);right=(lo[:,0]>=18.9998)&(n[:,0]>.5)
 paint((front|right)&zz(23,110),1,'registered_front_and_right_shaft_brick')
 # Raised quoins, not background wall, remain pale.
 for z in np.arange(23,109,3):
  for x in [-18.7,18.7]:paint((lo[:,0]>=x-.9002)&(hi[:,0]<=x+.9002)&(hi[:,1]<=-18.5998)&zz(z,z+1.3),2,'existing_front_raised_pale_quoin')
  for y in [-18.7,18.7]:paint((lo[:,1]>=y-.9002)&(hi[:,1]<=y+.9002)&(lo[:,0]>=18.5998)&zz(z,z+1.3),2,'existing_right_raised_pale_quoin')
 # Existing window surround relief and backed glazing only.
 for z in [30,55,80]:
  paint((lo[:,0]>=-2.5502)&(hi[:,0]<=2.5502)&(hi[:,1]<=-18.6498)&zz(z-.9,z+11.4),2,'existing_front_narrow_window_pale_surround')
  paint((lo[:,1]>=-2.5502)&(hi[:,1]<=2.5502)&(lo[:,0]>=18.6498)&zz(z-.9,z+11.4),2,'existing_right_narrow_window_pale_surround')
  paint(np.all(abs(t[:,:,1]+17.7)<.0002,axis=1)&(lo[:,0]>=-1.6502)&(hi[:,0]<=1.6502)&zz(z,z+10.5),4,'existing_front_narrow_recess_back_glazing')
  paint(np.all(abs(t[:,:,0]-17.7)<.0002,axis=1)&(lo[:,1]>=-1.6502)&(hi[:,1]<=1.6502)&zz(z,z+10.5),4,'existing_right_narrow_recess_back_glazing')
 for x in [-3.1,3.1]:
  paint((lo[:,0]>=x-2.3002)&(hi[:,0]<=x+2.3002)&(hi[:,1]<=-18.6498)&zz(97.2,109),2,'existing_top_pair_pale_surround')
  paint(np.all(abs(t[:,:,1]+17.7)<.0002,axis=1)&(lo[:,0]>=x-1.3502)&(hi[:,0]<=x+1.3502)&zz(98,108),4,'existing_top_pair_recess_back_glazing')
 paint(((hi[:,1]<=-19.7998)|(lo[:,0]>=19.7998))&zz(3,23),5,'registered_front_right_gray_stone_plinth')
 paint(np.all(abs(t[:,:,1]+18.35)<.0002,axis=1)&(lo[:,0]>=-1.3502)&(hi[:,0]<=1.3502)&zz(11,19),4,'existing_plinth_front_recess_back_glazing')
 # Visible balcony, head and corbels; unknown back/left faces not copied.
 paint(((c[:,1]<-17.9)|(c[:,0]>17.9))&zz(110,133),2,'registered_balcony_and_head_pale_proxy')
 paint(((hi[:,1]<=-17.4998)|(lo[:,0]>=17.4998))&zz(107.5,111.5),2,'existing_visible_balcony_corbel_stone')
 paint(np.all(abs(t[:,:,1]+16.75)<.0002,axis=1)&(lo[:,0]>=-11.0002)&(hi[:,0]<=11.0002)&zz(120,125),4,'existing_head_front_glazing_back')
 paint(np.all(abs(t[:,:,0]-16.75)<.0002,axis=1)&(lo[:,1]>=-9.0002)&(hi[:,1]<=9.0002)&zz(120,125),4,'existing_head_right_glazing_back')
 # Front pitched tile surfaces only; actual raised gable sheets stay pale.
 paint((lo[:,2]>=131.3998)&(hi[:,1]<=.0002)&(n[:,2]>.1),3,'registered_front_roof_tile_surface')
 for x in [-17,17]:paint((lo[:,0]>=x-1.5002)&(hi[:,0]<=x+1.5002)&(lo[:,2]>=131.3998),2,'existing_raised_gable_panel_pale')
 paint((lo[:,2]>=131.3998)&(hi[:,1]<=.0002)&(abs(n[:,2])<.1),2,'existing_front_eave_edge_pale')
 paint(hi[:,2]<=3.0001,6,'display_base_not_real_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NQU Library Tower Segment original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nqu-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated JJP architect primary project photograph, capture date unknown approximations, not measured material swatches','scope':'Registered architect-photo front and right only; pale raised quoins; front tile roof; unseen rear and unreviewed left neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
