"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='4321f4114275c766ac743e0adb1bac9d9626368a9fee920ea4734b805032453f'
PALETTE=[('neutral_unconfirmed_structure','#AAA79F'),('observed_white_inner_wall_columns','#D4D4CA'),('observed_gray_canopy_fascia','#666966')]
def classify(tri):
 v=tri;eps=.0003
 actual=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);n=actual/np.linalg.norm(actual,axis=1)[:,None]
 sel=np.zeros(len(v),bool)
 for i in range(80):
  th=(i+.5)*np.pi/80;u=np.array([np.cos(th),np.sin(th)]);rel=v[:,:,:2]-[0,-28];d=rel@u;t=np.array([-np.sin(th),np.cos(th)]);w=rel@t
  # inner original polygon wall planes. No cutbacks/reveals/pier faces.
  m=(abs(d-43*np.cos(np.pi/160))<eps).all(1)&(abs(w)<=43*np.sin(np.pi/160)+eps).all(1)&(v[:,:,2]>=2.8-eps).all(1)&(v[:,:,2]<=57+eps).all(1)&(abs(n[:,2])<eps)&((n[:,:2]@u)<-.99)
  sel|=m
 # Original radial white pier exterior planes, limited to full rotated box.
 for deg in range(2,180,13):
  th=np.radians(deg);u=np.array([np.cos(th),np.sin(th)]);t=np.array([-np.sin(th),np.cos(th)]);rel=v[:,:,:2]-[0,-28];r=rel@u;w=rel@t
  bounds=(r>=40.45-eps).all(1)&(r<=44.95+eps).all(1)&(abs(w)<=1.25+eps).all(1)&(v[:,:,2]>=3-eps).all(1)&(v[:,:,2]<=57+eps).all(1)
  planes=(abs(r-40.45)<eps).all(1)|(abs(w-1.25)<eps).all(1)|(abs(w+1.25)<eps).all(1)
  sel|=bounds&planes&(abs(n[:,2])<eps)
 # canopy front and two end fascia only; no top/underside (not photography-proven).
 can=np.zeros(len(v),bool)
 for ax,k,sgn in [(1,1.5,-1),(0,-11.5,-1),(0,11.5,1)]:
  can|=(n[:,ax]*sgn>.99)&(abs(v[:,:,ax]-k)<eps).all(1)&(v[:,:,0]>=-11.5-eps).all(1)&(v[:,:,0]<=11.5+eps).all(1)&(v[:,:,1]>=1.5-eps).all(1)&(v[:,:,1]<=14.5+eps).all(1)&(v[:,:,2]>=13.5-eps).all(1)&(v[:,:,2]<=15.3+eps).all(1)
 assert not (sel&can).any()
 color=np.zeros(len(v),dtype=int);color[sel]=1;color[can]=2
 why=np.full(len(v),'neutral_unconfirmed_or_outside_documented_scope',dtype=object);why[sel]='white_inner_wall_and_columns';why[can]='gray_canopy_fascia'
 assert np.bincount(color).tolist()==[4772,1395,9]
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCCU Jingtang Building limited original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nccu-jingtang-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official NCCU library memory photos personally viewed; capture dates unknown; uncalibrated material approximations.','scope':'Only 1395 inner curved white wall/column triangles and 9 gray canopy fascia triangles. All 4772 remaining triangles neutral, including window backs/frames, roof, back and ends. Geometry unchanged.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
