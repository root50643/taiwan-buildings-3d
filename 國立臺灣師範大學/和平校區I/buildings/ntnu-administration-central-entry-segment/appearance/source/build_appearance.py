"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='be7a7016c5e2012d06681b9c5956316c532b75fbc9ef03f4cbc2b407da9d6324'
PALETTE=[('neutral_unseen','#AAA79F'),('red_brown_brick','#986A5D'),('warm_gray_stone','#B2AE98'),('pale_window_frames','#D1D0B9'),('muted_glazing','#6D8280'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_cut_ends_and_top_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def xx(a,b):return (lo[:,0]>=a-.00025)&(hi[:,0]<=b+.00025)
 def yy(a,b):return (lo[:,1]>=a-.00025)&(hi[:,1]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 paint(plane(1,-11.5)&zz(3,84.8),1,'registered_front_backing_brick_no_fake_quoins')
 # Only existing piers and bands; photo alternating masonry not separately modeled.
 for x in [-64,-26,26,64]:
  paint(xx(x-1.55,x+1.55)&yy(-12.8,-10.2)&zz(3,86)&(n[:,2]<.1),2,'existing_solid_front_piers_stone_proxy_no_added_alternating_blocks')
  paint(xx(x-2.1,x+2.1)&yy(-13.4,-9.6)&zz(83,87)&(n[:,2]<.1),2,'existing_pier_caps_stone_sides')
 for z in [4,29,56,82]:paint(xx(-66,66)&yy(-12.8,-10.4)&zz(z,z+1.6),2,'existing_horizontal_stone_band')
 # Oriel front and angled cheeks, excluding unseen upper flat surfaces.
 paint(xx(-22,22)&yy(-23,-10.99)&zz(28,85)&(n[:,2]<.1),2,'observed_central_oriel_stone_faces_and_decorative_panels')
 paint(xx(-23,23)&yy(-24.5,-11.5)&zz(27,29.4)&(n[:,2]<.1),2,'original_oriel_base_stone_face')
 paint(xx(-22,22)&yy(-23.5,-6.5)&zz(84,91.8)&(n[:,2]<.1)&(n[:,1]<-.1),2,'observed_front_crest_stone_faces_only')
 # Tudor hood and passage returns are masonry, void remains an actual opening.
 paint(xx(-15,15)&yy(-14.1,-11.3)&zz(2.9,28.2),2,'existing_tudor_arch_hood_stone_not_dark_door')
 # Existing geometric frame members are separable; never paint generic wall strips.
 for y,xs,w,zs in [(-11.5,[-50,-36,36,50],10,[8,35,62]),(-22,[-10.5,0,10.5],7.4,[33,62])]:
  for x in xs:
   for z in zs:
    for zz0 in [z,z+15.7]:paint(xx(x-w/2-1,x+w/2+1)&yy(y-1.05,y+.45)&zz(zz0,zz0+1.3),3,'existing_window_outer_horizontal_frame')
    for x0 in [x-w/2-.35,x+w/2+.35]:paint(xx(x0-.65,x0+.65)&yy(y-1.05,y+.45)&zz(z,z+17),3,'existing_window_outer_vertical_frame')
    paint(xx(x-.5,x+.5)&yy(y-.25,y+1.15)&zz(z,z+17),3,'existing_window_central_mullion')
    for level in [z+17*.49,z+17*.79]:paint(xx(x-w/2,x+w/2)&yy(y-.25,y+1.15)&zz(level,level+1),3,'existing_window_transom')
    paint(xx(x-w/2,x+w/2)&plane(1,y+1.25)&zz(z,z+17),4,'existing_window_recess_back_muted_glazing')
 for x in [-10.5,0,10.5]:paint(xx(x-3.9,x+3.9)&yy(-23.8,-20.6)&zz(52,59.2),2,'original_diamond_relief_and_panel_stone_not_glass')
 # Polygonal side-light backs are not confidently isolated, remain stone approximation.
 paint(hi[:,2]<=3.0001,5,'display_base_not_site_surface')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTNU Administration Central Entry Segment original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntnuadmin-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NTNU guide image010.jpg; photo capture date unknown','scope':'Existing central entry segment only: front brick, stone oriel/pier/arch/bands, pale existing frame members and front window recess backs. No new quoins; side lights unassigned as glazing; roof, rear and cut ends neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
