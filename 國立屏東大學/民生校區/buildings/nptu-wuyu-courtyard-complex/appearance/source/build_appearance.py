"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='aa716930ffe333cd99e2adb6dc4f58ecb3bd3b1852a2ae96892a48b82b19aa6d'
PALETTE=[('neutral_masonry_mixed_balconies_louvers_unknown','#AAA79F'),('muted_bluegreen_curtain_proxy','#729E9A'),('muted_graygreen_discrete_windows','#798F88'),('silvergray_entry_roof','#ACB4AE')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'masonry_mixed_bands_balconies_louvers_vent_panels_low_wings_unknown_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.004)&(hi[:,2]<=b+.004)
 def xx(a,b):return (lo[:,0]>=a-.004)&(hi[:,0]<=b+.004)
 def yy(a,b):return (lo[:,1]>=a-.004)&(hi[:,1]<=b+.004)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 for a,b in [(49,88),(109,126)]:paint(plane(1,18.4)&xx(-11,11)&zz(a,b)&(norm[:,1]<-.0001),1,'source_front_central_continuous_curtain_field_exact_back')
 for z in [91,100]:paint(plane(1,18.4)&xx(-11,11)&zz(z,z+4.8)&(norm[:,1]<-.0001),2,'source_front_central_short_framed_window_row')
 paint(plane(1,42)&xx(-11,11)&zz(94,126)&(norm[:,1]>.0001),1,'source_rear_center_curtain_field_exact_back')
 radius=np.sqrt(t[:,:,0]**2+(t[:,:,1]-45)**2);ang=np.degrees(np.arctan2(t[:,:,1]-45,t[:,:,0]))
 curved=np.all(abs(radius-12.2)<.004,axis=1)&np.all((ang>=19.99)&(ang<=160.01),axis=1)&zz(54,85)&(abs(norm[:,2])<.001)
 paint(curved,1,'source_rear_drum_vertical_inner_facets_only_no_horizontal_reveals')
 for side in [-1,1]:
  for z in [54,66,78,90,102,114,126]:paint(plane(0,side*43.25)&yy(5,15)&zz(z,z+9)&(norm[:,0]*side<-.0001),1,'source_tower_inward_curtain_assembly_proxy_not_transparency_claim')
  for z in [96,108,120]:
   for y in [25,35]:paint(plane(0,side*64.75)&yy(y-2.7,y+2.7)&zz(z,z+4.7)&(norm[:,0]*side>.0001),2,'source_discrete_upper_tower_side_window_back')
 # Upper facade paired lights and separate bands; balcony recesses deliberately excluded.
 def pair(x,z,w,h):
  for dx in [-w/4,w/4]:
   cx=x+dx;half=(w/2-.65)/2;paint(plane(1,17.9)&xx(cx-half,cx+half)&zz(z,z+h)&(norm[:,1]<-.0001),2,'source_registered_upper_paired_window_back')
 for x in [-38,-30,-22,22,30,38]:
  pair(x,90,4.8,4.8)
  for z in [117,123]:pair(x,z,4.8,3.7)
 for x in [-15.5,15.5]:
  for z in [90,99,108,117,123]:pair(x,z,4.4,4.6 if z<117 else 3.7)
 for z in [99,108]:
  for x in [-30.5,30.5]:
   for i in range(6):
    cx=x-10.5+(i+.5)*3.5;paint(plane(1,17.9)&xx(cx-1.25,cx+1.25)&zz(z,z+4.8)&(norm[:,1]<-.0001),2,'source_registered_upper_window_bank_back')
 roof=np.all(abs(t[:,:,2]-(53.3-11.5/18*abs(t[:,:,0])))<.004,axis=1)
 paint(roof&xx(-18,18)&yy(-61.5,-26.5)&(norm[:,2]>.0001),3,'source_aerial_entry_metal_roof_exact_slopes_only_not_gables')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NPTU Wuyu Glazing And Entry Roof Limited Appearance original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nptuwuyu-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Eight complete NPTU official photographs, Original2002 and2016 plus other metadata as documented, mixed-era evidence not2026. Muted bluegreen curtain assemblies, graygreen discrete upper windows, silvergray entry roof','scope':'Glazing and entry roof limited appearance: exact whole-triangle backs and curved vertical facets only. All masonry, mixed balcony backs, opaque shoulder louvers, low ranges, vent panels and unregistered roofs remain neutral. Original geometry unchanged, no fine curtain grids or facade bands invented.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
