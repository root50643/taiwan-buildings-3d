"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='d0bf7fddba8a87f5cde77e58df8fb956a53a29217542d0af40f22d631765d6b4'
PALETTE=[('neutral_unknown','#AAA79F'),('pale_ivory_front_grid','#C6C5BD'),('pale_warmgray_end_cores','#BDB4AD'),('muted_bluegreen_glazing_proxy','#6C8586'),('window_frame_gray','#8E9998'),('gray_lilac_central_parapets','#B1A9AA'),('warmgray_entrance_stone','#ADA99F'),('visible_roof_support_gray','#7D888A')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_rear_flatroof_and_PV_unconfirmed_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.001)&(hi[:,2]<=b+.001)
 def xx(a,b):return (lo[:,0]>=a-.001)&(hi[:,0]<=b+.001)
 def yy(a,b):return (lo[:,1]>=a-.001)&(hi[:,1]<=b+.001)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.001,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(plane(1,-10)&xx(-66,66)&zz(4.3,104.3),1,'front_pale_ivory_structural_grid')
 for x,top in [(-61,114.3),(61,120.3)]:paint(box(x-5,x+5,-11,-10,4.3,top),2,'registered_pale_warmgray_front_end_cores')
 paint(xx(-54,54)&zz(5.8,98.7)&plane(1,-9.25),3,'original_discrete_front_window_recess_backs')
 paint(box(-54,54,-10.75,-10,5.8,91)&(hi[:,1]<-10.001),4,'original_projecting_window_mullions_gray_not_glazing')
 paint(box(-9.3,9.3,-11.7,-10,38,92.3),1,'central_window_stack_pale_solid_wall')
 for z in [39.4,49,58.6,68.2,77.8,87.4]:
  paint(xx(-8.4,8.4)&zz(z,z+5)&plane(1,-11),3,'central_stack_window_recess_back_not_sill_band')
  for x in [-6.5,-3.25,0,3.25,6.5]:paint(box(x-.4,x+.4,-12.4,-11,z-.1,z+5.1),4,'central_original_mullion_gray')
 for z in [38,47.6,57.2,66.8,76.4]:paint(box(-9.6,9.6,-13.9,-10.5,z,z+3.1),5,'solid_central_parapet_band_gray_lilac_NOT_glass')
 paint(xx(-22,22)&yy(-22.3,-10)&zz(21.3,36.7),6,'curved_entry_stone_drum_and_bands')
 for deg in [-165,-145,-125,-105,-85,-65,-45,-25,-5]:
  rad=np.deg2rad(deg);center=np.array([21*np.cos(rad),-10.5+11.2*np.sin(rad)]);normal=np.array([np.cos(rad)/21,np.sin(rad)/11.2]);normal/=np.linalg.norm(normal);tan=np.array([-normal[1],normal[0]])
  q=t[:,:,:2]-center;depth=q@normal;along=q@tan
  paint(zz(25.2,31.9)&np.all(abs(depth+.8)<.002,axis=1)&np.all(abs(along)<=1.801,axis=1),3,'original_tangent_curved_window_back_only_not_stone_bands')
 paint(xx(-9,9)&zz(4.8,21.1)&plane(1,-9.2),3,'recessed_main_entry_glazing_back')
 paint(box(-9.1,9.1,-10.5,-9.2,4.7,21.2)&~plane(1,-9.2),4,'entry_original_mullions_and_transoms_gray')
 for x,y in [(-18,-15.8),(-11.4,-20),(11.4,-20),(18,-15.8)]:paint(box(x-2.05,x+2.05,y-2.05,y+2.05,4.1,21.8),6,'four_pale_stone_entry_columns')
 for z in [7.4+9.6*i for i in range(10)]:
  paint(plane(0,68)&yy(-2.75,20.75)&zz(z,z+6),3,'photo_supported_right_outer_discrete_window_back')
 paint(box(-50.7,50.7,-3.8,23.8,105.2,110.7)&(hi[:,2]<109),7,'visible_lower_roof_metal_supports_only_no_PV_top_claim')
 paint(hi[:,2]<=4.4001,0,'neutral_base_and_forecourt')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU H1 Innovation Outreach Hall original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuuh1-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official H1 Innovation Outreach photos1–2; uncalibrated proxies','scope':'Front pale grid and warmgray end cores, discrete muted bluegreen windows, original gray frames, central solid lilac parapets and stone entrance. Only established right side window recesses; unseen left and rear neutral. Rooftop PV material unproven, top neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
