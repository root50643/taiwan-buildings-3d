"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='b143999b5181b615e1b14f6cc6201fcfdec115428cb7b3b5782cf6f3ae0b2e07'
PALETTE=[('neutral_unseen','#AAA79F'),('orange_red_brick_fields','#B96943'),('warm_gray_concrete','#AAA68E'),('offwhite_gable_and_soffit','#D0D0BD'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_side_rear_court_and_roofs_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 for x,z in [(-31,24),(31,26)]:
  paint((lo[:,0]>=x-14.50025)&(hi[:,0]<=x+14.50025)&plane(1,-65.5)&zz(3,z+.9),1,'registered_front_mass_brick_field')
  paint((lo[:,0]>=x-9.50025)&(hi[:,0]<=x+9.50025)&(lo[:,1]>=-65.50025)&(hi[:,1]<=-64.99975)&zz(5,17),1,'existing_shallow_front_panel_is_brick_not_glazing')
  for xx in [x-12,x+12]:paint((lo[:,0]>=xx-.60025)&(hi[:,0]<=xx+.60025)&(lo[:,1]>=-66.65025)&(hi[:,1]<=-65.34975)&zz(3,25),2,'existing_front_vertical_frame_concrete')
  paint((lo[:,0]>=x-17.00025)&(hi[:,0]<=x+17.00025)&plane(1,-68)&zz(z,z+8),3,'registered_gable_front_offwhite_no_invented_trim_border')
 for x in [-18,-6,6,18]:paint((lo[:,0]>=x-1.25025)&(hi[:,0]<=x+1.25025)&(lo[:,1]>=-66.50025)&(hi[:,1]<=-63.49975)&zz(3,19),2,'four_existing_canopy_piers_concrete')
 canopy=(lo[:,0]>=-23.00025)&(hi[:,0]<=23.00025)&(lo[:,1]>=-68.00025)&(hi[:,1]<=-43.99975)&zz(18,22)
 paint(canopy&~plane(2,20)&~((lo[:,0]>=20)&(hi[:,2]>21))&~((hi[:,0]<=-20)&(hi[:,2]>21)),2,'registered_canopy_vertical_and_edge_surfaces_concrete_proxy')
 paint(canopy&plane(2,18),3,'existing_canopy_underside_pale_soffit')
 paint(hi[:,2]<=3.0001,4,'display_base_not_ground_or_plinth')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU Chinese Department original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'chinese-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NCKU GIS images 38146 and 38147; capture dates unknown','scope':'Front-only brick shallow panels, original concrete frames and canopy piers, pale gable faces; no glazing claim. Rear court and all roof surfaces neutral; inherited asymmetrical massing not corrected.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
