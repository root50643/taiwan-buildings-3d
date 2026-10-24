"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='e4fbac9f7a983850267a3f57d710e6af2ca94d5f67295be2c384c48fc0c54b4b'
PALETTE=[('neutral_unconfirmed_structure','#AAA79F'),('opaque_upper_brick_proxy','#A56950')]
def classify(tri):
 sel=json.loads((A/'source/source-selection.json').read_text());color=np.zeros(len(tri),dtype=int);why=np.full(len(tri),'neutral_unconfirmed_or_excluded',dtype=object)
 cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(cross,axis=1);norm=cross/length[:,None];areas=length/2;audit=[];eps=sel['tolerance_mm']
 for g in sel['groups']:
  axis=g['plane_axis'];mask=(norm[:,axis]*g['normal_sign']>.999999)&(abs(tri[:,:,axis]-g['plane_mm'])<=eps).all(1)
  for axis,bounds in [(g['other_axis'],g['other_range_mm']),(2,g['z_range_mm'])]:
   lo,hi=bounds;mask&=(tri[:,:,axis]>=lo-eps).all(1)&(tri[:,:,axis]<=hi+eps).all(1)
  ids=np.flatnonzero(mask).tolist();assert ids==g['canonical_triangle_ids'],g['name'];assert not np.any(color[mask]);color[mask]=1;why[mask]=g['name'];area=float(areas[mask].sum());assert abs(area-g['area_mm2'])<1e-7;audit.append(dict(name=g['name'],ids=ids,count=len(ids),area_mm2=area))
 assert np.bincount(color).tolist()==[9388,238]
 assert abs(float(areas[color>0].sum())-2900.7799204075227)<1e-7
 (A/'qa/material-boundaries.json').write_text(json.dumps(dict(method='Actual outward normals and all three original vertices in four approved finite upper entry/garden brick planes; tolerance 0.00003 mm; no geometry changes',counts=np.bincount(color).tolist(),selected_area_mm2=float(areas[color>0].sum()),groups=audit),indent=2)+'\n')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'ISU Student Activity Center limited-scope limited original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'isu-student-activity-center-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official ISU history captions 2022, not authenticated EXIF capture dates; Secretary Office credit. Opaque uncalibrated brick proxy.','scope':'238 complete original upper entry +Y and garden -X brick faces; 9388 neutral. Frames, windows, belts, lower walls, roofs, east and rear unchanged. Evidence boundary is not a real material seam.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
