"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='01393ae4416f73bd5306842c6d2dfde4b15b3fd301674fe2a2a53829900ba000'
PALETTE=[('neutral_unseen','#AAA69D'),('pale_columns_pediment','#C9CBC6'),('gray_stone_front','#989C99'),('gray_stairs','#828580'),('dark_openings_proxy','#394246'),('display_plinth','#8A8C88')]
def classify(tri):
 t=tri.copy();t[:,:,:2]/=(150/68);t[:,:,2]=(t[:,:,2]-2.4)/(150/68)
 lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_west_dome_court_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0001)&(hi[:,2]<=b+.0001)
 def plane(axis,x):return np.all(abs(t[:,:,axis]-x)<.0001,axis=1)
 # View is the east (+X) entrance only. Do not mirror colors to west portico.
 paint((c[:,0]>0)&(n[:,0]>.3)&zz(5.25,16.85),2,'east_visible_stone_facade_proxy')
 paint(plane(0,19)&zz(-.04,4.6),2,'east_low_wing_front_continuity_proxy')
 # Front columns including their existing simplified capitals and round bases.
 for y in np.linspace(-6.55,6.55,6):
  mask=(lo[:,0]>=16.7499)&(hi[:,0]<=18.5501)&(lo[:,1]>=y-.9001)&(hi[:,1]<=y+.9001)&zz(5.15,16.65)
  paint(mask,1,'east_six_existing_columns_pale_stone')
 # Only outward-facing front pediment/entablature planes; roofs/dome stay neutral.
 paint((lo[:,0]>=18.7999)&(n[:,0]>.9)&zz(16.4,22.15),1,'east_front_pediment_entablature_pale')
 # The original clock recess remains blank pale stone, no hands or numerals.
 paint((lo[:,0]>=18.5499)&(hi[:,0]<=19.2501)&(lo[:,1]>=-.7001)&(hi[:,1]<=.7001)&zz(19.52,20.92),1,'existing_clock_recess_blank_pale_no_details')
 # East terrace outer balustrade only, not hidden courtyard or west rails.
 paint((lo[:,0]>=18.5499)&(hi[:,0]<=19.2001)&zz(5.05,6.25),1,'east_outer_terrace_railing_continuity_proxy')
 # Dark only on the backed east entrance/window planes, no painted shadows.
 paint(plane(0,13.65)&zz(5.65,14.7),4,'existing_east_window_and_door_recess_backs')
 # Low wing arch backs are only accepted on the east outer facade.
 paint(plane(0,18.65)&zz(.35,4.1),4,'existing_east_low_wing_arch_backs')
 # All coarsened east stair tread and riser faces, not an exact step count claim.
 paint((lo[:,0]>=18.6499)&(hi[:,0]<=27.6651)&(lo[:,1]>=-8.1001)&(hi[:,1]<=8.1001)&zz(-.03,5.2),3,'existing_east_stairs_gray')
 paint((lo[:,0]>=18.6499)&(hi[:,0]<=27.6701)&(abs(c[:,1])>=8.1999)&(abs(c[:,1])<=9.0001)&zz(-.03,5.75),2,'existing_east_stair_cheek_walls')
 paint(tri[:,:,2].max(axis=1)<=2.4001,5,'display_base_not_real_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'TTU Shangzhi Hall original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ttu-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated university-credited entrance photograph approximations, not measured material swatches','scope':'East entrance only; dome, west portico and courts neutral. Outer east low-wing front and rail colors use bounded continuity extrapolation.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
