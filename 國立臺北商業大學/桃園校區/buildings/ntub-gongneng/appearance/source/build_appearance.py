"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='32580d5fcdbbc1ad05bac9f77d49d2c568735e797c300007311c5d6597c3e164'
# Exact native linear RGBA is retained in Blend; 3MF displaycolor is an 8-bit sRGB proxy.
def srgb(v):return 12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055
ORIGINAL=json.loads((A/'source/original-materials.json').read_text())['materials']
PALETTE=[(m['name'],'#'+''.join(f'{round(srgb(v)*255):02X}' for v in m['diffuse_color'][:3])) for m in ORIGINAL]+[('opaque_PV_proxy','#344B5D'),('opaque_glazing_proxy','#526D73')]
def classify(tri):
 sel=json.loads((A/'source/source-selection.json').read_text());color=np.zeros(len(tri),dtype=int);why=np.full(len(tri),'unchanged_original_neutral',dtype=object)
 cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(cross,axis=1);norm=cross/length[:,None];areas=length/2;eps=sel['tolerance_mm'];audit=[]
 for g in sel['groups']:
  mask=(norm@np.array(g['normal'])>=1-1e-7)&(abs(tri[:,:,g['axis']]-g['plane'])<=eps).all(1)
  for axis,lo,hi in g['bounds']:mask&=(tri[:,:,axis]>=lo-eps).all(1)&(tri[:,:,axis]<=hi+eps).all(1)
  ids=np.flatnonzero(mask).tolist();assert ids==g['faces'];assert not color[mask].any();color[mask]=1 if g['material']=='pv' else 2;why[mask]=g['name'];area=float(areas[mask].sum());assert abs(area-g['area_mm2'])<1e-7;audit.append(dict(name=g['name'],ids=ids,count=len(ids),area_mm2=area))
 assert np.bincount(color).tolist()==[5150,48,96];assert np.flatnonzero(color).tolist()==sel['approved_canonical_face_ids'];assert abs(areas[color>0].sum()-sel['area_mm2'])<1e-7
 (A/'qa/material-boundaries.json').write_text(json.dumps(dict(method='Actual cross-product outward normals and all three original vertices in three finite support-plane rectangles; no mesh changes',counts=np.bincount(color).tolist(),selected_area_mm2=float(areas[color>0].sum()),groups=audit,original_unselected_assignments_unchanged=True),indent=2)+'\n')
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
 colors,why=classify(tri);assert set(colors)=={0,1,2}
 # .17g exactly roundtrips every source float32 value as float64.
 ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';E.register_namespace('',ns)
 model=E.Element('{'+ns+'}model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'});res=E.SubElement(model,'resources');bm=E.SubElement(res,'basematerials',{'id':'20'})
 for name,color in PALETTE:E.SubElement(bm,'base',{'name':name,'displaycolor':color+'FF'})
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTUB Gongneng Building limited-scope limited original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntub-gongneng-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'native_original_materials':ORIGINAL,'colors':'Original native linear RGBA retained exactly in Blend, nearest 8-bit sRGB in 3MF. Added opaque uncalibrated dark-blue-gray PV and lighter gray-blue glazing proxies.','scope':'Only 144 original faces: 48 coarse existing PV top triangles, NOT 48 actual panels, and 96 front tower glazing faces. 5150 neutral unchanged. Existing 4x5 / 70x71mm field remains approximate, no new precise boundary or current-condition claim.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
