"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='e6259387b93dfa3af0654f46b6c89de252d3088d228e12167cd4f4329c489be0'
PALETTE=[('neutral_unknown_or_passage','#AAA79F'),('cool_offwhite_tile_infill','#CED1CB'),('warm_pale_gray_stone_grid','#B5B4A9'),('muted_dark_window_proxy','#57615B')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_roof_planes_rear_right_and_central_passage_back_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-34)&xx(-65.5,68.5)&zz(3,77),1,'color_source_front_cool_white_tile_field')
 paint(plane(0,-65.5)&yy(-34,48)&zz(3,77),1,'color_source_left_tile_field')
 for z in [6,16,26,36,46,56,66]:
  for x in [-59,-47,-10,-.5]:paint(plane(1,-32.5)&xx(x-2.6,x+2.6)&zz(z,z+7.9),3,'source_original_arch_window_back_dark_proxy_no_added_frame')
  for y in [-24,-10,4,18,32,43]:paint(plane(0,-64)&yy(y-3.5,y+3.5)&zz(z,z+6),3,'source_left_rectangular_window_back_proxy')
 for z in [6,16,26]:
  for x in [12,24,36,48,60]:paint(plane(1,-32.5)&xx(x-2.6,x+2.6)&zz(z,z+7.9),3,'source_low_front_arch_window_back_proxy')
 for x in [12,24,36,48,60]:paint(plane(1,-32.5)&xx(x-4,x+4)&zz(34,39),3,'source_low_top_rectangular_window_back')
 for x in [-65,-53,-41,-16,-4,7,19,31,43,55,67]:paint(box(x-.7,x+.7,-36.5,-32.5,3,77 if x<5 else 42),2,'source_pale_gray_projected_vertical_grid')
 for z in [13,23,33,43,53,63,73]:
  paint(box(-65.5,3.5,-36.5,-32.5,z,z+1.4),2,'source_high_front_gray_horizontal_grid')
  if z<40:paint(box(3.5,68.5,-36.5,-32.5,z,z+1.4),2,'source_low_front_gray_horizontal_grid')
  paint(box(-67.75,-64.25,-34,48,z,z+1.4),2,'source_left_horizontal_gray_grid')
 for y in [-32,-18,-4,10,24,38,47]:paint(box(-67.75,-64.25,y-.7,y+.7,3,77),2,'source_left_vertical_gray_grid')
 for z in [31,45,59,73]:paint(box(-35.5,-20.5,-37.75,-30.25,z,z+2),2,'source_central_open_passage_floor_dividers_NOT_glass')
 flatup=(norm[:,2]>.001)&(abs(norm[:,0])+abs(norm[:,1])<.001)
 for x,y,z,w,d,h in [(-52,-19,77,25,27,19),(-6,-19,77,22,27,12),(-52,33,77,25,25,12),(45,-16,42,36,25,16)]:
  paint(box(x-w/2-2.5,x+w/2+2.5,y-d/2-3.5,y+d/2+3.5,z,z+h+1.5)&~flatup,2,'source_pavilion_posts_beams_rolled_lips_bounded_material_continuity_flat_tops_neutral')
 for x,w in [(-20,44),(43,43)]:
  for xc in [x-w/2+3,x+w/2-3]:paint(box(xc-1.25,xc+1.25,-47,-37,3,29),2,'source_gray_portico_posts')
  paint(box(x-w/2,x+w/2,-49.5,-31.5,27.5,32.5)&~flatup,2,'source_gray_portico_rolled_lip_and_soffit_flat_top_neutral')
 paint(hi[:,2]<=3.0001,0,'unsplit_base_not_pool_or_lawn')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU Physics Building original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthuphysics-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Architect color photographs only for palette; monochrome photographs used for shape only; uncalibrated historical proxies','scope':'Cool white front/left infill, warm pale gray projected grids/pavilions/porticoes, muted discrete window backs. Pavilion voids and central passage not glass; flat roof planes, rear/right unregistered faces neutral. Original heavy rolled lips and simplified arch/frame geometry retained.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
