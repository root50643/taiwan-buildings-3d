"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='949be122ac7d08a0f80eda8b58e68c3858e068ba980a88160e9a163c250f04f3'
PALETTE=[('neutral_unseen','#A7A49D'),('light_stone','#C6C1B5'),('pink_clay_shaft','#BB9990'),('gray_cornice_sill','#827F75'),('gray_blue_glazing_proxy','#526F73'),('muted_green_medallion','#759992'),('display_plinth','#8C8B87')]
def classify(tri):
 c=tri.mean(axis=1);lo=tri.min(axis=1);hi=tri.max(axis=1);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.linalg.norm(normal,axis=1)[:,None]
 # One material per unchanged source face. All selections are tied to existing
 # part boundaries. Back/side facade repetitions are explicit symmetry proxies.
 color=np.ones(len(tri),dtype=int);why=np.full(len(tri),'light_stone_existing_base_or_upper_core',dtype=object)
 def paint(mask,n,reason):color[mask]=n;why[mask]=reason
 paint(hi[:,2]<=3.0001,6,'display_plinth_not_real_ground')
 paint((lo[:,2]>=27.3999)&(hi[:,2]<=115.4001),2,'existing_shaft_same_treatment_symmetry_proxy')
 # Roofs and concealed horizontal surfaces remain neutral, not inferred green.
 paint(normal[:,2]>.9,0,'upward_unseen_surface_neutral')
 # Cornice bands are defined by existing top/bottom part planes.
 for z0,z1 in [(24.2,28.1),(114.4,118.8),(134,136.7)]:
  paint((lo[:,2]>=z0-.001)&(hi[:,2]<=z1+.001)&(abs(normal[:,2])<.9),3,'existing_cornice_vertical_band')
 # Existing sills below the shaft windows, not painted shadows.
 for z in [33,43,53,63,73,83,93,103]:
  mask=(lo[:,2]>=z-.801)&(hi[:,2]<=z+.201)&(np.max(abs(c[:,:2]),axis=1)>13.49)
  paint(mask,3,'existing_backed_sill')
 # The pre-existing solid window recess back plane; do not color entire jambs.
 for axis in [0,1]:
  other=1-axis
  for sign in [-1,1]:
   for z in [33,43,53,63,73,83,93,103]:
    mask=np.all(abs(tri[:,:,axis]-sign*12.55)<.0001,axis=1)&(lo[:,2]>=z-.001)&(hi[:,2]<=z+5.401)&(lo[:,other]>=-2.401)&(hi[:,other]<=2.401)
    paint(mask,4,'existing_single_window_recess_back')
   for x in [-8.5,0,8.5]:
    mask=np.all(abs(tri[:,:,axis]-sign*12.85)<.0001,axis=1)&(lo[:,2]>=120.999)&(hi[:,2]<=131.401)&(lo[:,other]>=x-2.451)&(hi[:,other]<=x+2.451)
    paint(mask,4,'existing_observation_window_recess_back')
 # Relief below observation room uses stone-gray proxy, preserving perforations.
 mask=(lo[:,2]>=108.999)&(hi[:,2]<=112.101)&(np.max(abs(c[:,:2]),axis=1)>13.501)
 paint(mask,3,'existing_relief_stone_gray_proxy')
 # Only actual existing abstract medallion front faces receive green. The full
 # roof is intentionally neutral. This is not a reproduced school emblem.
 for axis in [0,1]:
  other=1-axis
  for sign in [-1,1]:
   mask=np.all(abs(tri[:,:,axis]-sign*9.8)<.0001,axis=1)&(lo[:,2]>=140.499)&(hi[:,2]<=146.501)&(lo[:,other]>=-3.001)&(hi[:,other]<=3.001)
   paint(mask,5,'abstract_existing_medallion_front_color_proxy')
 return color,why

def writezip(path,files):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in files:
   info=zipfile.ZipInfo(name,(2026,10,20,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data)
def main():
 raw=(R/'model.stl').read_bytes();assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
 n=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*n
 tri=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)],dtype=np.float64).reshape(n,3,3)
 v,inv=np.unique(tri.reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
 colors,why=classify(tri);assert set(colors)==set(range(len(PALETTE)))
 # .17g exactly roundtrips every source float32 value as float64.
 ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';E.register_namespace('',ns)
 model=E.Element('{'+ns+'}model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'});res=E.SubElement(model,'resources');bm=E.SubElement(res,'basematerials',{'id':'20'})
 for name,color in PALETTE:E.SubElement(bm,'base',{'name':name,'displaycolor':color+'FF'})
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'YunTech Clouds Pavilion original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'yuntech-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official photograph approximations, not measured material swatches','symmetry':'Facade colors extended around existing symmetric model, not separately observed rear'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
