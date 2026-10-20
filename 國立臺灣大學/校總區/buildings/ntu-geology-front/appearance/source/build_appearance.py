"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='4ecea8d81d75b9516a6adedc9a467d159325959f6ea79ccab3c14cca0ec4615d'
PALETTE=[('neutral_unseen','#AAA79F'),('brick_red_infill','#A46657'),('light_gray_structure','#B3B7AE'),('pale_precast_hoods','#D0D4CA'),('muted_glazing','#5E7069'),('gray_canopy_and_entry_frames','#959E95'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_ends_and_roof_top_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def xx(a,b):return (lo[:,0]>=a-.00025)&(hi[:,0]<=b+.00025)
 def yy(a,b):return (lo[:,1]>=a-.00025)&(hi[:,1]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 paint(plane(1,-15.5)&zz(3,46.8),1,'observed_front_brick_infill_only')
 for z in [3,18,32,45]:paint(xx(-68.5,68.5)&yy(-16.45,-14.95)&zz(z,z+1.6),2,'existing_horizontal_structure_light_gray')
 for x in [-67,-47.5,-28.5,-9.5,9.5,28.5,47.5,67]:paint(xx(x-.75,x+.75)&yy(-16.5,-14.9)&zz(3,46),2,'existing_vertical_structure_light_gray')
 for x in [-57,-38,-19,0,19,38,57]:
  for center in [x-5.5,x,x+5.5]:
   for z,h in [(5,12.5),(21,10.5),(35,9)]:
    if x==0 and z==5:continue
    paint(xx(center-2.65,center+2.65)&yy(-19.3,-14.7)&zz(z,z+h+1)&~plane(1,-15.5),3,'existing_deep_precast_arched_hood_and_returns_pale')
    paint(xx(center-1.75,center+1.75)&plane(1,-14)&zz(z+.9,z+h+.7),4,'existing_inner_arch_back_glazing_not_hood_return')
 paint(xx(-13,13)&yy(-28.5,-13.5)&zz(16,19.8),5,'existing_curved_canopy_gray_proxy')
 paint(xx(-9,9)&plane(1,-14)&zz(3.2,14.2),4,'existing_entry_recess_back_glazing')
 for x in [-6,0,6]:paint(xx(x-.45,x+.45)&yy(-16,-14)&zz(3,14.3),5,'original_entry_mullions_gray')
 for x in range(-66,67,4):paint(xx(x-.6,x+.6)&yy(-19.4,-14.4)&zz(44,46.5),2,'existing_front_roof_edge_teeth_gray')
 paint(plane(1,-18)&zz(46,48),2,'front_roof_edge_only_not_unseen_top')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Geology Three Storey Front Block original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'geology-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NTU archival S22 IMG5857 and IMG5858 photos; capture date not independently verified','scope':'Three-storey front block only. Red brick infill, original pale projecting arched hoods, gray structure/canopy and muted recessed glazing. Ends/rear/roof top neutral, no rear complex or specimen building invented.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
