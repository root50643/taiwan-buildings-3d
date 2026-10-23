"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='49101683bfaa763f7130d995f47c88fc7745bcbb51207c174220cc2345c511ce'
import math
PALETTE=[('neutral_unconfirmed_structure','#AAA79F'),('letter_outward_pale_gray_proxy','#CDD1CD'),('window_backing_light_opaque_proxy','#A7B8B5')]
def angles(a,b,n):return [a+(b-a)*i/(n-1) for i in range(n)]
def strokes(ch,x,w):
 z=17;h=26
 if ch=='O':return [[(x+w/2+w/2*math.cos(t),z+h/2+h/2*math.sin(t)) for t in angles(0,2*math.pi,65)]]
 if ch=='U':return [[(x,z+h),(x,z+w/2)]+[(x+w/2+w/2*math.cos(t),z+w/2+w/2*math.sin(t)) for t in angles(math.pi,2*math.pi,25)]+[(x+w,z+h)]]
 if ch=='R':return [[(x,z),(x,z+h),(x+w*.5,z+h)]+[(x+w*.5+w*.5*math.cos(t),z+h*.76+h*.24*math.sin(t)) for t in angles(math.pi/2,-math.pi/2,25)]+[(x,z+h*.52),(x+w,z)]]
 if ch=='M':return [[(x,z),(x,z+h),(x+w/2,z),(x+w,z+h),(x+w,z)]]
 if ch=='E':return [[(x+w,z+h),(x,z+h),(x,z),(x+w,z)],[(x,z+h/2),(x+w*.85,z+h/2)]]
 if ch=='S':return [[(x+w/2+w/2*math.cos(t),z+h*.75+h*.25*math.sin(t)) for t in angles(.1,math.pi*1.5,30)]+[(x+w/2+w/2*math.cos(t),z+h*.25+h*.25*math.sin(t)) for t in angles(math.pi*.5,-math.pi+.1,30)]]
def classify(tri):
 from shapely.geometry import LineString, Polygon
 from shapely.ops import unary_union
 sel=json.loads((A/'source/source-selection.json').read_text());eps=3e-5;color=np.zeros(len(tri),dtype=int);why=np.full(len(tri),'neutral_unconfirmed_or_excluded',dtype=object)
 cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(cross,axis=1);norm=cross/length[:,None];areas=length/2;audit=[]
 for g in sel['groups']:
  side=g['side'];m=(side*norm[:,1]>=1-1e-7)&(abs(tri[:,:,1]-g['plane_y'])<=eps).all(1)
  if g['material']=='letter':
   ps=[]
   for ch,x,w in [('O',-64,20),('U',-42,11),('R',-29,11),('M',-14,18),('U',6,10),('S',18,10),('E',30,8),('U',40,10),('M',52,12)]:
    for points in strokes(ch,x,w):
     if side==1:points=[(-x,z) for x,z in points]
     ps.append(LineString(points).buffer(.9,cap_style=2,join_style=2))
   domain=unary_union(ps).buffer(eps)
   m&=(tri[:,:,2]<=44.3+eps).all(1)
   for i in np.flatnonzero(m):
    if not domain.covers(Polygon(tri[i][:,[0,2]])):m[i]=False
   col=1
  else:
   xa,xb,za,zb=g['finite_xz_bounds']
   for axis,lo,hi in [(0,xa,xb),(2,za,zb)]:m&=(tri[:,:,axis]>=lo-eps).all(1)&(tri[:,:,axis]<=hi+eps).all(1)
   col=2
  ids=np.flatnonzero(m).tolist();assert ids==g['faces'];assert not np.any(color[m]);color[m]=col;why[m]=g['name'];area=float(areas[m].sum());assert abs(area-g['area_mm2'])<1e-7;audit.append(dict(name=g['name'],ids=ids,count=len(ids),area_mm2=area))
 assert np.flatnonzero(color==1).tolist()==sel['approved_faces']['letter'];assert np.flatnonzero(color==2).tolist()==sel['approved_faces']['window'];assert np.bincount(color).tolist()==[7428,1002,130]
 (A/'qa/material-boundaries.json').write_text(json.dumps(dict(method='Actual outward cross-product normal, all 3 vertices in finite plane/domain; full triangle inside buffered stroke union for letters; no cutting',counts=np.bincount(color).tolist(),selected_area_mm2=float(areas[color>0].sum()),groups=audit),indent=2)+'\n')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTUA You Chang Museum historical-source limited original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntua-you-chang-museum-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official historical photographs: self-reported original dates 2007-11-01 and 2007-10-24 without timezone offset. 2017 is postprocessing; retrieved 2026-10-23 is not capture date. Uncalibrated opaque display proxies.','scope':'Only 1132 original faces:1002 outward lettering,130 existing window backings;7428 neutral. Not the northern planned museum, not brick/wood behind glass, no geometry changes.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
