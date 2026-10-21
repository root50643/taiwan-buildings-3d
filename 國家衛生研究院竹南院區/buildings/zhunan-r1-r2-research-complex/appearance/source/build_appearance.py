"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='b8188b578e39b4768520e406dd6943f935d46a8721bdd8e9705c56e18bcf3b80'
PALETTE=[('neutral_unknown','#AAA79F'),('pale_gray_cladding','#C9CCC8'),('gray_sunshade_frames','#949EA3'),('muted_blue_glazing_proxy','#496D83'),('warm_sandstone_galleries','#B99579')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1)
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_farend_roof_centralrear_ground_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.003,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 for sign in [-1,1]:
  cx=sign*48.5
  paint(plane(1,-62)&xx(cx-18,cx+18)&zz(2.8,60.4),1,'documented_near_end_pale_cladding')
  for cy in [-33.5,33.5]:
   paint((plane(0,sign*66.5)|plane(0,sign*30.5))&yy(cy-28.5,cy+28.5)&zz(2.8,60.4),1,'documented_outer_and_courtyard_pale_grid_walls')
   for y in np.linspace(cy-20,cy+20,7):
    for z in np.arange(7.2,51,5.7):paint(plane(0,sign*65.55)&yy(y-2.3,y+2.3)&zz(z,z+4.3),3,'outer_existing_discrete_pane_back')
   for y in np.linspace(cy-20,cy+20,6):
    for z in [10.2,21.6,33,44.4]:paint(plane(0,sign*31.325)&yy(y-2.9,y+2.9)&zz(z,z+9),3,'courtyard_existing_tall_pane_back')
   for z in np.arange(6.4,52,5.7):paint(box(min(sign*66.6-.425,sign*66.6+.425),max(sign*66.6-.425,sign*66.6+.425),cy-23.5,cy+23.5,z,z+.85),2,'existing_outer_gray_shading_rail')
  for z in np.arange(7.1,51,5.7):paint(plane(0,sign*63.8)&yy(-2.9,2.9)&zz(z,z+4.3),3,'outer_joint_existing_window_back')
  for z in [10.2,21.6,33,44.4]:paint(plane(0,sign*31.325)&yy(-59.6,-56.4)&zz(z,z+8.8),3,'near_courtyard_return_window_back')
  for x in [cx-7.6,cx-2.5,cx+2.5,cx+7.6]:
   for z in np.arange(7.2,49,4.5):paint(plane(1,-61.1)&xx(x-1.975,x+1.975)&zz(z,z+3.4),3,'near_end_existing_blue_pane_back')
  paint(plane(1,-61.1)&xx(cx-11.5,cx+11.5)&zz(54,57),3,'near_end_upper_clerestory')
  for z in np.arange(6.4,50,4.5):paint(box(cx-12.9,cx+12.9,-63.1,-61.6,z,z+.85),2,'source_gray_front_horizontal_louver_not_glass')
  for x in [cx-1.4,cx+1.4]:paint(box(x-.45,x+.45,-63,-61.5,6.4,49.8),2,'source_gray_front_vertical_rib')
  paint(box(cx-13.7,cx+13.7,-63.3,-61.5,50.5,51.8),2,'source_front_glazing_crown_edge')
  for y in np.arange(-64.5,38,8.2):paint(box(sign*23-.9,sign*23+.9,y-.9,y+.9,3.5,12.9),4,'source_low_sandstone_gallery_pier')
  paint(box(sign*23-1.05,sign*23+1.05,-65.45,38.05,12,13.5),4,'source_low_sandstone_gallery_beam')
 paint(plane(1,-29.5)&xx(-13.5,13.5)&zz(2.8,53.5),1,'source_center_head_pale_jambs')
 for x in [-7.3,-2.45,2.45,7.3]:
  for z in np.arange(8,48,5):paint(plane(1,-28.65)&xx(x-1.9,x+1.9)&zz(z,z+3.9),3,'center_head_existing_glazing_back')
 for x in [-1,1]:paint(box(x-.425,x+.425,-30.25,-29.05,9.5,49),2,'center_gray_vertical_ribs')
 paint(plane(1,-28.8)&xx(-2.05,2.05)&zz(3.2,8.8),3,'entry_existing_recess_proxy')
 for sign in [-1,1]:
  for x in [sign*17.8,sign*23.1,sign*28.2]:
   for z in np.arange(8,39,5.6):paint(plane(1,-6.9)&xx(x-1.85,x+1.85)&zz(z,z+4.35),3,'connector_existing_discrete_pane_back')
 paint(hi[:,2]<=3.0001,0,'original_ground_base_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NHRI Zhunan R1 R2 Research Complex original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nhrir12-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Association named research-building photo and Futsu contractor exterior; uncalibrated proxies','scope':'Pale cladding, blue discrete glazing backs, gray integral louvers and ribs, low sandstone galleries. Original simplified pane counts retained; far ends, rooftop and central rear neutral. No laboratory, equipment or security details.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
