"""STUST new covered sports court / 南臺科技大學新風雨球場. Photo-proportion exterior approximation."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[('concrete','#999D98',255),('court_green','#789C57',255),('steel_green','#558B69',255),('column_padding','#294F47',255),('roof_metal','#CDD3D0',255),('court_blue','#419AC2',255),('court_red','#B85C49',255),('court_lines','#F0EEDB',255),('backboard_blue','#244B9B',255)]
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
def box(c,s,col,name):add(Manifold.cube(s,True).translate(c),col,name)
def beam(a,b,w,col,name):
 a=np.array(a);b=np.array(b);d=b-a;L=np.linalg.norm(d);z=d/L;x=np.cross(z,[0,1,0])
 if np.linalg.norm(x)<.01:x=np.cross(z,[1,0,0])
 x/=np.linalg.norm(x);y=np.cross(z,x);T=np.column_stack([x,y,z,(a+b)/2]);add(Manifold.cube((w,w,L+w*.15),True).transform(T),col,name)
def path(points,w,col,name):
 for a,b in zip(points,points[1:]):beam(a,b,w,col,name)
def ring(x,y,z,s,w,col,name):
 for a,b in [((-s/2,-s/2),(s/2,-s/2)),((s/2,-s/2),(s/2,s/2)),((s/2,s/2),(-s/2,s/2)),((-s/2,s/2),(-s/2,-s/2))]:beam((x+a[0],y+a[1],z),(x+b[0],y+b[1],z),w,col,name)

# Display millimetres. +X east, +Y north old-shed junction, -Y south open end.
# 245 by107 mm roof approximate 73.5 by32.2 m plan proportions, NOT surveyed scale.
box((-3,0,1.5),(130,250,3),0,'bounded_display_ground')
box((0,0,3.15),(110,246,.5),1,'green_court_apron')
# Court finish layers overlap underlying display slabs; no disconnected decals.
for j,y in enumerate([-90,-30,30,90]):
 box((0,y,3.43),(94,50,.35),5,f'court_{j+1}_blue')
 for x in [-37,37]:box((x,y,3.65),(20,17,.3),6,'red_key')
 add(Manifold.cylinder(.3,6,6,48).translate((0,y,3.55)),6,'red_center_circle')
 # Raised marking widths are an intentional display simplification.
 for x in [-47,47,0]:box((x,y,3.84),(.35,50,.22),7,'white_court_line')
 for yy in [y-25,y+25]:box((0,yy,3.84),(94,.35,.22),7,'white_court_line')
 for x in [-37,37]:
  for yy in [y-8.5,y+8.5]:box((x,yy,3.87),(20,.35,.22),7,'key_line')
  box((x-10 if x>0 else x+10,y,3.87),(.35,17,.22),7,'key_line')
 # Rings are actual closed annular solids merged into court top.
 for cx,rad in [(0,6),(-27,6),(27,6)]:
  ringmesh=(Manifold.cylinder(.25,rad+.18,rad+.18,48)-Manifold.cylinder(.5,rad-.18,rad-.18,48).translate((0,0,-.1))).translate((cx,y,3.71))
  add(ringmesh,7,'white_circle')
# West seating terraces interrupted at a circulation stair; no east mirror.
for lo,hi in [(-120,-16),(-4,112)]:
 for i in range(3):box((-57-i*2.8,(lo+hi)/2,3.6+i*.75),(3.1,hi-lo,1.7+i*1.5),0,'west_terrace_step')
for i in range(6):box((-56-i*1.4,-10,3.2+i*.4),(1.6,12,1+i*.8),0,'west_access_stair_break')
# 9 main portals: two genuine I-profile columns per frame, no midspan pillars.
ys=list(np.linspace(-120,120,9))
for k,y in enumerate(ys):
 for x in [-53,53]:
  box((x,y,19.5),(1.8,.75,33),2,f'primary_column_web_{k}_{x}')
  for xx in [x-.9,x+.9]:box((xx,y,19.5),(.55,2.3,33),2,f'primary_column_flange_{k}_{x}')
  add(Manifold.cylinder(5.5,1.9,1.9,24).translate((x,y,3.2)),3,'dark_round_protective_padding_not_foundation')
 # Lower frame boundary is folded shoulder, separate from thin dual-pitch roof.
 path([(-53,y,24),(-46,y,28),(-35,y,32),(-15,y,36.4),(0,y,38),(15,y,36.4),(35,y,32),(46,y,28),(53,y,24)],1.6,2,f'portal_beam_folded_lower_shoulder_{k}')
 # Uprights tie folded main beam to upper roof system; voids remain open.
 for x in [-35,0,35]:
  lower=38 if x==0 else 32
  beam((x,y,lower),(x,y,42-abs(x)*6/55),1.1,2,'portal_short_vertical_tie')
# Roof outer surface: shallow planar slopes, not an arched sheet.
for pts in [[(-55,36),(0,42),(0,42.85),(-55,36.85)],[(0,42),(55,36),(55,36.85),(0,42.85)]]:
 add(CrossSection([pts]).extrude(245).rotate((90,0,0)).translate((0,122.5,0)),4,'thin_shallow_dual_pitch_roof')
for x in np.linspace(-53,53,13):
 z=42-abs(x)*6/55
 box((x,0,z-.6),(1,243,1.5),2,'longitudinal_purlin')
for x in [-53,53]:box((x,0,29),(1.2,242,1.2),2,'side_tie_beam')
# East only: 160 approximate blades, each with a distinct outward folded foot.
for y in np.linspace(-119,119,160):
 if min(abs(y-yy) for yy in ys)<1.6:continue # clear primary-column flange zones
 path([(53.3,y,35.8),(53.3,y,22),(54.5,y,18),(55.2,y,16.5)],.65,2,'east_folded_sunshade_blade_approx_count')
for z,x in [(34,53.3),(25,53.3),(18.2,54.4)]:box((x,0,z),(.9,240,.8),2,'east_shade_horizontal_tie')
# Eight column-mounted hoops, four along each side. Nets omitted; transparent board simplified open frame.
for y in [-90,-30,30,90]:
 for sign in [-1,1]:
  x=53*sign;xx=45.5*sign
  beam((x,y,14),(xx,y,14),.9,2,'hoop_arm')
  beam((x,y,20),(xx,y,14),.65,2,'hoop_diagonal')
  for yy in [y-3,y+3]:box((xx,yy,16),( .6,.55,4),7,'backboard_open_frame')
  for z in [14,18]:box((xx,y,z),(.6,6.5,.6),7,'backboard_open_frame')
  box((xx,y,14),(.8,6.7,.8),8,'backboard_blue_lower_edge')
  hoop=(Manifold.cylinder(.5,.95,.95,24)-Manifold.cylinder(.8,.55,.55,24).translate((0,0,-.1))).translate((xx-sign*.9,y,13.8));add(hoop,6,'basket_ring_no_net')
FEATURES=dict(name='南臺科技大學新風雨球場',school='南臺科技大學',slug='stust-covered-sports-court',selected_version='2020 completed early roof; no later PV',estimated_not_surveyed=True,main_portals=9,main_columns=18,longitudinal_bays=8,east_shade_only=True,west_interrupted_terraces=True,north_old_yellow_shed_excluded=True,both_ends_open=True,no_midspan_columns=True,no_invented_end_walls=True,roof_shallow_dual_pitch=True,beam_folded_lower_edge_separate_from_roof=True,basketball_courts=4,no_actual_print=True,support_free_certified=False,all_materials_opaque=True)
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.0005).simplify(.0005)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
centers=vs[fs].mean(axis=1);colors=np.empty(len(fs),dtype=int);maxdist=0
for start in range(0,len(fs),500):
 closest,dist,idx=trimesh.proximity.closest_point(source_tm,centers[start:start+500]);assert dist.max()<.002,dist.max();maxdist=max(maxdist,float(dist.max()));colors[start:start+500]=source_colors[idx]
t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Export exact float32 triangles with analytically normalized normals; no small-face threshold.
tri=np.asarray(t.triangles,dtype=np.float32);cr=np.cross(tri[:,1].astype(float)-tri[:,0],tri[:,2].astype(float)-tri[:,0]);nn=cr/np.linalg.norm(cr,axis=1)[:,None]
buf=bytearray(80)+struct.pack('<I',len(tri))
for nor,face in zip(nn,tri):buf+=struct.pack('<12fH',*nor,*face.ravel(),0)
(O/'model.stl').write_bytes(buf);raw=bytes(buf);n=len(tri)
rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n)
v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
assert np.array_equal(v[f],np.asarray(t.triangles,dtype=np.float32))
t=trimesh.Trimesh(v,f,process=False)
features=FEATURES
features.update(material_provenance_nearest_surface_max_distance_mm=maxdist,parts=part_records)
(O/'qa/design-features.json').write_text(json.dumps(features,ensure_ascii=False,indent=2)+'\n')
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b,'alpha':c} for a,b,c in palette]},indent=2)+'\n')
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns)
def el(p,name,attrs={}):return ET.SubElement(p,'{'+ns+'}'+name,{k:str(v) for k,v in attrs.items()})
r=ET.Element('{'+ns+'}model',{'unit':'millimeter','xml:lang':'en-US'});res=el(r,'resources');bm=el(res,'basematerials',{'id':2})
for a,b,c in palette:el(bm,'base',{'name':a,'displaycolor':b+f'{c:02X}'})
obj=el(res,'object',{'id':1,'type':'model','pid':2,'pindex':0});mm=el(obj,'mesh');vs=el(mm,'vertices');ts=el(mm,'triangles')
for q in v:el(vs,'vertex',dict(zip('xyz',[repr(float(a)) for a in q])))
for tri,col in zip(f,colors):el(ts,'triangle',{'v1':tri[0],'v2':tri[1],'v3':tri[2],'pid':2,'p1':col,'p2':col,'p3':col})
b=el(r,'build');el(b,'item',{'objectid':1})
files={'3D/3dmodel.model':ET.tostring(r,encoding='utf-8',xml_declaration=True),'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'}
with zipfile.ZipFile(O/'model.3mf','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items():info=zipfile.ZipInfo(name,(2026,10,21,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256(raw).hexdigest()}))
