"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='f4043043b3db240f2543ec085bc30660fa1ff9470aef58caad9d15b093f19a51'
PALETTE=[('neutral_mixed_walls_and_unknown','#AAA79F'),('pale_golden_bamboo_roof','#CBB184'),('dark_brown_roof_battens','#75604A'),('muted_dark_window','#60716A'),('gray_concrete_apron','#A1A69F')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'walls_mixed_bamboo_dark_horizontal_bands_or_gray_plinth_and_unknown_ends_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 upward=normal[:,2]>1e-8
 paint(box(-68,68,-58.5,-23.5,27,36)&upward,1,'official_aerial_front_wing_bamboo_roof_slope')
 paint(box(-59,21,22,58,28,37)&upward,1,'official_aerial_rear_upper_bamboo_roof_slope')
 paint(box(-58.5,32.5,9.5,34.5,24,31)&upward,1,'official_aerial_rear_lower_bamboo_roof_slope')
 paint(box(44,66,-43.5,53.5,25,31)&upward,1,'official_aerial_link_bamboo_roof')
 angle=np.deg2rad(18);q=t.copy();q[:,:,0]=(t[:,:,0]-34)*np.cos(angle)+(t[:,:,1]+7)*np.sin(angle);q[:,:,1]=-(t[:,:,0]-34)*np.sin(angle)+(t[:,:,1]+7)*np.cos(angle)
 paint(np.all(abs(q[:,:,0])<=20.003,axis=1)&np.all(abs(q[:,:,1])<=14.003,axis=1)&zz(24,31)&upward,1,'official_aerial_rotated_projection_roof_only')
 for y,z in [(-41,35.5),(-50,31),(-32,31)]:paint(box(-67,67,y-.6,y+.6,z,z+1),2,'source_original_front_roof_brown_ridge_and_batten')
 for y,z in [(40,36.5),(31,32),(49,32)]:paint(box(-58,20,y-.6,y+.6,z,z+1),2,'source_original_rear_roof_brown_ridge_and_batten')
 for x in [-55,-42,-23,-9,11,29,47,59]:paint(plane(1,-54)&xx(x-2.5,x+2.5)&zz(10,17),3,'source_actual_discrete_front_window_back_no_fake_frame')
 paint(box(-38,10,-22.5,-7.5,3,4.5),4,'source_existing_gray_courtyard_apron')
 paint(hi[:,2]<=3.0001,0,'unsplit_ground_not_all_grass')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU Bamboo House original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthubamboo-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTHU official 2023 completed aerial and ground photographs, uncalibrated proxies','scope':'Source-supported golden roof slopes, brown original roof battens, actual front window backs and concrete apron. Walls stay neutral because dark horizontal bands and courtyard gray plinth lack original boundaries; no invented bamboo textures or frames.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
