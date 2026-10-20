"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='679692bfe930e64f98569bc2142ee51bd1d24f3493fdfb47027438753bb98c17'
PALETTE=[('neutral_unseen','#AAA79F'),('gray_structure','#A2A39B'),('cream_walls','#C7BEA4'),('green_canopy','#317E70'),('muted_glazing','#729397'),('existing_PV','#587A99'),('dark_window_frames','#606D6C')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_ends_roof_and_unsplit_source_boundaries_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0003)&(hi[:,2]<=b+.0003)
 def xx(a,b):return (lo[:,0]>=a-.0003)&(hi[:,0]<=b+.0003)
 def yy(a,b):return (lo[:,1]>=a-.0003)&(hi[:,1]<=b+.0003)
 def plane(y):return np.all(abs(t[:,:,1]-y)<.0003,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(box(-60,60,-33,-10,2.8,29)&(n[:,1]<-.99),1,'observed_D1_front_gray_structure_and_recess_returns')
 paint(box(-60,-28,-33,-10,2.8,29)&(n[:,0]<-.99),2,'observed_D1_left_cream_end')
 paint(box(-20,39,-43,-26,2.8,15)&(n[:,1]<-.99),2,'observed_D1_lower_terrace_cream_wall')
 paint(box(-21,40,-44,-26,14,16.5),1,'existing_D1_terrace_slab_gray')
 # Red right mass is documented, but original front face lacks the real cream cross-band.
 # Both unsplit broad faces stay neutral; no fabricated cream cross-band or all-red claim.
 paint(box(39,60,-33,-32.9,2.8,29),0,'D1_unsplit_front_red_and_cream_band_mixture_neutral')
 paint(box(42,58,-34,-32.9,19,26.5),1,'existing_D1_blank_billboard_frame_no_advertising_text')
 for xa,xb,y,z0,z1 in [(-56,-35,-31.95,7,12.6),(-56,-35,-32,20,25.8),(-16,-2,-41.95,7,12.6),(2,16,-41.95,7,12.6),(20,35,-41.95,7,12.6)]:
  paint(xx(xa,xb)&zz(z0,z1)&plane(y),5,'D1_discrete_original_window_back')
  yf=-33.05 if xa<-30 else -43.05
  for x in np.arange(xa+3.5,xb-1,4.5):paint(box(x,x+.8,yf,yf+1.3,z0-.15,z1+.15),7,'D1_existing_window_vertical_mullions')
  zm=(z0+z1)/2;paint(box(xa-.15,xb+.15,yf,yf+1.3,zm-.4,zm+.4),7,'D1_existing_window_crossbar')
 paint(box(-53,56,24,46,7.8,46)&(n[:,1]<-.99),1,'D2_observed_front_structure_and_corridor_returns_gray_not_glass')
 for z in [12,24,36]:paint(xx(-6.2,50)&zz(z,z+7.5)&plane(30),0,'D2_deep_corridor_back_mixed_doors_windows_neutral_not_glass')
 for x in [-8,11,31,50]:paint(box(x,x+1.8,23.6,30.3,10,46.5),1,'D2_existing_gray_piers')
 for z in [11.5,23.5,35.5,45]:paint(box(-8,53,23.1,31,z,z+1.7),1,'D2_existing_gray_floor_bands')
 for z in [13.1,25.1,37.1]:paint(box(-7,51,23.3,24.5,z,z+1.4),1,'D2_thickened_solid_parapet_not_exact_rail')
 paint(box(-31,-9,19,44,7.8,58)&(n[:,1]<.01)&(n[:,2]<.01),1,'D2_observed_tower_gray_not_glass')
 for z in [11,24,37]:paint(xx(-27,-12)&zz(z,z+8)&plane(23),0,'tower_corridor_back_neutral')
 paint(box(-55,-27,7,27,7.8,32)&(n[:,1]<-.99),2,'D2_cream_entry_pavilion_no_gold_letters')
 for a,b in [(-53,-42),(-40,-29)]:paint(xx(a,b)&zz(10,18)&plane(8.2),5,'D2_existing_entry_window_back')
 paint(box(-55,-27,1.5,9,18,19.8),4,'documented_green_entry_canopy_existing_mesh_only')
 for a,b in [(-54,-52.4),(-29.6,-28)]:paint(box(a,b,2.2,8,7.8,18.4),2,'existing_canopy_supports_cream')
 for a,b,c,d,z,cols,rows in [(-57,-31,-30,-12,30,4,3),(-25,37,-25,-12,29.5,8,2),(42,58,-30,-12,30.9,3,3),(-5,52,28,44,47.4,8,3)]:
  for i in range(cols):
   for j in range(rows):
    x=a+(b-a)*i/cols;y=c+(d-c)*j/rows;paint(box(x,x+(b-a)/cols-.65,y,y+(d-c)/rows-.65,z-.1,z+.75),6,'existing_bonded_PV_tile_only')
 paint(hi[:,2]<=3.0001,0,'neutral_display_base_not_measured_slope')
 color[color>3]-=1
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU D1 D2 Hakka Complex original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuud12-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official NUU D1 photo4 and D2 photo1 EXIF2025; uncalibrated proxies','scope':'Source-registered front only; gray/cream, green existing canopy, discrete window backs and PV. D2 corridors not glass. Unsplit D1 right mass red/cream crossband neutral on both broad faces. Unknown rear/roof neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
