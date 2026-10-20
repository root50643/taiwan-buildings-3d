"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='a886d8fc6898f95b2de9455ee9c0b1a9c8415d2b24609dccafb19c8d8cb12717'
PALETTE=[('neutral_unseen','#AAA79F'),('courtyard_gray_wall','#9FA5A4'),('pale_structure','#C6CAC3'),('muted_green_glazing','#548C82'),('sage_metal_roof','#75948C'),('blue_PV','#567490'),('courtyard_grass','#849B60'),('gray_paving','#AAACA3')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_outer_rear_unresolved_brick_bands_and_display_base_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0004)&(hi[:,2]<=b+.0004)
 def xx(a,b):return (lo[:,0]>=a-.0004)&(hi[:,0]<=b+.0004)
 def yy(a,b):return (lo[:,1]>=a-.0004)&(hi[:,1]<=b+.0004)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.0004,axis=1)
 def box(x,y,z,w,d,h):return xx(x-w/2,x+w/2)&yy(y-d/2,y+d/2)&zz(z-h/2,z+h/2)
 for x in [-39,39]:paint(plane(0,x)&yy(-54,44)&zz(3,43),1,'observed_courtyard_wing_wall_gray_proxy_no_fake_brick_stripes')
 paint(plane(1,28)&xx(-61,61)&zz(3,43),1,'observed_rear_wing_courtyard_front_gray_proxy')
 for z in [11,19,27,35]:
  for x in [-50,50]:paint(box(x,4,z,22.7,80,.8)&((hi[:,0]<0)&(n[:,0]>.1)|(lo[:,0]>0)&(n[:,0]<-.1)),2,'original_inner_floor_bands_pale')
  paint(box(0,39,z,122,22.7,.8)&(n[:,1]<-.1),2,'original_back_wing_front_floor_bands_pale')
 for x in [-38.8,38.8]:
  for y in [-29,-17,-5,7,19]:paint(box(x,y,23,1,1.3,40),2,'existing_courtyard_piers_pale')
 for x in [-57,-37,-19,19,37,57]:paint(box(x,27.7,23,1.4,1,40),2,'existing_rear_courtyard_piers_pale')
 paint(box(0,27.3,26.3,21,4.2,46.6)&(n[:,1]<-.1),2,'existing_center_entry_front_frame_pale')
 for x in [-39,39]:
  back=x-.75 if x<0 else x+.75
  for y in [-27,-15,-3,9,21,33]:
   for z in [7.1,15.1,23.1,31.1,39.1]:
    for dy in [-2.5,2.5]:paint(plane(0,back)&yy(y+dy-1.9,y+dy+1.9)&zz(z-1.7,z+1.7),3,'existing_inner_wing_paired_window_backs_not_continuous_glass_tower')
 for x in [-53,-41,-29,-17,17,29,41,53]:
  for z in [7.1,15.1,23.1,31.1,39.1]:
   for dx in [-2.5,2.5]:paint(plane(1,28.75)&xx(x+dx-1.9,x+dx+1.9)&zz(z-1.7,z+1.7),3,'existing_rear_wing_courtyard_window_backs')
 for z in [8,16,24,32,40,46]:
  for x in [-6.5,0,6.5]:paint(plane(1,25.85)&xx(x-2.3,x+2.3)&zz(z-(2.1 if z<46 else 1.25),z+(2.1 if z<46 else 1.25)),3,'existing_center_entry_discrete_window_backs')
 for x in [-38.8,38.8]:
  back=x-.9 if x<0 else x+.9
  for z in [9,16,23,30,37]:paint(plane(0,back)&yy(-23.1,-20.9)&zz(z-2.9,z+2.9),3,'existing_narrow_stair_glazing_only_no_solid_wall_tower_fabrication')
 # Only genuine inclined roof planes, not arbitrary elevated facade faces.
 slope=(n[:,2]>.35)&(n[:,2]<.999)
 for x in [-50,50]:
  paint(box(x,4,46.6,24,82,5)&slope,4,'existing_side_gable_sage_metal_roof')
  paint(box(x,-42,34.4,24,26,2.8)&slope,4,'existing_front_hip_sage_roof')
  paint(box(x,7,51.1,9,23,1.4)&slope,4,'existing_side_vent_gable_sage_roof')
 paint(box(0,39,46.5,124,24,4.8)&slope,4,'existing_rear_gable_sage_roof')
 paint(box(0,34.5,52.75,24,19,5.1)&slope,4,'existing_center_shed_sage_roof')
 for x in [-51,51]:paint(box(x,43,56.05,13,13,4.3)&slope,4,'existing_corner_lantern_hip_sage_roof')
 for x in [-30,30]:paint(box(x,39,50.15,22,8,1.1)&slope,4,'existing_rear_vent_gable_sage_roof')
 def panel(x,y,w,d,fn):
  z=fn(t[:,:,0],t[:,:,1]);paint(xx(x-w/2,x+w/2)&yy(y-d/2,y+d/2)&np.all((t[:,:,2]>=z-.1504)&(t[:,:,2]<=z+.6504),axis=1),5,'existing_bonded_PV_cell_only_preserve_roof_gaps')
 for wing in [-50,50]:
  inward=1 if wing<0 else -1
  for off in [3.1,6.2,9.3]:
   for y in np.arange(-28,30,6.5):panel(wing+inward*off,float(y),2.4,5.8,lambda x,y,w=wing:49.1-abs(x-w)*5/12)
 for side in [-1,1]:
  for x in np.arange(14,46,5.5):
   for y in [29.2,32.4,35.6]:panel(side*float(x),y,4.8,2.5,lambda x,y:48.9-(39-y)*4.8/12)
 for x in [-8.1,-2.7,2.7,8.1]:
  for y in [27.3,31.8,36.3,40.8]:panel(x,y,4.6,3.8,lambda x,y:50.9+(y-25)*4.4/19)
 paint(xx(-39,39)&yy(-47,29)&plane(2,3.6),6,'existing_courtyard_nonpath_top_grass_only_not_base')
 paint(box(0,-17,3.9,4.5,78,.8),7,'existing_central_walkway_gray')
 for y in [-48,-37,-26,-15,-4,7,18]:paint(box(0,y,3.9,74,1.3,.8),7,'existing_transverse_walkway_gray')
 for x in [-36.5,36.5]:paint(box(x,-12,3.85,2,72,.7),7,'existing_longitudinal_walkway_gray')
 paint(xx(-12.5,12.5)&yy(14,26)&zz(3,5.2),7,'existing_compressed_entry_landing_steps_gray')
 paint(hi[:,2]<=3.0001,0,'neutral_display_base_not_site_ground')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU A2 Science Engineering Courtyard original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuua2-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official A2 gallery photos26/27 EXIF2025 primary plus undated historical aerial registration; uncalibrated proxies','scope':'Courtyard walls and discrete glazing only; no invented continuous glass towers or brick bands across unsplit faces. Genuine sage inclined roofs, original PV cells, grass top and gray paths. Unknown exterior/rear neutral. Preserve original substantial geometry simplifications.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
