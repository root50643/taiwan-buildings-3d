"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='64ef1c2e863bdc37c85143b1d96571f94654a6f0baaeb0032dc005336ece57d7'
PALETTE=[('neutral_walls_balconies_ties_roof_garden_and_unknown','#AAA79F'),('source_red_curved_fins_and_front_ribs','#B72C27'),('source_blue_outer_roof_fascias','#668AAB')]
def classify(tri):
 from shapely.geometry import Polygon
 t=tri;eps=1e-4;color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_walls_balconies_windows_ties_roofgarden_tower_and_unknown_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 for k,count in enumerate([52,54,46]):
  x=-60+k*6;yy=-48+k*2;poly=np.array([(x,3),(x+2.2,3),(x+2.2,14),(x+1.2,20),(x-2,25),(x-8,29),(x-14,31),(x-15,29),(x-9,26),(x-4,22),(x-1,17),(x,11)])
  P=Polygon(poly).buffer(eps);mask=np.zeros(len(t),bool)
  for i,tr in enumerate(t):
   if np.any(tr[:,1]<yy-1.4-eps) or np.any(tr[:,1]>yy+1.4+eps):continue
   if np.all(abs(tr[:,1]-(yy-1.4))<eps) or np.all(abs(tr[:,1]-(yy+1.4))<eps):
    if P.covers(Polygon(tr[:,[0,2]])):mask[i]=True
   for a,b in zip(poly,np.roll(poly,-1,axis=0)):
    v=b-a;d=tr[:,[0,2]]-a;cross=d[:,0]*v[1]-d[:,1]*v[0];q=d@v/(v@v)
    if np.all(abs(cross)/np.linalg.norm(v)<eps) and np.all((q>=-eps)&(q<=1+eps)):mask[i]=True
  assert mask.sum()==count,(k,mask.sum());paint(mask,1,'source2013_existing_curved_red_fin_exact_polygon_caps_edges_'+str(k))
 for x,count in zip([-61,-42,-23,-4,15,34],[21,21,21,21,21,14]):
  lo=np.array([x-1,-39.5,3]);hi=np.array([x+1,-36.5,38.5]);inside=np.all((t>=lo-eps)&(t<=hi+eps),axis=(1,2));surface=np.zeros(len(t),bool)
  for a in range(3):
   for v in [lo[a],hi[a]]:surface|=np.all(abs(t[:,:,a]-v)<eps,axis=1)
  mask=inside&surface;assert mask.sum()==count,(x,mask.sum());paint(mask,1,'source2013_existing_front_red_rib_box_outer_surfaces_only')
 mask=np.all(abs(t[:,:,1]+41)<eps,axis=1)&np.all((t[:,:,0]>=-74.5-eps)&(t[:,:,0]<=62.5+eps)&(t[:,:,2]>=37.6-eps)&(t[:,:,2]<=39.6+eps),axis=1);assert mask.sum()==2;paint(mask,2,'source2013_front_outer_blue_fascia_only_not_roof')
 P=Polygon([(-39,39),(34,61),(34,63),(-39,41)]).buffer(eps);mask=np.array([np.all(abs(tr[:,0]+65.5)<eps) and P.covers(Polygon(tr[:,[1,2]])) for tr in t]);assert mask.sum()==3;paint(mask,2,'source2013_left_rising_outer_blue_fascia_only')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU Magic School Red Entrance Blue Fascia Study original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nckumagic-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Three complete NCKU official photos, cameraOriginal2013-03-15, modified2013-03-18. Red curved entry fins and front narrow ribs; restrained blue front and rising left outerfascias only','scope':'Exact original fin polygon caps/edges and rib box surfaces; neutral unverified root ties, mixed balcony openings/walls/windows, terracegarden solids, tower and unknown roof/back. No vegetationgreen or extra ship/lettering. Original STL unchanged; historicalsource not2026condition.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
