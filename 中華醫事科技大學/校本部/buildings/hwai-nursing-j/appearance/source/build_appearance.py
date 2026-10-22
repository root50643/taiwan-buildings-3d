"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='6a529f825d294ee1066af11a9202e2f55214a43a5c91959407cbfc0f9c24b290'
PALETTE=[('neutral_unresolved_envelope_and_base','#AAA79F'),('muted_red_brown_visible_low_wing_roof','#8C4847'),('muted_green_single_recess_glazing','#3D8D72')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);eps=.00015
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'neutral_unresolved_mixed_walls_gable_hidden_surfaces_or_base',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def bounds(i,a,b):return (lo[:,i]>=a-eps)&(hi[:,i]<=b+eps)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<eps,axis=1)
 # Original hip cap taper: x half-width 15 -> 10.8, y half-depth 14 -> .42.
 # Restrict all three vertices to each original visible slope, not centroid selection.
 region=bounds(0,-67,-37)&bounds(1,-33,-5)&bounds(2,71,74.2)
 front=np.all(abs(t[:,:,2]-71-(t[:,:,1]+33)*3.2/13.58)<eps,axis=1)
 left=np.all(abs(t[:,:,2]-71-(t[:,:,0]+67)*3.2/4.2)<eps,axis=1)
 paint(region&(front|left),1,'official_14_jpg_visible_front_or_left_low_wing_original_hip_slope_full_triangle')
 glass=plane(1,-25.5)&bounds(0,-38.9,-35.1)&bounds(2,23,110)
 paint(glass,2,'official_14_jpg_single_front_left_recess_back_wall_full_triangle_excluding_crossbars')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'HWAI J Nursing Building limited original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'hwai-nursing-j-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official HWAI school history image 14.jpg; capture date unknown; viewed 2026-10-22; uncalibrated opaque display proxies','scope':'Only front and left original slopes of low front-left wing hip cap and back wall of single front-left vertical glazing recess. Mixed walls, gable, horizontal windows, hidden roofs and other surfaces remain neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
