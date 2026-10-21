"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='8c5e7abbfd63eb009bb1a0ea1d8cb471c804ed099a6b1b11e659c9d7ea0ccf4e'
PALETTE=[('neutral_unknown_or_mixed_passage','#AAA79F'),('warm_gray_concrete','#999C94'),('slate_gray_roof','#727E81'),('pale_olive_silver_frames','#B0B9A6'),('muted_graygreen_glazing','#758C85')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_rear_walls_and_mixed_lower_passage_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-17)&xx(-58,58)&zz(3,66),1,'source_front_gray_structure_excluding_recess_backs')
 paint(plane(0,58)&yy(-17,23)&zz(3,66),1,'source_visible_right_end_gray_structure')
 for x in [-54,-28,0,28,54]:paint(box(x-1.8,x+1.8,-27.5,-10.5,3,27),1,'source_gray_front_piers_bounded_returns')
 for x in [-42,-12,18]:paint(box(x-8,x+8,-25,-17,3,28),1,'source_existing_gray_diagonal_buttress')
 paint(box(-63,64,-31,24,26,30),1,'source_wrapping_concrete_balcony_bounded_continuous_slab')
 paint(box(-63,63,-23.5,25.5,47,49.8),1,'source_upper_concrete_band_bounded_continuity')
 paint(plane(1,-14.75)&xx(-56,56)&zz(32,45),4,'source_mid_front_discrete_glazing_back')
 paint(plane(1,-14.5)&xx(-55.5,55.5)&zz(51,64),4,'source_upper_front_window_back_between_deep_fins')
 paint(plane(0,55.8)&yy(-15,16)&(zz(32,45)|zz(51,64)),4,'source_visible_end_glazing_back')
 for x in [-53,-30,-7,16,39,54]:paint(box(x-1.1,x+1.1,-21,-15,31,46),3,'source_existing_middle_olive_silver_mullions')
 for z in [36.5,41.5]:paint(box(-56,56,-20.5,-15.5,z,z+1.2),3,'source_existing_horizontal_window_grid')
 for y in [-12,-3,6,15]:paint(box(55.5,60.5,y-.6,y+.6,31,46),3,'source_existing_end_window_grid')
 for x in [-54,-39,-24,-9,6,21,36,51]:paint(box(x-1.15,x+1.15,-24.5,-13.5,49,66.5),1,'source_gray_upper_sun_fins_NOT_glass')
 for y in [-11,1,13]:paint(box(55.5,60.5,y-.75,y+.75,50,65),1,'source_gray_end_vertical_fins')
 # Continuous modeled roof slopes, both slopes visible at photographed end;
 # no charcoal gable fill or fictitious detailed metal ribs.
 paint(box(-65,65,-28,29,64,82)&(norm[:,2]>0.01),2,'source_gray_roof_upper_slopes_bounded_same_system_across_five_original_strips')
 for i in range(10):paint(box(58.5,67.5,16-i*3.7,20-i*3.7,3,6+i*2.4),1,'source_gray_end_stairs')
 paint(box(65.75,68.25,-20,20,3,18),1,'source_gray_stair_cheek')
 paint(hi[:,2]<=3.0001,0,'unsplit_base_not_grass_or_stone_texture')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU Wang Chou Literature Museum original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthuwang-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTHU daylight long-elevation/end/lake photographs, uncalibrated proxies','scope':'Gray concrete piers, fins and continuous bands; pale olive-silver grids and discrete upper window backs; slate roof upper slopes bounded across original five strips. Lower passage mixed backing and unregistered rear walls neutral. Original flattened terrain and simplified roof kept.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
