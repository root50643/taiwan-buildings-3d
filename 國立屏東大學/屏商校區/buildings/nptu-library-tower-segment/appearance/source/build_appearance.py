"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='b9531e63c0c7e15bb7afae6539beddd60f06cfd4103f2b98076ea532c9a3f207'
PALETTE=[('neutral_mixed_podium_left_wall_and_unknown','#AAA79F'),('offwhite_registered_front_tower','#D2D3CA'),('muted_dark_window_proxy','#52615F'),('muted_bluegreen_top_and_cavity_glazing','#658D8C'),('brown_crown_vertical_edge','#85725D')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_podium_left_wall_entry_lower_cavity_or_unknown_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.004)&(hi[:,2]<=b+.004)
 def xx(a,b):return (lo[:,0]>=a-.004)&(hi[:,0]<=b+.004)
 def yy(a,b):return (lo[:,1]>=a-.004)&(hi[:,1]<=b+.004)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 paint(plane(1,-26)&xx(-47,47)&zz(35.1,134.2),1,'source_registered_front_white_tower_no_podium_or_side_extension')
 paint(plane(1,3)&xx(-15.5,15.5)&zz(42.2,99),1,'source_upper_white_cavity_wall_lower_opaque_screen_excluded')
 paint((plane(0,-15.5)|plane(0,15.5))&yy(-26,3)&zz(42.2,99),1,'source_white_cavity_return_walls')
 paint(plane(2,99)&xx(-15.5,15.5)&yy(-26,3),1,'source_white_cavity_soffit')
 for z in [39.5,50,60.5,71,81.5,92,102.5,113]:
  for x in np.linspace(-42.9,42.9,12):
   if abs(x)<15.6 and z<99:continue
   paint(plane(1,-24.8)&xx(x-2.6,x+2.6)&zz(z,z+6.3)&(norm[:,1]<-.0001),2,'source_discrete_front_window_back_only')
  for y in [-18,-8,2,12,22,30]:paint(plane(0,-45.65)&yy(y-3,y+3)&zz(z,z+6.3)&(norm[:,0]<-.0001),2,'source_discrete_upper_left_window_back_not_mixed_left_wall')
 for x in np.linspace(-38.5,38.5,6):paint(plane(1,-24.5)&xx(x-6.7,x+6.7)&zz(123.3,131.4)&(norm[:,1]<-.0001),3,'source_top_front_grouped_glazing_without_invented_grid')
 for y in [-17,-1,15,29]:paint(plane(0,-45.5)&yy(y-6.8,y+6.8)&zz(123.3,131.4)&(norm[:,0]<-.0001),3,'source_top_left_grouped_glazing_without_invented_grid')
 for z in [44,54.5,65,75.5,86]:
  paint(plane(1,3.4)&xx(-14,14)&zz(z,z+5.4)&(norm[:,1]<-.0001),3,'source_upper_cavity_glazing_back_lower_opaque_screen_excluded')
  paint(((plane(0,-16.8)&(norm[:,0]>.0001))|(plane(0,16.8)&(norm[:,0]<-.0001)))&yy(-24.5,1.5)&zz(z,z+5.4),3,'source_glazed_cavity_returns_actual_recess_backs')
 paint(((plane(1,-26.8)&xx(-47.8,47.8))|(plane(0,-47.8)&yy(-26.8,36.8)))&zz(134.2,135.9),4,'source_front_left_crown_vertical_brown_fascia_not_rooftop')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NPTU Library Tower Bounded Appearance original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nptutower-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NPTU official complete photos camera Original2019-06-28 and2019-06-11, modification July05/June21 separate. White registered front tower, bounded dark windows, bluegreen upper cavity/top, brown front-left crown vertical edge','scope':'Only existing tower and partial podium. Mixed lower podium and entrance, continuous left wall spanning white and brown bands, lower opaque cavity screen, roof/right/rear all neutral. No fine grids or thin mortar invented. Original triangles and STL unchanged.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
