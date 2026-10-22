"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='99af38ad78e375e04fae9217193b2c9f22335a646d1679c05e3ab7641a3a5d75'
PALETTE=[('neutral_unconfirmed_envelope_frames_base','#AAA79F'),('documented_white_metal_cover_top','#D9DAD5'),('documented_front_red_roof_slopes','#984A4E')]
def classify(tri):
 t=tri/1.5-np.array([17,2,0]); eps=1e-4
 normals=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);normals/=np.linalg.norm(normals,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'neutral_unconfirmed_or_outside_documented_scope',dtype=object)
 top=[(-12.5,30.8),(-7,31.5),(-1,31.8),(1,31.8),(7,31.5),(12.5,30.8)]
 for k,((x0,z0),(x1,z1)) in enumerate(zip(top,top[1:])):
  slope=(z1-z0)/(x1-x0)
  for label,y0,y1,dz in [('cover',-20,24,0)]+[('rib_'+str(j),y-.4,y+.4,.28) for j,y in enumerate(np.linspace(-19.5,23.5,9))]:
   mask=np.all((t[:,:,0]>=x0-eps)&(t[:,:,0]<=x1+eps)&(t[:,:,1]>=y0-eps)&(t[:,:,1]<=y1+eps)&(abs(t[:,:,2]-(slope*(t[:,:,0]-x0)+z0+dz))<eps),axis=1)&(normals[:,2]>0)&(abs(normals[:,0]+slope*normals[:,2])<eps)&(abs(normals[:,1])<eps)
   color[mask]=1;why[mask]='documented_white_'+label+'_segment_'+str(k)
 assert (color==1).sum()==190
 for label,y,z,w,d,h,sy in [('upper_front',-25.2,28.1,23.5,8.2,2.4,.17),('entry',-32,7.6,14,7.3,1.2,.18)]:
  y0=y-d/2;y1=y-d*sy/2;slope=h/(y1-y0)
  # Front hip support tapers from full width to .92 width with elevation.
  frac=(t[:,:,1]-y0)/(y1-y0);half=w/2*(1-.08*frac)
  mask=np.all((t[:,:,1]>=y0-eps)&(t[:,:,1]<=y1+eps)&(abs(t[:,:,0])<=half+eps)&(abs(t[:,:,2]-(z+slope*(t[:,:,1]-y0)))<eps),axis=1)&(normals[:,2]>0)&(normals[:,1]<0)&(abs(normals[:,0])<eps)&(abs(normals[:,1]+slope*normals[:,2])<eps)
  assert mask.sum()==4
  assert not np.any(color[mask]);color[mask]=2;why[mask]='documented_'+label+'_red_front_slope'
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NHU Wujinzang Library limited original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nhu-library-roofs-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NHU official ground VR node datetime 2023/9/18 is metadata, not certified capture date; aerial capture date unknown; viewed 2026-10-22; uncalibrated proxy, not verified 2026 condition','scope':'190 exact cover/rib top faces and 8 front red slope faces only. Walls, glass, roof side faces, side roofs and all undocumented surfaces remain neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
