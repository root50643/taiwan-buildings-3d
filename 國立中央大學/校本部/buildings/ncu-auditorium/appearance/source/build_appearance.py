"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='50964d7b2b33cb1489a01b8b3198e272d1a1a03c2d537dd9c7fb4030053e9d4b'
PALETTE=[('neutral_unresolved_envelope_and_base','#AAA79F'),('muted_gray_blue_foyer_glazing','#3B4A4F'),('silver_gray_foyer_frames','#A6ABA8'),('pale_gray_front_foyer_roof','#C3C6C2')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);eps=.00015
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'neutral_unresolved_upper_panel_pattern_rear_mixed_envelope_or_base',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-eps)&(hi[:,2]<=b+eps)
 def xx(a,b):return (lo[:,0]>=a-eps)&(hi[:,0]<=b+eps)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<eps,axis=1)
 def cylinder_side(cx,cy,rx,ry,n):
  # Exact planar facets of original regular polygon cylinder, not a centroid/radius mask.
  hit=np.zeros(len(t),dtype=bool)
  for j in range(n):
   a=2*np.pi*(j+.5)/n
   d=(t[:,:,0]-cx)/rx*np.cos(a)+(t[:,:,1]-cy)/ry*np.sin(a)-np.cos(np.pi/n)
   hit |= np.all(abs(d)<eps/max(rx,ry),axis=1)
  return hit
 outer=cylinder_side(0,0,66,48,144)
 gaps=[(3,10),(11.15,17),(18.15,24),(25.15,31),(32.15,38),(39.15,45),(46.15,46.8)]
 for a,b in gaps:paint(outer & xx(0,70)&zz(a,b)&(abs(normal[:,2])<eps),1,'daylight_photo_015_existing_front_ellipse_vertical_glazing_full_face')
 band_side=cylinder_side(0,0,67,49,144)
 # Every original band top/bottom exterior portion lies outside the solid foyer.
 radial=(t[:,:,0]/66)**2+(t[:,:,1]/48)**2
 for z in [10,17,24,31,38,45]:
  cap=(plane(2,z)|plane(2,z+1.15)) & np.all(radial>=.9994,axis=1)
  paint(xx(-14,70)&zz(z,z+1.15)&(band_side|cap|plane(0,-14)),2,'daylight_photo_015_original_horizontal_metal_relief')
 for a in range(-88,89,11):
  r=np.deg2rad(a);cx=66*np.cos(r);cy=48*np.sin(r)
  near=np.all((abs(t[:,:,0]-cx)<=1+eps)&(abs(t[:,:,1]-cy)<=1+eps),axis=1)
  paint(near & zz(3,46)&(cylinder_side(cx,cy,1,1,12)|plane(2,46)),2,'daylight_photo_015_original_vertical_support_relief')
 paint(plane(2,46.8)&xx(0,70)&(normal[:,2]>eps),3,'aerial_photos_009_010_independent_front_foyer_roof_only')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCU Auditorium partial foyer original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ncu-auditorium-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Architect supplied gooood report 2021-11-03; photographs capture dates unknown; uncalibrated subdued display proxies','scope':'Partial front foyer glazing, original metal relief and independently bounded front foyer roof only. Upper multicolored aluminum panels and mixed rear envelope stay neutral; no invented panel pattern, transparent glazing or exact pane count.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
