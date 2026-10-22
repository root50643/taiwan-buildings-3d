"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='6e1960bf13afe0f05ead516f8994e5fc83d220cd010d304b524a4a9231d020ee'
PALETTE=[('neutral_unresolved_envelope_and_base','#AAA79F'),('muted_blue_green_stair_tower_front_frames','#638A8B')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);eps=.00015
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'neutral_unresolved_glass_mixed_bands_side_cheeks_hidden_surfaces_or_base',dtype=object)
 normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 def bounds(i,a,b):return (lo[:,i]>=a-eps)&(hi[:,i]<=b+eps)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<eps,axis=1)
 for x in [-31,20]:
  front=plane(1,-16.5)&bounds(0,x-4.5,x+4.5)&bounds(2,2.8,56.8)&(normal[:,1]<0)
  # All vertices must lie entirely in one solid frame strip (not across the recess).
  solid=bounds(0,x-4.5,x-2.15)|bounds(0,x+2.15,x+4.5)|bounds(2,54,56.8)
  cap=plane(1,-17)&bounds(0,x-6,x+6)&bounds(2,56,57.8)&(normal[:,1]<0)
  mask=(front&solid)|cap
  color[mask]=1;why[mask]='official_14_jpg_stair_tower_solid_front_frame_or_cap_front_full_triangle'
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'HWAI H Student Activities Center limited original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'hwai-activity-h-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official HWAI school history image 14.jpg; capture date unknown; viewed 2026-10-22; uncalibrated opaque display proxies','scope':'Only solid front frames and cap front vertical faces of two stair towers. Glass, crossbars, mixed horizontal bands, side cheeks, walls, roofs and other surfaces remain neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
