"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='c100700000dfb445be70dab4615a2654875ba3de9ae63e0f0c1c096bec2f6d74'
PALETTE=[('neutral_unverified_surfaces_and_base','#AAA79F'),('muted_gray_blue_glazing','#647F85'),('pale_silver_window_crossbars','#C2C6C1'),('pale_warm_gray_front_tiles','#BEB7AE')]
def classify(tri):
 t=tri;lo=t.min(1);hi=t.max(1);eps=.00015
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'neutral_unverified_roof_rear_sides_low_mixed_bays_or_boundary',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def span(i,a,b):return (lo[:,i]>=a-eps)&(hi[:,i]<=b+eps)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<eps,axis=1)
 # Only original front-facing planar tile surfaces. Unknown side/roof surfaces neutral.
 front=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])[:,1]<-eps
 paint(front & span(0,-64,64)&span(1,-46,-29)&span(2,3,107.8),3,'photo_front_opaque_tile_full_face_only')
 # Actual individual window backs; broad y=-29 facade backing is NOT glass.
 for x in range(-44,45,11):
  for z in [31,42,53,64,75,86]:
   box=span(0,x-4.2,x+4.2)&span(2,z,z+8)
   paint(box&plane(1,-27)&span(0,x-4.1,x+4.1)&span(2,z,z+7.8),1,'discrete_grid_window_back_repeated_material_inference_upper_rows')
   bar=(span(0,x-.5,x+.5)|span(2,z+3.8,z+4.7))
   paint(box&bar&span(1,-30.5,-26.5),2,'existing_grid_crossbar_full_face')
 for x,h,w in [(-33,18,19),(-16,30,18),(0,18,19),(16,30,18),(33,18,19)]:
  paint(plane(1,-43.5)&span(0,x-(w-4)/2,x+(w-4)/2)&span(2,23,23+h-5),1,'photo_upper_entry_rectangular_window_back')
 radial=t[:,:,0]**2+(t[:,:,2]-48)**2
 paint(plane(1,-44)&np.all(radial<=36+eps,axis=1),1,'photo_round_window_recessed_disk_only')
 paint(span(1,-46,-44)&((span(0,-.5,.5)&span(2,41,55))|(span(0,-7,7)&span(2,47.5,48.5))),2,'photo_original_round_window_crossbars')
 # Ground-level lateral rectangles lack actual opaque infill boundaries: all stay neutral.
 paint(span(2,0,22)&span(1,-55,-29),0,'ground_level_mixed_opaque_glass_and_steps_held_neutral')
 paint(hi[:,2]>=97-eps,0,'top_band_roof_and_crossing_faces_held_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCU Main Library limited facade original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ncu-main-library-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'2018-09-27 EXIF front photograph and official disaster-plan identity crosscheck; uncalibrated display proxies','scope':'Whole-face front tiles, window backs and existing crossbars. Upper repeated grid glazing is bounded material inference. Ground mixed bays, top band, sides, roof and rear remain neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
