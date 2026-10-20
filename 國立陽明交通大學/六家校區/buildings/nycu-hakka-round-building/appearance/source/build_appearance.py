"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='522314e6bc9582b7c6b6e0f968fc685f46f74a8b6f95fa5661f41d3ed675e84c'
PALETTE=[('neutral_unregistered','#AAA79F'),('concrete_frames','#B2B1A7'),('silvergray_fan_roofs','#C0C6C6'),('muted_bluegray_glazing','#637E89'),('front_terrace_grass_proxy','#7F9856'),('display_plinth','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None];r=np.linalg.norm(t[:,:,:2],axis=2);rc=np.linalg.norm(c[:,:2],axis=1);ang=np.degrees(np.arctan2(c[:,1],c[:,0]))%360
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unregistered_or_mixed_surface_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0001)&(hi[:,2]<=b+.0001)
 # Source-registered concrete galleries/slab edges and cylindrical backing remain untextured.
 paint((r.min(1)>=27.0)&(r.max(1)<=50.1)&zz(2.9,44.65),1,'registered_main_ring_concrete_proxy')
 # Only top surfaces of the three stepped rear fan roofs and conference cap.
 paint((n[:,2]>.99)&(lo[:,2]>=44.0999)&(r.max(1)<=51.0002)&(ang>=10.9)&(ang<=169.1),2,'existing_rear_fan_and_conference_roof_top_silvergray')
 # Exact original radial recess backs, not entire wall bands or dark openings.
 for a in range(0,360,15):
  ar=np.radians(a);u=np.array([np.cos(ar),np.sin(ar)]);v=np.array([-np.sin(ar),np.cos(ar)]);rad=t[:,:,:2]@u;side=t[:,:,:2]@v
  for z in [5.2,15.2,25.2]+([35.2] if 12<=a<=168 else []):
   paint(np.all(abs(rad-47.25)<.0002,axis=1)&(np.max(abs(side),axis=1)<=4.7502)&zz(z,z+6.2),3,'existing_outer_radial_recess_back_glazing')
   if not 68<=a<=112:paint(np.all(abs(rad-37.55)<.0002,axis=1)&(np.max(abs(side),axis=1)<=4.1002)&zz(z,z+6.2),3,'existing_courtyard_radial_recess_back_glazing')
 # Existing central projecting drum has curved inward recess backs.
 for z in [6,16,26,36]:paint((r.min(1)>=19.58)&(r.max(1)<=19.6002)&zz(z,z+5.7)&(ang>=70.9)&(ang<=109.1),3,'existing_conference_curved_recess_back_glazing')
 # Source aerial shows front terrace lawn. Original triangles set spatial resolution;
 # never color parapet tops/walls and never invent separate paving strips.
 paint(np.all(abs(t[:,:,2]-34.65)<.0001,axis=1)&(n[:,2]>.99)&(r.min(1)>=29.2998)&(r.max(1)<=50.0002)&(r.max(1)>36.01)&(lo[:,1]<-.0001),4,'front_terrace_inset_from_parapets_lawn_proxy_not_exact_paving_boundary')
 # Low-wing slab spans lawn AND paved edge in one triangle: intentionally left neutral.
 paint(hi[:,2]<=3.0001,5,'display_base_not_real_ground_or_courtyard_grass')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NYCU Hakka Round Building original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'hakka-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NYCU courtyard and aerial photographs, capture dates unknown approximations, not measured material swatches','scope':'Source-bounded round building; inset front terrace lawn proxy, registered roof tops and recessed glass; mixed low-wing lawn/paving neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
