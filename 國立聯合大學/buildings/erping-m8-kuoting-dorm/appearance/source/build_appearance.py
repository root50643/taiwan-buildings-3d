"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='99b86acd48bf9dbb4065d9976e1d4b82fc9d2cb3435280a741260f3f70b4299c'
PALETTE=[('neutral_unknown','#AAA79F'),('warm_ochre_brick','#B5A28A'),('silver_metal_frame_roof_proxy','#9FA8AA'),('muted_gray_green_glazing','#6D8784'),('pale_mint_upper_glazing','#9CB9B3'),('gray_steps_and_low_annex_roof','#818787')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_back_left_or_unsplit_mixed_surface_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.003,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-16)&xx(-64,64)&zz(8,76),1,'observed_front_ochre_brick')
 paint(plane(0,64)&yy(-16,46)&zz(8,76),1,'observed_right_wall_ochre_brick')
 paint(box(-63,-25,-31.5,-12.5,8,36),1,'observed_low_annex_brick')
 paint(box(-63,-25,-31.5,-12.5,30,36)&(n[:,2]>.7),5,'annex_roof_gray_not_uniform_green_weathering')
 for x in np.linspace(-59,-29,7):
  for z,h in [(15,6),(26,4)]:paint(plane(1,-30.5)&xx(x-1.35,x+1.35)&zz(z,z+h),3,'low_annex_discrete_window_back')
 for row in range(5):
  z=11+row*12
  for x in [-56,-48,-40,-32,28,36,44,52,60]:
   if row<2 and x< -25:continue
   paint(plane(1,-15)&xx(x-2.5,x+2.5)&zz(z,z+7.5),3,'front_existing_discrete_pane_back')
  for y in [-9,0,9,18,27,36,43]:paint(plane(0,63)&yy(y-2.5,y+2.5)&zz(z,z+7.3),3,'right_existing_discrete_pane_back')
 # Tall strip mixes opaque spandrels and panes without matching original segmentation.
 paint(plane(1,-15)&xx(-21,-11)&zz(11,69),0,'tall_strip_mixed_spandrel_and_glass_unsplit_neutral')
 for z in np.arange(13,70,7):paint(box(-21.2,-10.8,-17.1,-14.9,z,z+.9),2,'existing_tall_strip_silver_transom')
 paint(box(-16.45,-15.55,-17.1,-14.9,10,69),2,'existing_tall_strip_silver_mullion')
 paint(box(-10,20,-18.5,-15.5,22,57),1,'central_lattice_brick_not_metal')
 for x in np.linspace(-7.2,17.2,8):
  for z in np.linspace(24,53,7):paint(plane(1,-17.6)&xx(x-1.175,x+1.175)&zz(z,z+3.2),3,'central_square_existing_pane_back')
 paint(box(-10.5,20.5,-23,-15,20.5,22.1),1,'blank_entry_sign_lintel_no_gold_letters')
 paint(box(-11.25,-8.75,-21.5,-16.5,8,21)|box(18.75,21.25,-21.5,-16.5,8,21),1,'existing_brick_entry_side_supports')
 paint(plane(1,-12.9)&xx(-7,17)&zz(9,19),3,'inner_door_pane_proxy_not_whole_portico')
 paint(box(-12,24,-46,-15.5,2.3,8),5,'existing_gray_steps_and_retaining_walls')
 paint(zz(75.7,98),2,'upper_metal_frame_and_continuous_roof_silver_proxy_PV_gaps_not_in_mesh')
 for x in np.linspace(-59,59,18):
  rz=float(np.interp(abs(x),[0,22,45,66],[98,97,94,89]))
  paint(plane(1,-15)&xx(x-2.3,x+2.3)&zz(78,rz-1.8),4,'upper_front_existing_mint_pane_back')
 for y in np.linspace(-10,40,9):paint(plane(0,63)&yy(y-2.2,y+2.2)&zz(78,85.4),4,'upper_right_existing_mint_pane_back')
 paint(plane(1,46)&zz(75.7,87.2),0,'unseen_upper_back_wall_neutral')
 paint(hi[:,2]<=2.4001,0,'neutral_original_unsplit_base')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU M8 Kuoting Dormitory original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuum8-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official M8 complete front, aerial and close entrance photographs; uncalibrated proxies','scope':'Ochre front/right brick, central brick lattice discrete glazing and mint upper panes. Tall mixed strip backing neutral, existing frames silver. Aerial confirms real PV but continuous mesh lacks array gaps: whole roof conservative silver proxy, not fabricated PV coverage. Unknown rear/left neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
