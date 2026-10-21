"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='c8e05927c1944962c18280678321b25cf2029755aaeab74c63888fc00e58bc86'
PALETTE=[('neutral_walls_side_blindpanels_roof_and_unknown','#AAA79F'),('source_curved_front_muted_graygreen_window_proxy','#7C9790')]
def classify(tri):
 t=tri;eps=1e-4;color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mainwalls_all_sidewindows_blindpanels_entry_roof_and_unknown_neutral',dtype=object);total=np.zeros(len(t),bool)
 for z in [9,22,35,48,61,74,87]:
  for ang in [-56,-28,0,28,56]:
   a=np.deg2rad(ang);xx=38*np.sin(a);yy=-36-17.48*np.cos(a);r=np.deg2rad(ang*.46);q=t-[xx,yy,0];q=q@np.array([[np.cos(r),np.sin(r),0],[-np.sin(r),np.cos(r),0],[0,0,1]])
   mask=np.all(abs(q[:,:,1]-1.4)<eps,axis=1)&np.all((abs(q[:,:,0])<=5.5+eps)&(q[:,:,2]>=z-eps)&(q[:,:,2]<=z+7.7+eps),axis=1);assert mask.sum() in [2,4],(z,ang,mask.sum());total|=mask
 assert total.sum()==98;color[total]=1;why[total]='source_lowresolution_front_seven_levels_only_glazingproxy_original_fiveangle_simplification_not_exact_bay_count'
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU Uni President Curved Front Recess Study original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nckuhealth-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official complete300x227 NCKU frontoblique source supports sevenlevel mutedgraygreen windows only; nofineframe orcurrentconditionclaim','scope':'Only98whole original frontrecessback triangles. Originalfiveangle35cuts simplify source threefrontgroups; notwindowaccuratereconstruction. GISsidephotoorientation notverified; allsidewindows includingtopblindpanels neutral. Walls/entry/roof/back neutral. No geometrychange.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
