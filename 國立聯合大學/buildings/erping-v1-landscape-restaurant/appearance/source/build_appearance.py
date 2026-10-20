"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='80c9e2f5243a745949db2b29b20fa078832102d71e3dd9d06c51f88537e1b522'
PALETTE=[('neutral_unseen','#AAA79F'),('observed_brick','#A6634E'),('silver_gray_roof','#9DA5A4'),('muted_green_frame','#557B68'),('muted_gray_green_glazing','#526F70'),('gray_bands_steps','#B2B5AE')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_rear_or_unresolved_mixed_frame_and_pedestal_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0004)&(hi[:,2]<=b+.0004)
 def xx(a,b):return (lo[:,0]>=a-.0004)&(hi[:,0]<=b+.0004)
 def yy(a,b):return (lo[:,1]>=a-.0004)&(hi[:,1]<=b+.0004)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.0004,axis=1)
 def box(x,y,z,w,d,h):return xx(x-w/2,x+w/2)&yy(y-d/2,y+d/2)&zz(z-h/2,z+h/2)
 paint(plane(1,-13)&xx(-37,63)&zz(2.3,19.5),1,'observed_lower_front_brick_wall_not_upper_glass_facade')
 paint(plane(0,63)&yy(-13,21)&zz(2.3,37.3),1,'observed_right_short_end_brick_wall')
 paint(plane(1,-15)&xx(-65.5,-38.5)&zz(2.3,20.8),1,'observed_pavilion_lower_front_brick_wall')
 # Only existing recess surfaces; broad upper facade remains neutral because
 # the real slender green frame cannot be represented by its thick solid piers.
 for x in [-28,-8,12,32,52]:
  for z,w,h in [(6.5,11,9.5),(24,17,10)]:
   region=xx(x-w/2,x+w/2)&yy(-13.0004,-12.3996)&zz(z,z+h)
   paint(region,3,'existing_window_reveal_green_proxy_not_added_thin_frame')
   paint(region&plane(1,-12.4),4,'existing_front_window_recess_back_glazing')
 for y in [-6,5,15]:
  region=xx(62.2996,63.0004)&yy(y-3.75,y+3.75)&zz(24,34)
  paint(region,3,'existing_right_window_reveal_green')
  paint(region&plane(0,62.3),4,'existing_right_window_back_glazing')
 for z in [22,35]:paint(box(13,-14.6,z+.55,105,1.6,1.1),5,'existing_front_horizontal_band_gray')
 paint(box(13,-15,20.8,105,10,2.6)&(n[:,1]<-.1),5,'existing_arcade_front_floor_edge_gray')
 paint(zz(37,48)&(n[:,2]>.2),2,'existing_main_and_pavilion_roof_silver_gray_bounded_same_sheet_material')
 paint(plane(0,67.5)&zz(37,47),5,'observed_right_gable_pale_gray')
 paint(xx(-67,-30)&yy(-30.6,-19.5)&zz(2.4,21.1)&(n[:,2]>.9),5,'existing_stair_treads_gray_not_fake_metal_railings')
 paint(hi[:,2]<=2.4001,0,'neutral_display_base_not_site_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU Erping V1 Landscape Restaurant original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuuv1-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official V1 complete photo1; uncalibrated appearance proxies','scope':'Source-supported lower brick and right end, silver roofs with bounded same-sheet-material extrapolation, original discrete glazing and green reveals, gray bands/treads. Thick upper solid piers and unsegmented column pedestals remain neutral; no geometry changes or fake slender frames.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
