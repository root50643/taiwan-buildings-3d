"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='e787eed05e65220adfc6118c4da2cf82c4a7b3247c258df38b3de592241ad8fb'
PALETTE=[('neutral_mixed_masonry_corridors_canopy_trim_roof','#AAA79F'),('source_pale_reflective_gray_glazing_proxy','#C5CBCA'),('source_restrained_bluegray_thin_mullions','#537E89')]
def classify(tri):
 t=tri;eps=.0001;color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_redgray_walls_open_corridor_arcades_canopy_roundaperture_archtrim_roof_back_neutral',dtype=object)
 mask=np.all(abs(t[:,:,1]+27.5)<eps,axis=1)&np.all((abs(t[:,:,0])<=6+eps)&(t[:,:,2]>=16-eps)&(t[:,:,2]<=50+eps),axis=1);assert mask.sum()==25;color[mask]=1;why[mask]='source2010_central_arch_discrete_glazing_back_pale_reflection_proxy_not_cyan'
 def bs(lo,hi,count):
  lo=np.array(lo);hi=np.array(hi);mask=np.all((t>=lo-eps)&(t<=hi+eps),axis=(1,2));surf=np.zeros(len(t),bool)
  for a in range(3):
   for v in [lo[a],hi[a]]:surf|=np.all(abs(t[:,:,a]-v)<eps,axis=1)
  mask&=surf;assert mask.sum()==count;return mask
 for x in [-3,3]:
  mask=bs([x-.5,-29.05,16],[x+.5,-27.55,42],54);color[mask]=2;why[mask]='source2010_existing_central_arch_thin_vertical_bluegray_mullion'
 for z,count in zip(range(20,47,5),[36,36,36,36,36,16]):
  mask=bs([-6,-29.05,z],[6,-27.55,z+1],count);color[mask]=2;why[mask]='source2010_existing_central_arch_thin_horizontal_bluegray_mullion'
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Putong Central Arch Glazing Frame Only original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntuputong-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Four complete official NTU campusplanning photos cameraOriginal2010-10-16, modified2011-01-11 separate. Central arch pale reflectivegray glass proxy and restrainedbluegray thin mullions only','scope':'Central arched recessback and2vertical6horizontal originalbox members only. Broad architectural archtrim neutral, not sameas thinmetal frame. Redgraywallmixedfaces,openwingcorridors and groundarcades,canopy,roundaperture,roof/back neutral. No2026conditionclaim;originalSTLunchanged.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
