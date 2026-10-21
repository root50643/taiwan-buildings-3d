"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='cf2d99b0abefa670f963aa51fb23462d359e2f06f1dba9f169aeb47bd6fc7697'
PALETTE=[('neutral_unknown','#AAA79F'),('cream_yellow_tile','#C9BE9C'),('ivory_screen','#D6D7CC'),('silver_window_frames','#BFC5BF'),('muted_graygreen_glass','#81918A'),('gray_concrete_eave_canopy','#A5AAA5'),('neutral_screen_recess_NOT_glass','#7C827C')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_side_rear_roof_and_entry_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-16)&xx(-68,68)&zz(2.8,41.8),1,'source_front_cream_tile_wall')
 for x in [-67,-55,-43,14,26,38,50,62,68]:paint(box(x-.75,x+.75,-17.6,-15.8,3,42),1,'source_front_cream_tile_pilasters')
 paint(box(-33,9,-21.5,-16,15,41),2,'source_white_screen_coarsened_pattern_no_missing_tan_divider_invention')
 for x in range(-30,8,3):
  for z in range(18,40,3):paint(plane(1,-20.5)&xx(x-.8,x+.8)&zz(z,z+1.6),6,'backed_screen_hole_neutral_proxy_NOT_glazing')
 for x in [-61,-49,20,32,44,56]:
  for z in [6,19,32]:
   paint(plane(1,-15)&xx(x-4.15,x+4.15)&zz(z,z+8),4,'source_actual_window_recess_back_only')
   paint(box(x-.5,x+.5,-16.7,-15.3,z,z+8),3,'source_existing_silver_vertical_frame')
   paint(box(x-4.15,x+4.15,-16.7,-15.3,z+4,z+4.9),3,'source_existing_silver_horizontal_frame')
 paint(box(-34.5,10.5,-28,-16,14,16),5,'source_canopy_gray_sides_soffit_bounded_same_material_top')
 for x in [-32,8]:paint(box(x-1.1,x+1.1,-23.5,-18.5,3,16),1,'source_entry_cream_tile_support')
 paint((plane(1,-18.5)|plane(0,70.5))&box(-70.5,70.5,-18.5,26.5,41,43.2),5,'source_front_right_gray_eave_fascia_not_rooftop')
 paint(hi[:,2]<=3.0001,0,'unsplit_ground_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Electrical Engineering One original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntuee1-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTU official N22 historical photographs; uncalibrated material proxies','scope':'Cream front tile, coarse white backed screen with neutral recesses not glass, separate graygreen windows and silver frames, gray canopy/eave. Unknown roof, sides, rear and mixed entry back neutral. Tan divider strips absent from original screen are omitted, not newly invented.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
