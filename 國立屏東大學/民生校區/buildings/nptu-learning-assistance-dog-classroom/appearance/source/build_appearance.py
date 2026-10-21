"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='8d35b5f952938914a2b2615591195676ef953275ffa9bdb609e55a12811bff9e'
PALETTE=[('neutral_unregistered_or_mixed','#AAA79F'),('offwhite_siding_posts_gable','#D2D1C5'),('muted_brick_plinth','#A76C52'),('charcoal_roof','#545C5A'),('muted_window_mesh_proxy','#82908A'),('gray_veranda_steps','#969C96')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_left_gable_rear_fenced_wall_mixed_doors_base_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.004)&(hi[:,2]<=b+.004)
 def xx(a,b):return (lo[:,0]>=a-.004)&(hi[:,0]<=b+.004)
 def yy(a,b):return (lo[:,1]>=a-.004)&(hi[:,1]<=b+.004)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(box(-55,55,-26,-24.6,9.8,31),1,'source_registered_front_siding_and_existing_engraved_joint_faces_not_green_tree_cast')
 paint(box(53.6,55,-26,26,9.8,31),1,'source_registered_right_siding_existing_grooves')
 paint(plane(0,57.5)&yy(-29,29)&zz(30.3,49),1,'source_right_triangular_gable_siding_not_charcoal_roof')
 paint((plane(1,-26.5)&xx(-55.5,55.5)|plane(0,55.5)&yy(-26.5,26.5))&zz(2.8,9.8),2,'source_registered_front_and_right_integrated_brick_plinth_vertical_faces_only')
 for x in [-52,-18,18,52]:paint(box(x-1.4,x+1.4,-45.4,-42.6,4.3,26.5),1,'source_white_veranda_posts_whole_existing_component')
 roof=np.all(abs(t[:,:,2]-(49-(18.7/29)*abs(t[:,:,1])))<.004,axis=1)
 paint(roof&xx(-57.5,57.5)&yy(-29,29)&(norm[:,2]>.0001),3,'source_main_pitched_roof_slopes_only_gable_ends_excluded')
 paint(box(-58,58,-.9,.9,48.4,49.8),3,'source_ridge_cap_same_charcoal_roof_system')
 front=np.all(abs(t[:,:,2]-(27+(t[:,:,1]+46)*5/21))<.004,axis=1)
 paint(front&xx(-57.5,57.5)&yy(-46,-25)&(norm[:,2]>.0001),3,'source_front_veranda_sloped_roof_top_only')
 rear=np.all(abs(t[:,:,2]-(26.8-(t[:,:,1]-25)*3.2/14))<.004,axis=1)
 paint(rear&xx(-57,57)&yy(25,39)&(norm[:,2]>.0001),3,'source_visible_rear_lean_to_roof_top_only')
 paint(box(-57.5,57.5,-46.65,-45.35,25.2,26.6),3,'source_existing_front_roof_edge_protection_component')
 for x in [-39,10,37]:
  for dx in [-2.25,2.25]:paint(plane(1,-24.7)&xx(x+dx-1.65,x+dx+1.65)&zz(11.3,22.5),4,'source_front_discrete_window_back_glass_mesh_proxy')
 for y in [-17,17]:paint(plane(0,53.6)&yy(y-4.1,y+4.1)&zz(17,22.5),4,'source_right_short_window_back_glass_mesh_proxy')
 paint(box(-57.5,57.5,-47.5,-24.5,2.8,4.6),5,'source_simplified_gray_veranda_floor')
 for i in range(3):paint(box(-25.5,-6.5,-52.95+i*1.6,-51.05+i*1.6,2.8,3.3+.5*i),5,'source_simplified_entry_steps')
 paint(hi[:,2]<=3.0001,0,'unsplit_ground_base_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NPTU Learning Assistance Dog Classroom Bounded Appearance original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nptudog-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'NPTU official complete photos camera Original2018-10-09,2019-06-28,2018-10-11; modification separate. Offwhite siding not green cast, charcoal slopes not white gable, brick plinth only existing belt','scope':'One classroom main house, not three gallery-label buildings. Source-registered front/right siding and brick plinth, white posts, exact roof slope tops and ridge, separate window backs. Mixed white/glass doors, fenced rear walls/windows, opposite end and base neutral. No fence/grout/roofcorrugation/logo invented, geometry unchanged.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
