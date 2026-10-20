"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='043b6cb6208f9b56562d007cdbcc7b69e90081bcebffb8185fde6b88bed7724b'
PALETTE=[('neutral_unseen','#AAA79F'),('gray_concrete','#999D96'),('yellow_inclined_columns','#D9AF42'),('red_mid_bands','#B54E43'),('dark_shaft_glazing','#52666B'),('existing_PV','#627E93'),('silver_mullions','#AAB3B0')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_rear_roof_lower_open_recess_and_unsplit_mixed_back_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0003)&(hi[:,2]<=b+.0003)
 def xx(a,b):return (lo[:,0]>=a-.0003)&(hi[:,0]<=b+.0003)
 def yy(a,b):return (lo[:,1]>=a-.0003)&(hi[:,1]<=b+.0003)
 def plane(y):return np.all(abs(t[:,:,1]-y)<.0003,axis=1)
 def box(x,y,z,w,d,h):return xx(x-w/2,x+w/2)&yy(y-d/2,y+d/2)&zz(z,z+h)
 paint(box(0,7,2.3,118,41,44)&(n[:,1]<-.99)&plane(-13.5),1,'observed_front_structural_border_gray')
 paint(box(64,5,2.3,14,45,54)&(n[:,1]<.01)&(n[:,2]<.01),1,'observed_front_shaft_concrete_not_adjacent_T2')
 paint(xx(59.5,68.5)&zz(6,52)&plane(-16.9),5,'existing_shaft_glazing_recess_back_only')
 for z in np.arange(8,49,6):paint(box(64,-18,float(z),9.5,1.8,1.1),7,'existing_shaft_crossbars_gray')
 # Front recess back triangles cross both floors: leave neutral; no eligible upper-only triangles.
 for x in [-50,-25,0,25,50]:paint(box(x,-13.8,3,1.5,2.8,42),1,'existing_behind_beam_vertical_structure_gray')
 for x in np.arange(-52,56,7):paint(box(float(x),-13.9,23.8,1,2.6,17),7,'existing_upper_glazing_mullions_gray')
 for z in [4,43]:paint(box(0,-15,float(z),120,3,1.5),1,'observed_outer_horizontal_structure_gray')
 for z in [22,25]:paint(box(0,-15,float(z),120,3,1.5),3,'observed_existing_midlevel_red_bands')
 # Exact distance to original twelve-sided inclined cylinder axes, not broad X stripes.
 for x in [-50,-25,0,25,50]:
  for dx in [-1.7,1.7]:
   a=np.array([x+dx,-25,2.1]);v=np.array([0,10,41.9]);L=np.linalg.norm(v);u=v/L;d=t-a;h=d@u;r=np.linalg.norm(d-h[:,:,None]*u,axis=2)
   paint(np.all((r<=1.1004)&(h>=-.0004)&(h<=L+.0004),axis=1),2,'existing_paired_inclined_columns_yellow_axis_distance_mask')
 paint(box(0,6,46,124,47,2)&yy(-17.5,-13.4),1,'observed_front_roof_edge_gray_not_whole_roof')
 paint(box(14,9,47.8,89,24,1.8),6,'existing_roof_PV_pad_only_not_equipment_or_flat_roof')
 paint(hi[:,2]<=2.4001,0,'neutral_display_base_not_site_ground')
 color[color>4]-=1
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU V2 Landscape Restaurant original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuuv2-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official NUU V2 photo2 EXIF2025; uncalibrated proxies','scope':'Exact existing inclined beams yellow, midbands red, front concrete gray, shaft glazing and existing PV. All original front recess back triangles cross floors, so neutral rather than fake lower glass. Unknown rear/roof/equipment neutral; adjacent T2 and parking shelter excluded.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
