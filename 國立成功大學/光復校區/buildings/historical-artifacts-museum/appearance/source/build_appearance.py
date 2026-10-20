"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='ca13cdfad947e1da58621ad2ac64cfda4d9065476800170de0cf138bab22d72f'
PALETTE=[('neutral_unseen','#AAA79F'),('red_brown_brick','#9D6350'),('cream_trim','#C7C5AC'),('warm_wood_recess_returns','#786348'),('muted_glazing_proxy','#7F8980'),('gray_tile_visible_roof','#747674'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_right_side_rear_and_far_roof_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 paint(plane(1,-67)&zz(3,26.9),1,'registered_front_brick_field')
 paint(plane(0,-32.5)&zz(3,26.9),1,'registered_left_long_wall_brick_field')
 for x in [-31,-10.5,10.5,31]:paint((lo[:,0]>=x-1.50025)&(hi[:,0]<=x+1.50025)&(lo[:,1]>=-68.00025)&(hi[:,1]<=-66.59975)&zz(3,26.2),1,'existing_front_brick_pilaster')
 for y in [-65,-42,-22,-2,18,38,66]:paint((lo[:,0]>=-33.55025)&(hi[:,0]<=-32.04975)&(lo[:,1]>=y-1.50025)&(hi[:,1]<=y+1.50025)&zz(3,26.2),1,'existing_observed_left_brick_pilaster')
 for x in [-20,20]:
  mask=(lo[:,0]>=x-4.30025)&(hi[:,0]<=x+4.30025)&(lo[:,1]>=-67.00025)&(hi[:,1]<=-65.99975)&zz(8,21.5)
  paint(mask,3,'existing_front_window_returns_wood_proxy');paint(mask&plane(1,-66),4,'existing_front_window_back_muted_glazing')
  paint((lo[:,0]>=x-5.00025)&(hi[:,0]<=x+5.00025)&(lo[:,1]>=-68.45025)&(hi[:,1]<=-66.89975)&(zz(7.2,8.3)|zz(20.3,21.5)),2,'existing_front_sill_and_lintel_cream')
 for y in [-52,-32,-12,8,28,48]:
  mask=(lo[:,0]>=-32.50025)&(hi[:,0]<=-31.49975)&(lo[:,1]>=y-3.85025)&(hi[:,1]<=y+3.85025)&zz(8,21.5)
  paint(mask,3,'observed_left_window_returns_wood_proxy');paint(mask&plane(0,-31.5),4,'observed_left_window_recess_back_glazing_proxy')
  paint((lo[:,0]>=-33.75025)&(hi[:,0]<=-32.24975)&(lo[:,1]>=y-4.60025)&(hi[:,1]<=y+4.60025)&zz(7.2,8.2),2,'existing_left_sill_cream')
 paint((lo[:,0]>=-11.00025)&(hi[:,0]<=11.00025)&(lo[:,1]>=-73.00025)&(hi[:,1]<=-65.99975)&zz(22.5,24.3),2,'existing_entry_rain_shelter_cream')
 paint((plane(1,-68.5)|plane(0,-34))&zz(25.3,27.1),2,'observed_front_and_left_eave_band_vertical_edge_cream')
 paint(zz(26.7,37.3)&(n[:,2]>.1)&((n[:,0]<-.1)|(n[:,1]<-.1)),5,'registered_front_and_left_roof_slopes_gray_tile_proxy')
 paint(hi[:,2]<=3.0001,6,'display_base_not_white_stone_plinth')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU Historical Artifacts Museum original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'artifact-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NCKU photos 3055 and 3489; posted 2024-08-07 and 2025-02-05, capture dates separately unverified','scope':'Front and left long side only; corresponding roof slopes gray; unseen right, rear and far slopes neutral. No new plinth boundary or door glazing claim.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
