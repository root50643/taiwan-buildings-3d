"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='f3270ed0011806b4e4ac1100e8ed7d7a736da2e38aaa19757f3482be120e5e00'
PALETTE=[('neutral_unseen','#AAA79F'),('ivory_plaster','#C8C9BA'),('warm_brown_timber','#907353'),('muted_glazing','#5D706B'),('tan_gray_masonry','#AAA18B'),('gray_tile_visible_roof','#777B75'),('gray_metal_secondary_canopy','#909A98'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_return_and_far_roof_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 paint(plane(1,-36.5)&zz(3,38.9),1,'registered_front_plaster_proxy_wood_only_existing_window_regions')
 paint((plane(0,-65)&zz(34.65,38.9))|(plane(0,-69)&zz(38,60)),1,'observed_left_upper_wall_and_gable_ivory')
 paint(plane(0,-65)&zz(9,34.65),2,'existing_left_lower_wall_between_siding_bands_timber')
 for z in [9,14,19,24,29,34]:paint((lo[:,0]>=-65.90025)&(hi[:,0]<=-64.89975)&(lo[:,1]>=-36.50025)&(hi[:,1]<=36.50025)&zz(z,z+.65),2,'existing_left_siding_relief_timber')
 for x in [-52,-20,-9,2,13,24,52]:
  scope=(lo[:,0]>=x-4.05025)&(hi[:,0]<=x+4.05025)&(lo[:,1]>=-36.50025)&(hi[:,1]<=-35.69975)&zz(8,30.9)
  paint(scope&~plane(1,-36.5),2,'existing_front_window_returns_timber_flat_strips_not_separable')
  for dx in [-3,0,3]:
   for z in [8,12.8,17.6,22.4,27.2]:paint((lo[:,0]>=x+dx-1.05025)&(hi[:,0]<=x+dx+1.05025)&plane(1,-35.7)&zz(z,z+3.7),3,'existing_front_pane_back_muted_glazing')
 for dy in [-3.6,0,3.6]:
  for z in [10,15,20,25,30]:
   mask=(lo[:,1]>=-19+dy-1.30025)&(hi[:,1]<=-19+dy+1.30025)&(lo[:,0]>=-65.90025)&(hi[:,0]<=-64.19975)&zz(z,z+4)
   paint(mask,2,'existing_left_corner_window_returns_timber');paint(mask&plane(0,-64.2),3,'left_corner_existing_pane_back_glazing')
 for y in [-2,1,4]:
  mask=(lo[:,1]>=y-.85025)&(hi[:,1]<=y+.85025)&(lo[:,0]>=-69.00025)&(hi[:,0]<=-68.19975)&zz(44,51)
  paint(mask,2,'existing_high_gable_vent_returns_timber');paint(mask&plane(0,-68.2),0,'high_gable_vent_back_neutral_not_asserted_glass')
 for x in [-36,37]:paint((lo[:,0]>=x-1.50025)&(hi[:,0]<=x+1.50025)&(lo[:,1]>=-39.00025)&(hi[:,1]<=-34.99975)&zz(3,32),4,'existing_front_solid_piersonly_tan_gray_masonry')
 paint(zz(38,60)&(n[:,2]>.1)&(n[:,1]<-.1),5,'registered_near_main_roof_slope_gray_tile_proxy')
 paint((lo[:,0]>=-59.00025)&(hi[:,0]<=59.00025)&(lo[:,1]>=-43.00025)&(hi[:,1]<=-35.99975)&zz(31,35.6),6,'existing_secondary_canopy_gray_metal_not_red_tile')
 paint(hi[:,2]<=3.0001,7,'display_base_not_stone_plinth_or_site_surface')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU Taiwan Literature Lecture Hall E107 original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'e107-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NCKU GIS38153/38152 photos; embedded 2023-09-28 capture timestamps not independently verified','scope':'Front plaster and existing timber window returns (flat strips remain plaster because shared triangles cannot isolate them), observed left siding/gable, near gray tiled roof and gray metal canopy. Rear, mapped small return and far roof neutral; no invented plinth boundary.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
