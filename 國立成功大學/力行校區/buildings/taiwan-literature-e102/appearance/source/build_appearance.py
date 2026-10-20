"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='ada5704fb1ac8304846d957c0efca5b27fcce52a2c0b0f481afff60ac21c6882'
PALETTE=[('neutral_unseen','#AAA79F'),('red_brick','#A87361'),('pale_gray_frames_and_sills','#C4C7B9'),('muted_glazing','#73817F'),('gray_steps_and_low_plinth','#969A90'),('visible_roof_gray_proxy','#737570'),('display_base','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_rear_opposite_end_and_far_roof_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.00025)&(hi[:,2]<=b+.00025)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.00025,axis=1)
 paint((plane(1,-31)|plane(0,-66))&zz(4.9,39.9),1,'registered_front_long_wall_and_left_end_brick')
 paint(plane(0,-69)&zz(39,58),1,'registered_left_gable_brick_face')
 for x in [-54,-36,-18,0,18,36,54]:
  scope=(lo[:,0]>=x-3.90025)&(hi[:,0]<=x+3.90025)&(lo[:,1]>=-31.00025)&(hi[:,1]<=-30.19975)&zz(9,30)
  paint(scope&~plane(1,-31),2,'existing_long_window_recess_returns_pale_no_false_front_strip_boundaries')
  for dx in [-2.2,2.2]:
   for z in [9,14.5,20,25.5]:paint((lo[:,0]>=x+dx-1.70025)&(hi[:,0]<=x+dx+1.70025)&plane(1,-30.2)&zz(z,z+4.5),3,'existing_long_window_pane_back_glazing')
  paint((lo[:,0]>=x-5.50025)&(hi[:,0]<=x+5.50025)&(lo[:,1]>=-32.70025)&(hi[:,1]<=-30.69975)&zz(8,9.5),2,'existing_long_window_sill_pale')
 for y in [-6,14]:
  scope=(lo[:,1]>=y-4.20025)&(hi[:,1]<=y+4.20025)&(lo[:,0]>=-66.00025)&(hi[:,0]<=-65.14975)&zz(9,30)
  paint(scope&~plane(0,-66),2,'left_end_window_recess_returns_pale_no_false_front_strip_boundaries')
  for dy in [-2.4,2.4]:
   for z in [9,14.5,20,25.5]:paint((lo[:,1]>=y+dy-1.80025)&(hi[:,1]<=y+dy+1.80025)&plane(0,-65.15)&zz(z,z+4.5),3,'left_end_existing_window_pane_back_glazing')
  paint((lo[:,0]>=-67.70025)&(hi[:,0]<=-65.69975)&(lo[:,1]>=y-5.50025)&(hi[:,1]<=y+5.50025)&zz(8,9.4),2,'left_end_existing_sill_pale')
 paint((lo[:,0]>=-66.00025)&(hi[:,0]<=-64.99975)&(lo[:,1]>=-28.00025)&(hi[:,1]<=-19.99975)&zz(4,26),2,'left_end_door_recess_pale_leaf_proxy_no_invented_glass_panels')
 paint((lo[:,0]>=-69.00025)&(hi[:,0]<=-68.19975)&(lo[:,1]>=-1.90025)&(hi[:,1]<=1.90025)&zz(44,51),0,'gable_vent_neutral_no_unverified_frame')
 paint((lo[:,0]>=-73.00025)&(hi[:,0]<=-64.99975)&(lo[:,1]>=-30.50025)&(hi[:,1]<=-17.49975)&zz(3,5.9),4,'existing_exterior_door_steps_gray')
 paint((plane(1,-31.5)|plane(0,-66.5))&zz(3,4.9),4,'existing_low_plinth_visible_edges_gray_proxy')
 paint(zz(39,58)&(n[:,2]>.1)&(n[:,1]<-.1),5,'registered_near_roof_slope_uniform_gray_proxy_occlusion_disclosed')
 paint(plane(1,-32.85)&zz(39,40.1),2,'existing_front_eave_edge_pale_gray')
 paint(hi[:,2]<=3.0001,6,'display_base_not_site_surface')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCKU Taiwan Literature E102 original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'e102-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official NCKU GIS36474 image, EXIF2010-02-25 metadata only; historical reference not current condition','scope':'Visible long front and left gable, existing pane/frame recesses and sills; near roof uniform gray proxy under tree occlusion, far roof and rear neutral. Original proportions unchanged.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
