"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='0e82c74526433d5037a26c5e25ed0cababf52aa95a339250e4c5e492fccedd35'
PALETTE=[('neutral_unknown','#AAA79F'),('pale_gray_aggregate_wall','#BCC0BB'),('muted_gray_green_glazing','#72817D'),('blue_solar_collector_tops_not_confirmed_PV','#4B7291'),('gray_roof_and_collector_edges','#868F91')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_longside_rear_base_or_mixed_balcony_floor_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.003,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-51)&xx(-6.5,34.5)&zz(2.3,93.3),1,'observed_main_front_gray_aggregate')
 paint(box(-53.5,-6.5,-46,-40.9,2.3,40.3),1,'observed_lower_front_gray_wall')
 paint(box(15.5,49,-61,-30.5,2.3,103.3),1,'observed_rounded_stair_exterior_gray_not_glass')
 # Curved recess cores are exterior solid proxies, never continuous glazing.
 for row in range(6):
  z=7+row*14.5
  for x in [2,18]:paint(plane(1,-50.5)&xx(x-5.5,x+5.5)&zz(z,z+8),2,'front_original_rectangular_window_back_only')
 for x in [-47,-31,-15]:
  for z in [7,25]:paint(plane(1,-41)&xx(x-5.5,x+5.5)&zz(z,z+10),2,'lower_front_original_rectangular_window_back_only')
 paint(plane(2,93.3)&xx(-6.5,34.5)&yy(-51,65),4,'aerial_main_flat_roof_gray_not_weathering')
 paint(plane(2,40.3)&xx(-53.5,-6.5)&yy(-41.5,19.5),4,'aerial_lower_flat_roof_gray_proxy')
 paint(plane(2,103.3)&xx(15.5,36.5)&yy(-51.5,-30.5),4,'aerial_stair_head_roof_gray')
 for x in [1,13,25]:
  paint(box(x-4.5,x+4.5,-33,57,93.2,95.3),4,'original_collector_edges_and_seams_gray')
  paint(plane(2,95.3)&xx(x-4.5,x+4.5)&yy(-33,57),3,'three_blue_solar_collector_rows_not_verified_photovoltaic')
 paint(hi[:,2]<=2.4001,0,'original_unsplit_base_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU Faculty Housing Visible Complex original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuufac-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official faculty housing complete front and aerial images; uncalibrated proxies','scope':'Pale gray visible frontage and rounded open stair bays, discrete front window backs only. Three blue solar collector rows top faces: photovoltaic type not confirmed. Mixed red/beige bay floors stay gray; unknown long side/rear neutral. Geometry and simplified horizontal collector slabs retained.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
