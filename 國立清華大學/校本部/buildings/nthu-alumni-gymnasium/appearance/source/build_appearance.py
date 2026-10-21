"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='e77fbcaa88b66ab33f798d7f598ad3f90f34eef9a67334258da0479cb2c0a3b1'
PALETTE=[('neutral_unknown_or_mixed','#AAA79F'),('silver_gray_metal','#BAC1BD'),('pale_warm_gray_roof','#B5B0A7'),('dark_muted_window_louver_recess','#515B58')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_lower_entry_wall_hidden_long_lower_wall_roof_deck_rear_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-30.5)&xx(-65.5,-30.5)&zz(29,44),1,'source_high_front_silver_cladding_no_fake_corrugation_or_text')
 paint(plane(1,-29.5)&xx(-30.5,66)&zz(26,31.8),1,'source_long_upper_cladding_only_whole_triangles')
 for x in range(-24,64,8):paint(plane(1,-28.75)&xx(x-3.1,x+3.1)&zz(26,29.7),3,'source_clerestory_window_back')
 for x,z in [(-60,32),(-49,36),(-39,31),(-33,37),(-52,28),(-35,28)]:paint(plane(1,-29)&xx(x-1.1,x+1.1)&zz(z-1.1,z+1.1),3,'source_existing_round_window_back')
 for z in [12,13.7,15.4,17.1,18.8]:
  for x,w in [(-28,19),(-58,10)]:paint(plane(1,-35.4)&xx(x-w/2,x+w/2)&zz(z,z+.7),3,'source_dark_louver_groove_back_NOT_glass')
 for x in [-29,-19]:paint(box(x-1.3,x+1.3,-36.8,-34.2,3,11),1,'source_silver_gray_entry_round_column_bounded_circumference')
 for x in range(-26,64,12):paint(box(x,x+11,-27.5,35.5,31,34)&(norm[:,2]>.001),2,'source_repeated_metal_roof_upper_faces_bounded_same_system_NOT_PV')
 paint(hi[:,2]<=3.0001,0,'unsplit_base_not_paving_pattern')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU Alumni Gymnasium original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthugym-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTHU alumni/library and architect AMBI exterior photographs, uncalibrated proxies','scope':'High front silver cladding, existing round and clerestory recesses, dark louver backs, silver entry columns, repeated roof upper faces. Mixed silver/taupe lower entrance wall neutral because original faces lack boundary; hidden long lower wall, high deck and rear neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
