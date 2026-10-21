"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='61d36d81b68a3f166ad27fe3adc82be30cb954c1d03a5adb803678017adfca5f'
PALETTE=[('neutral_unknown','#AAA79F'),('pale_stone_columns_and_tower','#C4C8C5'),('cool_gray_fascia_and_rails','#9EA7AC'),('warm_sandstone_screen','#B99579'),('dark_glazing_proxy','#53666F')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_side_roof_or_ground_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.003,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(box(-62,70,-34.6,-34.25,24,34.8),2,'documented_cool_gray_front_tile_fascia')
 paint(plane(1,-34.5)&xx(-62,70)&zz(2.8,24),1,'front_pale_frame_not_whole_dark_wall')
 paint(plane(1,-33)&xx(-54,62)&zz(7,24),4,'existing_entrance_glazed_recess_back')
 for x in [-49,-43,-8,-2,34,40,58]:paint(box(x-1.35,x+1.35,-35.75,-33.05,5,24),1,'source_pale_integral_round_column')
 for z in [24.4,27.5]:paint(box(-56.5,64.5,-36.2,-33.8,z,z+1.25),2,'source_gray_horizontal_sunshade_rail')
 for x in np.arange(-59,65,11):
  if x!=7:paint(box(x-1.4,x+1.4,-44.2,-40.8,5.8,22.8),3,'foreground_warm_stone_pier')
 paint(box(-63.5,67.5,-44.2,-40.8,22,24.5),3,'foreground_warm_stone_beam')
 paint(box(22,66,-45,-33,3,12)&(abs(n[:,2])<.1),3,'terrace_vertical_stone_faces_only')
 paint(box(1,17,-46.825,-33.975,3,11.64),3,'source_sandstone_stair_steps')
 # Broad opposite-side contractor image supports tall rear grid and side glazing.
 paint(plane(1,44.5)&xx(-65.5,-12.5)&zz(2.8,63.8),1,'contractor_documented_tall_rear_pale_wall')
 paint(plane(0,-65.5)&yy(-4.5,44.5)&zz(2.8,63.8),1,'contractor_documented_tall_left_pale_wall')
 paint(plane(1,-4.5)&xx(-65.5,-12.5)&zz(34.8,63.8),1,'association_documented_front_tower_pale_wall')
 for ix in range(6):
  for iz in range(6):
   x=-55+ix*6.4;z=17+iz*5.3;paint(plane(1,43.35)&xx(x-2.7,x+2.7)&zz(z,z+4.35),4,'rear_grid_existing_pane_back')
 for x in np.arange(-55,-17,4.8):paint(plane(1,43.35)&xx(x-1.4,x+1.4)&zz(56,60.5),4,'rear_upper_clerestory_back')
 for x in np.arange(-56,-15,8):
  for z in [6,11.5]:paint(plane(1,43.35)&xx(x-2.5,x+2.5)&zz(z,z+3.2),4,'rear_lower_discrete_window_back')
 for y in np.arange(5,40,6):
  for z in np.arange(17,49,5.3):paint(plane(0,-64.4)&yy(y-2.4,y+2.4)&zz(z,z+4.1),4,'tall_side_grid_existing_window_back')
 for y in np.arange(7,38,6):paint(plane(0,-64.4)&yy(y-1.85,y+1.85)&zz(56,60.4),4,'tall_side_upper_window_back')
 for x in np.arange(-55,-18,6):paint(plane(1,-3.35)&xx(x-1.75,x+1.75)&zz(51,56.2),4,'source_front_high_clerestory_back')
 paint(plane(1,-3.35)&xx(-55.5,-18.5)&zz(45,48),4,'source_front_high_horizontal_glass_back')
 paint(plane(1,29.5)&xx(5.5,70.5)&zz(2.8,32.8),1,'contractor_visible_outer_low_wing_pale_wall')
 paint(plane(1,28.35)&xx(12.5,63.5)&zz(19,24),4,'outer_wing_high_slit_back')
 paint(plane(1,28.35)&xx(19,63)&zz(13.5,16),4,'outer_wing_low_slit_back')
 for x in np.arange(15,64,8):paint(box(x-.45,x+.45,29,29.9,19,24),2,'existing_outer_slit_gray_mullion')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NHRI Zhunan Library Information original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nhrilib-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Association named library close view and Futsu contractor exterior; uncalibrated proxies','scope':'Gray fascia/rails, pale columns/tower, sandstone foreground piers/beams/stair and terrace verticals. Existing discrete glazing backs registered front, rear and left from two viewpoints; unregistered right side and roofs neutral. Different source dates unknown, no current-condition claim.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
