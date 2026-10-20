"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='eb12447ceea7899d830e2d02257d5c3a9da5ecd7bc9e667af0fa1769c6b3624a'
PALETTE=[('neutral_unseen','#A5A39B'),('dark_gray_tile','#565A61'),('visible_west_end_red','#813C39'),('gray_ridge','#91928D'),('display_plinth','#888A86')]
BUILDINGS=json.loads((A/'source/building-controls.json').read_text())
def classify(tri):
 color=np.zeros(len(tri),dtype=int);why=np.full(len(tri),'unseen_surface_or_annex_neutral',dtype=object)
 def paint(mask,n,reason):color[mask]=n;why[mask]=reason
 for b in BUILDINGS:
  # Invert original per-building rotation and translation; no mesh alteration.
  angle=np.deg2rad(b['angle_deg']);cs=np.cos(angle);sn=np.sin(angle)
  t=tri.copy();xy=t[:,:,:2]-np.array(b['model_center_mm']);t[:,:,0]=xy[:,:,0]*cs+xy[:,:,1]*sn;t[:,:,1]=-xy[:,:,0]*sn+xy[:,:,1]*cs
  lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
  L,W=b['roof_mm'];floor=[1.70,2.55,3.60,4.60][b['level']]+.55;E=floor+3.6
  envelope=(lo[:,0]>=-L/2-.0001)&(hi[:,0]<=L/2+.0001)&(lo[:,1]>=-W/2-1.0001)&(hi[:,1]<=W/2+1.0001)
  roof=envelope&(lo[:,2]>=E-.8501)&(hi[:,2]>=E-.0001)&(n[:,2]>.01)
  paint(roof,1,b['id']+'_existing_roof_slopes_dark_gray_visible_with_continuity_proxy')
  ridge=envelope&np.all(abs(t[:,:,2]-(E+2.65))<.0001,axis=1)&(n[:,2]>.9)
  paint(ridge,3,b['id']+'_existing_flattened_ridge_gray_proxy')
  # The aerial exposes only selected west short ends. No global red walls.
  if b['id'] in ['N3','S2','S3','S4']:
   gable=np.all(abs(t[:,:,0]-(-L/2+2))<.0001,axis=1)&(lo[:,2]>=E+.7999)&(hi[:,2]<=E+2.6501)&(n[:,0]<-.9)
   paint(gable,2,b['id']+'_photo_visible_west_upper_gable_only')
  if b['id'] in ['N3','S2']:
   wall=np.all(abs(t[:,:,0]-(-(L-3)/2))<.0001,axis=1)&(lo[:,2]>=floor-.1001)&(hi[:,2]<=floor+2.9001)&(n[:,0]<-.9)
   paint(wall,2,b['id']+'_visible_west_short_wall_surface_no_hidden_side_extension')
 paint(tri[:,:,2].max(axis=1)<=1.5001,4,'display_base_not_real_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'TKU Palace Classrooms original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'tku-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated 2021 photographer-image approximations, not measured material swatches','scope':'Seven registered roof surfaces; only N3/S2 west short walls and N3/S2/S3/S4 west upper gables red; hidden walls and both annexes neutral. 2021 source not 2026.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
