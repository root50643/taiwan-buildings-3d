"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='44fe0094b484e6bc3f910b8db771a2cd0744b69dc8b86ad2686f760ee0bf1179'
PALETTE=[('neutral_mixed_or_unknown','#AAA79F'),('upper_buff_orange_brick','#B78B6D'),('gray_aggregate_bands','#999B8F'),('silver_white_window_frames','#C8D0C8'),('muted_graygreen_glass','#8A9B96')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_ground_top_fascia_portico_columns_deep_upper_bays_and_unseen_sides_rear_roof_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 for a,b in [(23.5,40),(43.5,60)]:paint(plane(1,-20.5)&xx(-68,68)&zz(a,b),1,'source_upper_brick_only_inside_existing_horizontal_material_boundaries')
 for z in [20,40,60]:paint(box(-68.5,68.5,-21.8,-19.8,z,z+3.5),2,'source_existing_gray_aggregate_horizontal_band')
 for x in [-68,-52,-20,0,20,52,68]:paint(box(x-.7,x+.7,-21.6,-19.8,3,82),2,'source_existing_gray_aggregate_vertical_strip')
 for z in [25,45]:
  for x in [-9,9]:paint(plane(1,-19)&xx(x-2.25,x+2.25)&zz(z,z+12),4,'source_narrow_center_window_back')
 for x in [-8,8]:
  paint(plane(1,-19)&xx(x-5.5,x+5.5)&zz(65,77),4,'source_center_top_window_back')
  paint(box(x-.5,x+.5,-20.6,-18.6,65,77),3,'source_original_center_top_vertical_frame')
  paint(box(x-5.3,x+5.3,-20.6,-18.6,73,73.9),3,'source_original_center_top_horizontal_frame')
 for z in [5,25,45]:
  for x in [-60,-45,-31,31,45,60]:
   paint(plane(1,-19)&xx(x-3,x+3)&zz(z,z+12),4,'source_discrete_side_window_back_not_solid_wall')
   paint(box(x-2.8,x+2.8,-20.6,-18.6,z+8,z+8.9),3,'source_existing_side_window_horizontal_frame')
 for x,w in [(-60,9),(60,9),(-48,6),(48,6)]:
  paint(plane(1,-19)&xx(x-w/2,x+w/2)&zz(65,77),4,'source_top_end_window_back')
  if abs(x)==60:paint(box(x-.5,x+.5,-20.6,-18.6,65,77),3,'source_top_end_original_vertical_frame')
 for x in [-31,31]:paint(box(x-9,x+9,-22,-20,62,64),2,'source_existing_deep_bay_gray_sill_back_stays_neutral')
 paint(plane(1,-19)&xx(-14.5,14.5)&zz(3,22),4,'source_entry_glazed_back_only')
 for x in [-10,-5,5,10]:paint(box(x-.5,x+.5,-20.6,-18.6,3,22),3,'source_existing_entry_vertical_frame')
 paint(box(-25,25,-39.5,-18.5,25,28.5),2,'source_gray_portico_cap_bounded_same_material_top')
 paint(box(-23,23,-37.25,-32.75,20,27),2,'source_gray_arch_beam_open_arch_NOT_glass')
 # Full portico columns remain neutral: source brick body plus gray foot is inseparable.
 for x in [-21,21]:paint(box(x-2.5,x+2.5,-37.5,-32.5,3,26),0,'mixed_brick_and_gray_foot_portico_column_neutral')
 paint(hi[:,2]<=3.0001,0,'original_unsplit_ground_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Language Front original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntulang-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTU CLD official front/oblique and 2010 N74 photos, uncalibrated proxies','scope':'Only two original fully bounded upper brick strips; gray structural bands, separate windows/frames, gray canopy/arch. Mixed groundwall and portico columns, upper fascia, deep upper alcoves, unseen sides/rear/roof neutral. No ivy or material-boundary subdivision.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
