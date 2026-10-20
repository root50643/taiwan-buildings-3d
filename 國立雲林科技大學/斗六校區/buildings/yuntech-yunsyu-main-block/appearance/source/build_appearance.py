"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='150e20b3d21638149eae6afd4549b72e1f1417f7a7021b0f5783f4af59160587'
PALETTE=[('neutral_unseen','#AAA79F'),('offwhite_front_structure','#D5D3C1'),('light_gray_stone_parapet','#B8BDB6'),('redbrown_open_rail','#7C3735'),('pale_yellow_upper_frames','#C7C193'),('dark_glazing_proxy','#293D3B'),('display_plinth','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_roof_stairs_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0001)&(hi[:,2]<=b+.0001)
 front=hi[:,1]<=-11.7499
 paint(front&zz(3,52)&(n[:,2]<.5),1,'registered_front_structure_offwhite_bounded_continuity')
 paint((hi[:,1]<=-25.0999)&zz(36,42),2,'existing_upper_solid_stone_parapet_and_blank_sign')
 paint((hi[:,1]<=-25.1999)&zz(3,6.6),2,'existing_low_front_stone_panels')
 # Only existing front open metal guardrail, not adjacent concrete columns.
 rail=(lo[:,1]>=-26.9001)&(hi[:,1]<=-25.0999)&zz(20.3,27)
 for x in [-66,-52.5,-31.5,-10.5,10.5,31.5,52.5,66]:
  rail &= ~((lo[:,0]>=x-1.1001)&(hi[:,0]<=x+1.1001))
 paint(rail,3,'existing_front_second_level_open_metal_rail')
 for z in [7.2,23.2,39.0]:
  for x in [-42,-21,0,21,42]:
   if z==7.2 and x==0:continue
   w=(lo[:,0]>=x-8.8501)&(hi[:,0]<=x+8.8501)&zz(z,z+9.6)
   back=w&np.all(abs(t[:,:,1]+11.75)<.00015,axis=1)
   paint(back,5,'existing_front_window_recess_back_dark_glazing')
   frame=w&(lo[:,1]>=-13.0501)&(hi[:,1]<=-11.5499)&~back
   paint(frame,4 if z>10 else 5,'existing_upper_mullion_pale_yellow' if z>10 else 'existing_lower_mullion_dark')
 paint(hi[:,2]<=3.0001,6,'display_base_not_real_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'YunTech Yunsyu Main Block original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'yunsyu-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official 2023 article facade photograph approximations, not measured material swatches','scope':'Front main block only, 2023 post-restoration source; hidden rear, roof and stairs neutral; no annex canopy.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
