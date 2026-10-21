"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='eca2a97497c30c0ace8acd6384142b8937507caf058445039234cb8da448356f'
PALETTE=[('neutral_unknown_or_mixed','#AAA79F'),('cream_tiled_panels','#CECBB6'),('gray_concrete_ribs_and_wave_ends','#8D9592'),('silver_window_frames','#C7CECA'),('muted_graygreen_glass','#84968F'),('dark_gray_canopy','#626B67')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_roof_rear_right_side_and_unregistered_mixed_walls_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 for x in [-52,-26,26,52]:paint(box(x-5.5,x+5.5,-28,-26,3,46),1,'source_cream_broad_panel_visible_face_and_bounded_short_returns')
 for x in [-65,-39,-13,13,39,65]:paint(box(x-.9,x+.9,-27.95,-25.45,3,52),2,'source_gray_front_vertical_rib')
 paint(plane(1,-28)&zz(49,55.5),2,'source_gray_wave_front_end_only_NOT_unknown_curved_roof_top')
 for x in [-52,-26,0,26,52]:
  for w in [x-8.6,x+8.6]:
   for z in [6,21,36]:
    paint(plane(1,-24.75)&xx(w-3.1,w+3.1)&zz(z,z+10),4,'source_actual_discrete_front_window_back')
    paint(box(w-.5,w+.5,-26.5,-24.7,z,z+10),3,'source_original_silver_window_vertical_frame')
    paint(box(w-2.9,w+2.9,-26.5,-24.7,z+6,z+6.9),3,'source_original_silver_window_crossbar')
 paint(plane(1,-24.5)&xx(-7.5,7.5)&zz(4,17),4,'source_entry_glazed_back')
 for x in [-5,0,5]:paint(box(x-.45,x+.45,-26.6,-24.6,4,17),3,'source_entry_silver_original_strips')
 paint(box(-15,15,-34,-24,17,18.7),5,'source_dark_gray_canopy_bounded_same_material_top')
 # Only left oblique side positively registered; other side remains neutral.
 for y in [-17,-3,11,25,35]:
  paint(box(-66.1,-63.9,y-1,y+1,3,51),2,'source_left_oblique_existing_gray_side_pier')
  for z in [8,23,38]:paint(plane(0,-64)&yy(y+1,y+7)&zz(z,z+9),4,'source_left_oblique_discrete_side_window_back_without_invented_frames')
 paint(box(-16,16,-38.85,-32.95,2.8,5.6),2,'source_gray_entry_steps')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU ESOE Five Wave Entrance original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntuesoe-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTU official 2022 front and 2010 E61 photos, uncalibrated proxies','scope':'Five-wave entry segment only: cream panels, gray front wave ends and ribs, silver frames, subdued glass, dark canopy with bounded material top. Unknown curved roof top, rear and unregistered side/walls neutral. Vent recesses NOT glass.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
