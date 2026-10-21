"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='23e28a2efe2c78a1f804c8323a680c5f61acef975845978990df9fa580b3d2b6'
PALETTE=[('neutral_unknown_or_mixed','#AAA79F'),('warm_ivory_structure','#CECEC1'),('pale_silver_window_metal','#BBC6BE'),('muted_graygreen_glazing','#7F9891'),('navy_pv_panel_top','#455B70')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_roof_rear_and_high_cube_mixed_panel_wall_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint((plane(1,-32)|plane(1,-36))&xx(-68,68)&zz(3,34),1,'source_front_ivory_structure')
 paint(plane(0,68)&yy(-36,-4)&zz(3,34),1,'source_right_end_ivory_structure')
 # Both source views support front projection returns, not far rear mass.
 for x in [-34,36]:paint(plane(0,x)&yy(-36,-32)&zz(3,34),1,'source_ivory_front_setback_return')
 for x,w,y in [(-51,30,-36),(-12,39,-32),(25,29,-32),(52,27,-36)]:
  for z in [6,16,26]:
   paint(plane(1,y+1.5)&xx(x-w/2,x+w/2)&zz(z,z+5.5),3,'source_discrete_front_strip_window_back')
   for xc in np.arange(x-w/2+4,x+w/2,5):paint(box(xc-.6,xc+.6,y-1.6,y+1.4,z,z+5.5),2,'source_existing_pale_front_mullions')
 for z in [6,16,26]:
  for y in [-28,-18,-9]:paint(plane(0,67)&yy(y-3,y+3)&zz(z,z+5.5),3,'source_right_end_discrete_window_back')
 paint(box(-3.5,21.5,-43.5,-30.5,12,15),1,'source_ivory_entry_canopy_bounded_returns')
 for x in [-1,19]:paint(box(x-1.1,x+1.1,-42.6,-39.4,3,12.5),1,'source_ivory_entry_columns')
 paint(plane(1,-30.9)&xx(0,18)&zz(3.2,11.9),3,'source_entry_window_back')
 for x in [3,9,15]:paint(box(x-.6,x+.6,-34.5,-30.5,3.3,11.3),2,'source_existing_entry_mullions')
 for x,w,y,d,z in [(-28,76,-18,22,33.5),(38,46,-18,22,33.5),(-10,35,14,29,49)]:
  paint(box(x-w/2,x+w/2,y-d/2,y+d/2,z,z+2)&(norm[:,2]>.001)&(abs(norm[:,0])>.001),4,'official_aerial_verified_PV_original_sloped_tops_only_seam_floor_and_thick_sides_neutral')
 paint(hi[:,2]<=3.0001,0,'unsplit_base_not_lawn')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU General Building I original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthugeneral-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTHU official ground and 2019 EXIF aerial source photographs, uncalibrated proxies','scope':'Source-supported ivory front/right structure, pale mullions and separate graygreen window backs; official aerial verified PV upper sloped surfaces only. Incision floors, thick PV sides, unseen roof/rear and high cube mixed gray inset panel face neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
