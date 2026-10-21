"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='0a1614814d7e7779999d31def1294e3878262ff0ca56bd19efc9be1924c5930a'
PALETTE=[('neutral_unknown','#AAA79F'),('pale_ivory_stone_ribbons','#C8C4B6'),('muted_cool_window_proxy','#829497'),('olive_gray_tower_window_proxy','#68766B'),('silver_gym_metal_roof','#A6ADAF'),('warm_beige_solid_core','#B7AEA0'),('pale_window_frames','#CED1C6')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_rear_and_unregistered_surfaces_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.001)&(hi[:,2]<=b+.001)
 def xx(a,b):return (lo[:,0]>=a-.001)&(hi[:,0]<=b+.001)
 def yy(a,b):return (lo[:,1]>=a-.001)&(hi[:,1]<=b+.001)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.001,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint(xx(-56,56)&yy(-37,-14)&zz(5.4,80),1,'original_curved_front_stone_walls_ribbons_and_sign_blank')
 def local(t,center,deg):
  a=np.deg2rad(deg);q=t[:,:,:2]-center
  return q@np.array([np.cos(a),np.sin(a)]),q@np.array([-np.sin(a),np.cos(a)])
 for deg in [-16,-8,0,8,16]+list(np.linspace(-16.1,18.8,14)):
  a=np.deg2rad(deg);center=np.array([155*np.sin(a),120-155*np.cos(a)]);u,v=local(t,center,deg)
  rows=[(7,12.5,17.5),(21,8.5,17.5),(40,9,17.5)] if deg in [-16,-8,0,8,16] else [(59.5,10.4,5.4)]
  for z,h,w in rows:
   mask=zz(z,z+h)&np.all(abs(u)<=w/2+.002,axis=1)&np.all(abs(v)<=.826,axis=1)
   paint(mask,6,'original_curved_window_reveal_pale_frame')
   paint(mask&np.all(abs(v-.825)<.002,axis=1),2,'tangent_cut_window_back_only_not_broad_stone_ribbon')
 # Tower source-visible front and left arc; unobserved rear remains neutral.
 d=t[:,:,:2]-np.array([-58,-24]);rad=np.linalg.norm(d,axis=2)
 paint(np.all(rad<=14.01,axis=1)&zz(2.3,89.1)&((n[:,1]<-.05)|(n[:,0]<-.05)|(n[:,2]>.2)),1,'observed_round_tower_stone_mullions_drums_cornices')
 paint(np.all(rad<=7.1,axis=1)&zz(88.7,117),1,'cupola_same_stone_system_bounded_circumferential_material_extension')
 for deg in np.arange(145,361,18):
  a=np.deg2rad(deg);center=np.array([-58+12.6*np.cos(a),-24+12.6*np.sin(a)]);u,v=local(t,center,deg+90)
  for z in np.arange(15,78,7):
   paint(zz(z,z+5.95)&np.all(abs(u)<=1.601,axis=1)&np.all(abs(v-.8)<.002,axis=1),3,'existing_tower_pane_back_olivegray_reflection_proxy_not_intrinsic_tint_claim')
 for deg in range(160,326,24):
  a=np.deg2rad(deg);center=np.array([-58+13.3*np.cos(a),-24+13.3*np.sin(a)]);u,v=local(t,center,deg+90)
  paint(zz(4.8,11)&np.all(abs(u)<=2.101,axis=1)&np.all(abs(v-.8)<.002,axis=1),2,'lower_drum_discrete_recess_not_whole_glass')
 paint(box(54.5,67.5,-38,-37.9,2.3,86.3),5,'observed_solid_right_core_front_beige')
 paint(plane(0,-69)&yy(-10.5,38.5)&zz(5.4,78.7),1,'observed_left_wing_pale_wall')
 for y in [0,7,14,21,28]:
  for z,h,w in [(44,8.6,4.5),(65,4.5,1.7),(15.5,6.9,4.7)]:
   paint(plane(0,-68.25)&yy(y-w/2,y+w/2)&zz(z,z+h),2,'discrete_left_wing_window_back')
 # Mid-level left colonnade is intentionally neutral, not glazing.
 paint(box(-56,56,-10,37,78.7,88.7)&(n[:,2]>.1),4,'same_gym_roof_metal_system_silver_NOT_PV_seams_retained')
 paint(hi[:,2]<=5.5001,0,'neutral_forecourt_and_base')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU J1 Activity Center original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuuj1-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official J1 Activity Center photos1–2; uncalibrated proxies','scope':'Curved ivory stone ribbons, original discrete cool window backs, olivegray reflected tower-pane proxy, pale cupola, solid beige right core and silver gym metal roof not PV. Cupola and roof same-system materials bounded; rear and colonnade neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
