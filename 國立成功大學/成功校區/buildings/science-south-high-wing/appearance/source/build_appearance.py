"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='fb050883417a73563937606ee0042dd308fee2faf9aaf17c36679f486350fbac'
PALETTE=[('neutral_boxframes_open_corridors_walls_roof_unknown','#AAA79F'),('source_muted_green_original_thickened_louvres','#709463')]
def classify(tri):
 t=tri;eps=1e-4;color=np.zeros(len(t),dtype=int);why=np.full(len(t),'boxframes_open_corridor_backs_mixed_walls_windows_roof_and_unknown_neutral',dtype=object);total=np.zeros(len(t),bool);number=0
 patterns=[(46,[(-48,25),(-14,34),(21,26),(50,25)]),(59,[(-51,19),(-24,29),(10,35),(48,30)]),(72,[(-47,31),(-12,28),(19,24),(48,28)]),(85,[(-53,18),(-27,29),(8,35),(46,34)]),(98,[(-46,34),(-8,34),(27,29),(54,17)])]
 for row,(z,bays) in enumerate(patterns):
  for j,(xx,w) in enumerate(bays):
   for side in ([-1,1] if (row+j)%2==0 else [1]):
    for dz in [2,3.8,5.6,7.4,9.2]:
     x=xx+side*(w/2-2.5);lo=np.array([x-1.75,-55.75,z+dz]);hi=lo+[3.5,1.5,.8];within=np.all((t>=lo-eps)&(t<=hi+eps),axis=(1,2));surface=np.zeros(len(t),bool)
     for a in range(3):
      for v in [lo[a],hi[a]]:surface|=np.all(abs(t[:,:,a]-v)<eps,axis=1)
     m=within&surface;assert m.sum() in [8,12];assert not np.any(total&m);total|=m;number+=1
 assert number==150 and total.sum()==1320;color[total]=1;why[total]='source2018_green_louvre_material_existing150_thickened_box_strips_only_not_full_density_replica'
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU Science South Original Louvres Only original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nckuscisouth-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official NCKU GIS38126 complete800x600 daytimephoto cameraOriginal2018-10-04 supports mutedgreen louvres; other2018views shapecontext only','scope':'Only150 original thickenedslatboxes1320wholefaces. Slatdensity/widthpattern simplified, notexactphoto replication. Whiteboxframes/openbalconybacks/mixedbrickcreamwalls/windows/roof/unknownneutral. No glasscolor inopen corridors; noadditionalgreen backingpanels orgeometry.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
