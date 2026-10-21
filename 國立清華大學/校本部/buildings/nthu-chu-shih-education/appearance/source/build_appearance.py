"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='eff1a406b54db47994b49d8456d9621991573a531ebf3a5463b949069b9b8dc3'
PALETTE=[('neutral_unknown_or_mixed','#AAA79F'),('muted_red_steel','#A65E59'),('warm_ochre_low_hall_brick','#AB855B'),('pale_aluminum_rib_roof','#B7BCB9'),('offwhite_concrete','#D0D1C8'),('dark_muted_window_proxy','#667371')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_or_mixed_brick_band_and_glass_infill_surfaces_neutral',dtype=object)
 def paint(m,k,r):color[m]=k;why[m]=r
 def zz(a,b):return (lo[:,2]>=a-.004)&(hi[:,2]<=b+.004)
 def xx(a,b):return (lo[:,0]>=a-.004)&(hi[:,0]<=b+.004)
 def yy(a,b):return (lo[:,1]>=a-.004)&(hi[:,1]<=b+.004)
 def plane(i,v):return np.all(abs(t[:,:,i]-v)<.004,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 # Original whole members only. All thin triangular diagonals sit in the isolated overhead band.
 for x in [-61,-45]:paint(box(x-1.2,x+1.2,-46,-42,3,112),1,'source_red_steel_screen_posts')
 for z in range(5,109,10):paint(box(-62,-44,-46,-42,z,z+1.8),1,'source_red_steel_screen_rails')
 for x in [-57,-53,-49]:paint(box(x-.55,x+.55,-45.3,-42.7,3,112),1,'source_red_steel_screen_fine_posts_no_perforated_mesh_added')
 paint(box(-63,63,-46.5,-41.5,100,112.4),1,'source_existing_red_steel_overhead_truss_whole_members')
 paint(box(59,63,-46,-32,110,112.4),1,'source_exposed_upper_steel_end_support_not_brick_tower')
 # Low hall visible front and left; top metal roof independently visible in aerial.
 paint(zz(3,31)&((plane(1,-63.5)&xx(-7,47))|(plane(0,-7)&yy(-63.5,-20.5))),2,'source_low_hall_front_and_left_ochre_brick_not_tall_core')
 for x in [0,10,20,30,40]:paint(box(x-1,x+1,-66.5,-61.5,5,28)&plane(1,-66.5),2,'source_low_hall_existing_fin_front_only_uncertain_sides_neutral')
 paint(box(-8,48,-64,-20,31,32.9)&(norm[:,2]>.0001),3,'aerial_source_confirmed_low_hall_ribbed_metal_roof_top')
 # Attached low white core front and right visibly isolated from tall brick tower.
 paint(zz(3,29)&((plane(1,-59)&xx(47,65))|(plane(0,65)&yy(-59,-37))),4,'source_visible_attached_white_core_front_right')
 for x in [51,60]:
  for z in [9,19]:paint(plane(1,-58)&xx(x-1.4,x+1.4)&zz(z,z+3),5,'source_discrete_attached_core_window_backs')
 paint(plane(1,-62.25)&xx(6.5,13.5)&zz(22,24.5),5,'source_low_hall_discrete_small_front_window')
 # Courtyard is predominantly white structure; mixed long window backs remain neutral.
 paint(zz(3,103)&((plane(0,-34)&yy(-41,59))|(plane(0,31)&yy(-37,61))|(plane(1,35)&xx(-51,51))),4,'source_registered_courtyard_white_structure_not_recessed_mixed_glass_spandrels')
 for side,y,z,w in [(-1,-8,23,28),(-1,24,47,28),(1,-10,35,23),(1,24,23,27),(1,25,59,23)]:
  x=-32 if side<0 else 29
  for h in [z,z+10]:paint(box(x-3,x+3,y-w/2,y+w/2,h,h+2),4,'source_projecting_white_courtyard_frame_component')
  for v in [y-w/2+1,y+w/2-1]:paint(box(x-3,x+3,v-1,v+1,z,z+12),4,'source_projecting_white_courtyard_frame_component')
 paint(hi[:,2]<=3.0001,0,'unsplit_base_neutral')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTHU Chu Shih Education Bounded Appearance original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nthuchushi-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official NTHU archive PDF page6 as-built aerial and courtyard photographs; capture dates unknown, document dates not capture; uncalibrated proxies','scope':'Existing red steel screen/truss, visible ochre low hall, aerial-confirmed silver ribbed roof, white attached core and courtyard structural faces. Tall brick tower crosses unmodeled gray bands and stays neutral; long window backs mix opaque infill and glazing so remain neutral; unknown rear/roof neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
