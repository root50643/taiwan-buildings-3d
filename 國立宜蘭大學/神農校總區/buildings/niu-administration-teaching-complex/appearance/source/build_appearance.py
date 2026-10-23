"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='d8f9925c97d2076d1aa4eec343b0fbf9aa6bb24ccfc9c32b52974394d5df2bdd'
PALETTE=[('neutral_unconfirmed_structure','#AAA79F'),('observed_upper_front_glazing_proxy','#98ABB2')]
def regions():
 yield from [('z41.2_window1', -47.853818181818184, -41.164363636363646, 42.325, 47.575), ('z41.2_window2', -36.61854545454545, -32.174181818181815, 42.325, 47.575), ('z41.2_window3', -29.179636363636366, -23.314909090909094, 42.325, 47.575), ('z41.2_window4', -16.985454545454544, -12.86181818181818, 42.325, 47.575), ('z41.2_window5', -9.209454545454545, 0.04581818181818065, 42.325, 47.575), ('z41.2_window6', 5.838545454545456, 10.786909090909091, 42.325, 47.575), ('z41.2_window7', 17.862545454545447, 27.301090909090902, 42.325, 47.575), ('z41.2_window8', 33.208363636363636, 35.45345454545454, 42.325, 47.575), ('z41.2_window9', 38.307272727272725, 47.24181818181818, 42.325, 47.575), ('z32.0_window1', -49.20545454545455, -44.85272727272727, 33.125, 38.375), ('z32.0_window2', -39.70799999999999, -32.88109090909091, 33.125, 38.375), ('z32.0_window3', -28.220727272727274, -24.601090909090914, 33.125, 38.375), ('z32.0_window4', -20.343272727272726, -13.562181818181818, 33.125, 38.375), ('z32.0_window5', -8.780727272727276, -3.328363636363639, 33.125, 38.375), ('z32.0_window6', 2.8047272727272725, 10.089818181818181, 33.125, 38.375), ('z32.0_window7', 14.373818181818187, 18.22254545454546, 33.125, 38.375), ('z32.0_window8', 23.746909090909085, 29.794909090909087, 33.125, 38.375), ('z32.0_window9', 36.55309090909091, 43.105090909090904, 33.125, 38.375), ('z22.8_window1', -48.32181818181818, -41.67818181818182, 23.925, 29.175), ('z22.8_window2', -37.00145454545454, -32.51127272727272, 23.925, 29.175), ('z22.8_window3', -28.49236363636363, -23.08581818181818, 23.925, 29.175), ('z22.8_window4', -17.266909090909095, -13.234909090909094, 23.925, 29.175), ('z22.8_window5', -8.934545454545454, -1.145454545454546, 23.925, 29.175), ('z22.8_window6', 5.023636363636367, 10.750909090909094, 23.925, 29.175), ('z22.8_window7', 15.185454545454553, 19.767272727272733, 23.925, 29.175), ('z22.8_window8', 24.463636363636365, 30.19090909090909, 23.925, 29.175), ('z22.8_window9', 36.55309090909091, 43.105090909090904, 23.925, 29.175)]
def classify(tri):
 v=tri;e=2e-5;color=np.zeros(len(v),dtype=int);why=np.full(len(v),'neutral_unconfirmed_or_outside_documented_scope',dtype=object)
 normal=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);plane=(abs(v[:,:,1]+60.32)<e).all(1)&(normal[:,1]<-1e-8)
 for name,x0,x1,z0,z1 in regions():
  mask=plane&(v[:,:,0]>=x0-e).all(1)&(v[:,:,0]<=x1+e).all(1)&(v[:,:,2]>=z0-e).all(1)&(v[:,:,2]<=z1+e).all(1)
  assert not color[mask].any();color[mask]=1;why[mask]=name
 assert np.bincount(color).tolist()==[6600,54]
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NIU Administration Teaching Complex limited original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'niu-administration-teaching-complex-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Author YLUS01-07 personally viewed; capture dates unproven. Light low-saturation opaque glass/curtain proxy, not calibrated current condition.','scope':'Only upper THREE rows, 27 front -Y chamfered-window backing panes, 54 entire triangles. Lower TWO rows, all sloping reveals, opaque elevations, roof and courtyard openings remain neutral. Geometry unchanged.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
