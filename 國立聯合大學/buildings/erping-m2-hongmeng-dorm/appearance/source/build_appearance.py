"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='525839fc29c02b2d26ec9580a8cb4c1b4d2957d256a0123f745f6cbac98e4bf2'
PALETTE=[('neutral_unknown','#AAA79F'),('warm_concrete_facade','#B6AE9E'),('pale_frames_lift_cladding','#D0D2CA'),('muted_gray_glazing','#7B8885'),('teal_lift_glass_canopy','#568B81'),('silver_gray_metal_canopy_rail','#A6AFAD')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_rear_ends_roof_and_unsplit_base_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.003)&(hi[:,2]<=b+.003)
 def xx(a,b):return (lo[:,0]>=a-.003)&(hi[:,0]<=b+.003)
 def yy(a,b):return (lo[:,1]>=a-.003)&(hi[:,1]<=b+.003)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.003,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(box(-56.5,66,-16.7,-13.8,2.3,55.8),1,'documented_warm_concrete_front_structure_and_solid_recess_spandrels')
 for row in range(4):
  z=7+row*11.2
  for x in np.linspace(-51,57,13):
   paint(plane(1,-13.95)&xx(x-3.15,x+3.15)&zz(z+2.4,z+7.5),3,'only_inner_window_pane_back_not_outer_recess')
   for k in [1,2]:
    q=x-3.15+6.3*k/3;paint(box(q-.4,q+.4,-15.175,-13.825,z+2.35,z+7.55),2,'original_pale_window_mullion')
   paint(box(x-3.2,x+3.2,-15.175,-13.825,z+6.072,z+6.872),2,'original_pale_window_transom')
 paint(plane(0,-69.5)&yy(-21,21)&zz(2.3,63.1),2,'documented_white_lift_side_unsplit_green_bands_omitted')
 paint(box(-69.5,-56.5,-22.4,-20.3,2.3,63.1),2,'documented_pale_lift_front_X_frames_and_surrounds')
 for row in range(5):
  z=5.1+row*11.1
  paint(plane(1,-20.35)&xx(-65.8,-57.8)&zz(z,z+9.3),4,'existing_lift_glazing_recess_teal_proxy')
 paint(box(-66.5,-45.5,-27.7,-18.7,28.8,30.3),4,'documented_small_teal_entrance_canopy')
 paint(box(-68.5,-33.5,-32.5,-14.9,17.8,19.8),4,'documented_abbreviated_bridge_green_deck_not_extra_extent')
 paint(box(-67.6,-34.3,-32.5,-29.35,19.5,23.9),5,'existing_bridge_posts_and_rail_gray')
 for x in [-66,-36]:paint(box(x-.85,x+.85,-31.05,-29.35,2.3,17.9),5,'existing_bridge_support_gray')
 for x in [-65,-47]:paint(box(x-.75,x+.75,-27.55,-26.05,19.6,29),5,'existing_canopy_post_gray')
 paint(box(-66.35,-57.25,-22.55,-21.45,26.5,29.7),2,'blank_pale_sign_no_invented_text')
 paint(box(-41.5,61.5,-18.2,-14.2,9.7,10.9),5,'documented_lower_awning_conservative_metal_gray')
 paint(box(-54,52,-12,18,58,66),5,'documented_metal_canopy_NOT_confirmed_PV_top_silver_proxy')
 for x in [-51,-31,-11,9,29,49]:
  for y in [-9,15]:paint(box(x-.75,x+.75,y-.75,y+.75,55.6,63.6),5,'existing_canopy_support_silver')
 paint(hi[:,2]<=2.4001,0,'neutral_original_base')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU M2 Hongmeng Dormitory original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuum2-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official M2 complete exterior photos 1 and 4; uncalibrated proxies','scope':'Warm front concrete and solid spandrels, pale existing window/lift frames, inner panes only gray glass, teal lift glazing/canopy/bridge deck. Roof canopy metal underside documented but PV top NOT confirmed; neutral silver same-assembly proxy. Unsplit green cladding bands omitted, unseen rear and ends neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
