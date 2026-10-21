"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='00d317de3628ecc8922c0da391d53adfa0a40e9703e9daa5c7fdda2b21cc2136'
PALETTE=[('neutral_mixed_facades_deck_and_unknown','#AAA79F'),('warm_copper_color_roof_proxy','#AB704F'),('lightgray_open_pavilion_columns','#B8BCB5')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_shop_facades_unsegmented_terrace_grass_lower_piers_windows_and_roof_edges_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 roofs=[(-48,-7,26,26,21,5.3,12,2.5),(-14,2,25,20,17,5.1,-8,0),(14,2,26,29,23,5.5,27,-2.2),(29,10,25,16,22,5,27,1.5)]
 counts=[]
 for num,(x,y,z,w,d,rise,ang,off) in enumerate(roofs):
  # Same source-generator roof points, used solely to locate unchanged STL faces.
  v=np.array([[-w/2,-d/2,1.4],[w/2,-d/2,2.6],[w/2,d/2,3.7],[-w/2,d/2,2.0],[-w*.19,off,rise],[w*.19,off,rise]])
  a=np.deg2rad(ang);R=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]])
  v=v@R.T+np.array([x,y,z]);mask=np.zeros(len(t),dtype=bool)
  for f in [[0,1,5],[0,5,4],[1,2,5],[2,3,4],[2,4,5],[3,0,4]]:
   p,q,r=v[f];u=q-p;v2=r-p;n=np.cross(u,v2);n=n/np.linalg.norm(n);a0=np.dot(u,u);b0=np.dot(u,v2);c0=np.dot(v2,v2);den=a0*c0-b0*b0
   rel=t-p;d0=np.einsum('ijk,k->ij',rel,u);e0=np.einsum('ijk,k->ij',rel,v2)
   s=(c0*d0-b0*e0)/den;w2=(a0*e0-b0*d0)/den
   coplanar=np.all(abs(np.einsum('ijk,k->ij',rel,n))<.001,axis=1)
   inside=np.all((s>=-.001)&(w2>=-.001)&(s+w2<=1.001),axis=1)
   mask|=coplanar&inside&(norm[:,2]>.0001)
  counts.append(int(mask.sum()));paint(mask,1,'source_registered_folded_roof_'+str(num+1)+'_top_only_all_vertices_on_original_patch')
 assert counts==[6,6,12,18],counts
 assert int(np.sum(color==1))==42
 for x in [-21,-7]:
  for y in [-4,8]:
   m=(lo[:,0]>=x-.904)&(hi[:,0]<=x+.904)&(lo[:,1]>=y-.904)&(hi[:,1]<=y+.904)&(lo[:,2]>=14.196)&(hi[:,2]<=26.004)
   paint(m,2,'source_visible_open_pavilion_existing_lightgray_column_component')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTPU Mind Lake Hall Bounded Roof Appearance original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntpumind-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NTPU official and Fieldscape completed project photos, no Original capture dates; modification2021/2022 and publication2022 are not capture dates. Day aerial warm copper-color metal roof proxy, not red clay tiles or measured metal composition','scope':'Roof-limited color study: four original folded roof tops over three pavilion zones, exact plane and all-three-vertex barycentric containment, plus four gray open-pavilion columns. Mixed shop walls, unsegmented grass/paving terrace, lower brick/glass fields, underside and roof fascia neutral. Original roof twist simplification retained; no seams/lawn/equipment invented.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
