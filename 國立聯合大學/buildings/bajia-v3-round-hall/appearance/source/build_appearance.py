"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='4861e12f2c5bfa73b6a60bf596b2484e485a573d1eda4787c690050a502e95d9'
PALETTE=[('neutral_unseen','#AAA79F'),('salmon_tile','#AD8580'),('blue_gray_mosaic','#8297A0'),('cream_inner_parapet','#D2D0C3'),('muted_glazing','#425B60'),('gray_paving_and_cap','#99968E'),('olive_gray_frame','#7B847D'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_back_or_unregistered_surface_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def xx(a,b):return (lo[:,0]>=a-.00025)&(hi[:,0]<=b+.00025)
 def yy(a,b):return (lo[:,1]>=a-.00025)&(hi[:,1]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 # Front half only, no triangle splitting to manufacture absent mosaic bands.
 paint(yy(-41,6)&zz(2.4,45.3)&(n[:,1]<-.1),1,'observed_front_elliptical_wall_tile_no_added_horizontal_bands')
 # Original tangent window cuts; back planes only are glazing, returns remain wall.
 for deg in [-165,-135,-105,-75,-45,-15]:
  rad=np.deg2rad(deg);origin=np.array([57*np.cos(rad),6+46*np.sin(rad)])
  norm=np.array([np.cos(rad)/57,np.sin(rad)/46]);norm/=np.linalg.norm(norm)
  tangent=np.array([norm[1],-norm[0]])
  local_y=(t[:,:,:2]-origin)@norm;local_x=(t[:,:,:2]-origin)@tangent
  for z in ([30] if deg==-75 else [9,30]):
   back=np.all(abs(local_y+1.1)<.0004,axis=1)&np.all(abs(local_x)<=6.5004,axis=1)&zz(z,z+10)
   paint(back,0 if deg in [-165,-15] else 4,'end_opening_neutral_not_glass' if deg in [-165,-15] else 'existing_front_tangent_window_recess_back_only_glazing')
 # Entire roof terrace and inner parapet are visible from elevated photo; exterior back remains unknown.
 paint(plane(2,45.3),5,'observed_roof_terrace_paving_no_equipment')
 radial=c[:,:2]-[0,6];outdot=(radial*n[:,:2]).sum(axis=1)
 paint(zz(45,49)&(abs(n[:,2])<.1)&(outdot<0),3,'observed_inner_parapet_cream_full_visible_ring')
 paint(zz(45,49)&(abs(n[:,2])<.1)&(outdot>0)&yy(-41,6),1,'front_outer_parapet_salmon_tile')
 paint(plane(2,49),2,'observed_parapet_top_blue_gray_mosaic')
 paint(xx(-41,-23)&yy(1.5,22.5)&zz(2.4,70.3)&(n[:,1]<.1),1,'visible_tower_front_and_sides_tile_back_neutral')
 paint(xx(-42,-22)&yy(.5,23.5)&zz(56,58)&(n[:,1]<.1),2,'existing_tower_band_blue_gray_proxy')
 paint(xx(-40.5,-23.5)&yy(2,22)&zz(69.8,79.8)&(n[:,1]<.1),5,'source_tower_upper_cap_light_gray_visible_surfaces')
 paint(xx(-37,-27)&plane(1,1.7)&zz(57,67),0,'tower_recess_uncertain_opening_neutral_not_glass')
 paint(xx(-2,38)&yy(-54.5,-27.5)&zz(2.4,21.3)&(n[:,1]<.1),1,'existing_simplified_annex_front_sides_tile_not_reconstructed_curve')
 paint(xx(-3.5,39.5)&yy(-55.5,-26.5)&zz(21,23),2,'existing_annex_roof_rim_blue_gray_mosaic_proxy')
 paint(plane(2,23),5,'annex_terrace_gray_paving_proxy')
 paint(xx(6.5,29.5)&plane(1,-53.8)&zz(4.5,18.5),4,'existing_annex_entry_recess_back_glazing')
 for x in [10,18,26]:paint(xx(x-.6,x+.6)&yy(-55.5,-53.7)&zz(4.4,18.7),6,'existing_entry_mullions_olive_gray')
 paint(xx(-2,38)&yy(-57.5,-54.5)&zz(18,20),2,'existing_entry_canopy_blue_gray_not_signboard')
 paint((xx(-64,-54)|xx(54,64))&yy(-30.1,10.1)&zz(2.4,25.1),5,'observed_side_access_stairs_gray_no_added_rails')
 paint(hi[:,2]<=2.4001,7,'neutral_display_base_not_site_paving')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU Bajia Round Hall original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuuround-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NUU photos6 and7; historical photo evidence, not current survey','scope':'Front ellipse and source-visible terrace/tower/annex only. Rear exterior neutral; absent mosaic bands not invented. Existing square annex and tower are simplified proxies. No equipment, lettering or texture added.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
