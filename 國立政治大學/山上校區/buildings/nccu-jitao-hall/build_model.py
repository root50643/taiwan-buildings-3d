"""Jitao Hall complete main building: private proportional source study, not survey."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection,JoinType,FillRule
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
SCALE=3.0
palette=[('pale_exposed_concrete','#B9B7AC',255),('red_brown_brick','#905D49',255),('dark_glazed_stair','#374B52',255),('opaque_window_proxy','#6F8385',255),('pale_window_frames','#D4D7CD',255),('slope_base_proxy','#827D69',255)]
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
def CS(p,**kw):return CrossSection(p,fillrule=FillRule.EvenOdd)
def poly(p,z0,z1):return CS([p]).extrude(z1-z0).translate((0,0,z0))
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def block(x0,x1,y0,y1,z0,z1,c,n):add(cube(x0,x1,y0,y1,z0,z1),c,n)
def beam(a,b,w,c,n):
 a=np.array(a);b=np.array(b);d=b-a;L=np.linalg.norm(d);z=d/L;x=np.cross(z,[0,1,0])
 if np.linalg.norm(x)<.01:x=np.cross(z,[1,0,0])
 x/=np.linalg.norm(x);y=np.cross(z,x);add(Manifold.cube((w,w,L+w*.1),True).transform(np.column_stack([x,y,z,(a+b)/2])),c,n)
def canon(points):return [((x-855)/20,(589-y)/20) for x,y in points]
# Shared stair root is (855,589) in high-resolution2F; X right,Y up. NOT source compass.
right=canon([(855,589),(1458,589),(1458,721),(919,721),(855,657)])
lower=canon([(755,670),(855,589),(919,657),(919,721),(635,1005),(568,938),(575,880),(561,867)])
low_annex=canon([(633,1003),(829,807),(908,867),(908,923),(720,1109),(625,1014)])
upper=canon([(381,469),(730,125),(1020,125),(1020,255),(915,255),(915,328),(809,328),(557,579),(503,526),(480,550),(455,542)])
upper5=canon([(381,469),(730,125),(919,125),(919,245),(881,245),(881,328),(809,328),(557,579),(503,526),(480,550),(455,542)])
r_source_pixels=[(504,542),(832,214),(958,214),(958,191),(1048,191),(1048,316),(1010,316),(1010,378),(938,378),(685,632),(630,577),(589,620)]
r_outline=[((x-112.5-873)/20/1.022,(638-(y-5))/20/1.022) for x,y in r_source_pixels]
connector=canon([(881,255),(1020,255),(1020,527),(985,527),(985,589),(855,589),(855,527),(881,527)])
core=canon([(755,553),(855,553),(855,527),(985,527),(985,589),(855,589),(755,690)])
# Four-storey front; occupied5F restricted to upper diagonal. Lower connector roof stays at4F.
# Lower diagonal4F occupies shortened portion; its unlabelled far end remains a3F terrace.
lower4=canon([(755,670),(855,589),(919,657),(919,721),(770,870),(703,803)])
foot=CS([right])+CS([lower])+CS([low_annex])+CS([upper])+CS([connector])+CS([core])
# Terrain proxy follows all connected wings, with rear plinth reaching the missing1F level.
# Front ground z=.7; rear2F starts4.05 and is grounded on disclosed rising solid terrain.
add(foot.offset(.7).extrude(.75),5,'connected_outline_following_terrain_base')
# Sloped hill wedge, clipped to the rear and connector footprints: NOT an invented occupied B1.
rearfoot=(CS([upper])+CS([connector])).offset(.35)
add(rearfoot.extrude(3.45).translate((0,0,.7)),5,'rear_hillside_base_reaches2F_no_floating_wing')
# Modest sloping road-side grade alongside straight-wing far end, capped well below2F.
wedge=poly([(10,-7.5),(31,-7.5),(31,1),(10,1)],.7,2.6)
# Wedge generated as triangular xz prism; its low end merges into lower plinth.
ww=CS([[(10,0),(31,0),(31,2.6),(10,.7)]]).extrude(8.5).rotate((90,0,0)).translate((0,1,0))
add(ww,5,'right_end_rising_grade_proxy')
#1F foyer under upper front wing is genuinely recessed/open, not filled to gain one shell.
front1=(poly(right,.7,4.05)+poly(lower,.7,4.05)+poly(core,.7,4.05))-cube(-1,11.8,-7,-1.8,1.0,4.06)
add(front1,1,'1F_front_wings_with_open_recessed_entrance')
add(poly(low_annex,.7,7.45),1,'1F_2F_wider_low_projecting_room_group')
for p,n in [(right,'right_straight'),(lower,'front_lower_diagonal'),(core,'common_stair_root')]:add(poly(p,3.98,10.8),1,'2F_3F_'+n)
for p,n in [(right,'right_straight'),(lower4,'shortened_front_diagonal'),(core,'common_stair_root')]:
 m=poly(p,10.73,14.15)
 if n=='right_straight':m=m-cube(28.3,30.3,-1.55,.1,11.0,13.25)
 add(m,0,'4F_'+n+'_concrete_upper_frame')
add(poly(upper,4.02,14.15),1,'2F_to4F_rear_upper_diagonal')
add(poly(upper5,14.1,17.5),1,'5F_rear_upper_diagonal_only_excludes_blank_east_connector_roof')
add(poly(connector,4.02,14.15),1,'2F_to4F_straight_connector_no_occupied5F')
block(29.95,30.15,-.22,0,10.73,14.15,0,'photo828_right_end_upper_frame_corner_post')
# Roof decks/parapets explicitly stepped.
def roof(p,z,n):
 cs=CS([p]);add(cs.extrude(.22).translate((0,0,z)),0,n+'_deck')
 add((cs-cs.offset(-.22)).extrude(.6).translate((0,0,z+.12)),0,n+'_open_low_parapet')
roof(low_annex,7.4,'2F_low_room_roof');roof(lower,10.75,'3F_lower_diagonal_terrace');roof(lower4,14.1,'4F_short_diagonal_roof');roof(right,14.1,'4F_right_roof');roof(connector,14.1,'4F_connector_roof');roof(upper,14.1,'4F_rear_east_block_lower_roof');add(poly(upper5,17.45,17.67),0,'complete5F_cap_never_cut_away_for_different_R_drawing')
roof(r_outline,17.52,'R_registered_two_stair_stepped_perimeter')
# Shared stair cores are fixed by common plan corners; registered no raster setbacks.
block(0,6.5,-.12,3.05,.7,14.5,0,'common_stair_core_fixed_all_floors')
# Right attached rounded corridor stair, separately retained in full perimeter.
cs=CrossSection.circle(1.05,24).translate((21.9,3.0))+CS([[(20.85,-.1),(22.95,-.1),(22.95,3),(20.85,3)]])
add(cs.offset(.35).extrude(.85),5,'right_stair_ground_contact')
add(cs.extrude(14.5).translate((0,0,.7)),0,'right_corridor_external_round_stair')
# Upper diagonal far-end rounded stair at fixed source coordinates.
A=np.array(canon([(455,542)])[0]);B=np.array(canon([(503,590)])[0]);T=(B-A)/np.linalg.norm(B-A);N=np.array([-T[1],T[0]])
stairpts=[A-.1*T+.25*N,A+3.4*T+.25*N,A+3.4*T-2.6*N,A-.1*T-2.6*N]
cs=CS([stairpts])+CrossSection.circle(1.75,24).translate((A+1.65*T-2.6*N).tolist())
add(cs.offset(.35).extrude(4.05),5,'rear_stair_ground_contact')
add(cs.extrude(13.9).translate((0,0,3.85)),0,'rear_upper_diagonal_rounded_end_stair')
# Lower diagonal end stair3F;4F blank end is lower terrace rather than extra classroom.
add(poly(canon([(568,938),(635,1005),(668,972),(600,905)]),.7,10.9),0,'lower_diagonal_end_stair')
# Foyer rear doors and entrance porch, approximate detail from827.
block(-.3,11.7,-1.95,-1.75,1.1,3.7,2,'recessed_entry_door_glazing')
block(2.9,12.9,-8.05,-1.8,3.75,4.15,0,'projecting_entry_canopy_with_open_soffit')
for x in [5.4,10.5]:add(Manifold.cylinder(3.15,.24,.24,20).translate((x,-7.0,.7)),0,'round_entrance_porch_column')
# Brick/window courses on photo-evidenced right long face; not replicated on unseen facades.
for z in [4.5,7.85,11.2]:
 for x in [14.5,18,21.5,25,28]:
  block(x-1.25,x+1.25,-6.72,-6.56,z,z+1.45,3,'right_long_face_opaque_window_proxy')
  for xx in [x-1.25,x,x+1.25]:block(xx-.055,xx+.055,-6.85,-6.66,z-.04,z+1.5,4,'right_window_mullion')
  for zz in [z,z+.7,z+1.45]:block(x-1.3,x+1.3,-6.85,-6.66,zz-.055,zz+.055,4,'right_window_transom')
# Actual lattice air-space in front of recessed opaque glazing, not dark texture pretending holes.
block(4.4,12.7,-6.72,-6.54,4.4,10.9,2,'entry_screen_recessed_glazing')
for x0,x1 in [(4.35,5.65),(6.55,10.55),(11.45,12.8)]:
 for x in np.arange(x0+.075,x1,.62):block(x-.075,x+.075,-7.35,-6.65,4.35,10.95,0,'entrance_screen_three_segment_vertical')
 for z in np.arange(4.4,11.0,.65):block(x0,x1,-7.35,-6.65,z-.075,z+.075,0,'entrance_screen_three_segment_horizontal')
for x in [6.1,11.0]:add(Manifold.cylinder(6.95,.23,.23,20).translate((x,-7.0,4.1)),0,'two_upper_storeys_round_columns_between_lattice_panels')
block(4.3,12.85,-7.4,-6.5,10.95,11.2,0,'screen_upper_crossbeam')
# Glazed stair strip at left of entry on lower sloping wing, source-relative not mirror.
a=np.array([-.13,-9.93]);b=np.array([3.07,-6.73]);t=(b-a)/np.linalg.norm(b-a);n=np.array([t[1],-t[0]])
def strip(u0,u1,v0,v1,z0,z1,c,name):
 cen=a+(u0+u1)/2*t+(v0+v1)/2*n
 add(Manifold.cube((u1-u0,v1-v0,z1-z0),True).transform([[t[0],n[0],0,cen[0]],[t[1],n[1],0,cen[1]],[0,0,1,(z0+z1)/2]]),c,name)
strip(0,4.55,-.25,.08,.8,14.1,2,'entrance_left_glazed_stair_strip')
for z in np.arange(1,14,.8):strip(0,4.55,-.3,.16,z,z+.09,4,'stair_glazing_horizontal_frame')
for u in [0,2.2,4.45]:strip(u,u+.09,-.3,.17,.8,14.1,4,'stair_glazing_vertical_frame')
block(3.08,4.25,-6.98,-6.50,.7,14.12,0,'vertical_concrete_name_wall_strip_beside_glazed_stair')
# Upper front top window course above screen.
for x in [5.8,8.7,11.6]:
 block(x-1.15,x+1.15,-6.77,-6.57,11.35,12.85,3,'upper_entry_windows')
 block(x-1.25,x+1.25,-7.0,-6.55,12.9,13.08,0,'upper_entry_coarse_sunshade')
# Two roof access hoods only, small approximate enclosures; not entire sixth floor.
block(1.1,3.7,1.0,2.8,14.1,15.3,0,'low_common_stair_roof_access_approx')
block(-.8,1.1,13.4,16.3,17.45,18.65,0,'rear_R_stair_access_approx')
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學季陶樓','revision':'v4','scope':'complete connected main building;1F-4F front,2F-5F rear,stepped roofs and terrain proxy','nominal_scale_mm_per_approx_design_unit':SCALE,'coordinate_transform':'2011 landscape2F: X=(pixelX-855)/20,Y=(589-pixelY)/20; proper image-Y inversion, no mirror,no compass claim','outlines':{'right':right,'lower':lower,'low_annex':low_annex,'upper':upper,'upper5':upper5,'R':r_outline,'connector':connector,'core':core,'lower4':lower4},'floor_z_design':[.7,4.05,7.4,10.75,14.1,17.45],'registration':{'1F':{'anchor':[535,334],'scale':1.24},'2F':{'anchor':[855,589],'scale':1},'3F':{'anchor':[774,600],'scale':1.012},'4F':{'anchor':[919,622],'scale':1.02},'5F':{'anchor':[873,638],'scale':1.022}},'R_registration':{'R_to5F_translation_pixels':[-112.5,-5],'R_stair_centers':[[989,332],[611,642]],'5F_stair_centers':[[879,324],[496,640]],'method':'two stair common anchors; no .944 exterior-edge scaling; approx4px residual; keep full5F cap plus separately traced R low roof boundary'},'limits':['Unmeasured heights and terrain; no surveyed scale','Photo827 entrance registration and828 right end candidate require first-model review','Unseen fenestration intentionally neutral','2011 rear2F rooms414/413 equal plan4F, not two extra floors','Unknown B1 interiors omitted, no full exposed basement invented','OfficialPDF photographs capture date unknown; not verified2026 state','Source rights unresolved; private only, no broad model license','No physical print or support-free guarantee']}
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
# Preserve original surface/material partitions through simplification: no nearest-triangle material spill.
m=Manifold(m.to_mesh()).set_tolerance(.001).simplify(.001)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
colors=np.empty(len(fs),dtype=int);maxdist=0
for i,rid in enumerate(me.run_original_id):colors[me.run_index[i]//3:me.run_index[i+1]//3]=material_for_id[rid]

t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Export exact float32 triangles with analytically normalized normals; no small-face threshold.
tri=np.asarray(t.triangles,dtype=np.float32);cr=np.cross(tri[:,1].astype(float)-tri[:,0],tri[:,2].astype(float)-tri[:,0]);assert np.all(np.linalg.norm(cr,axis=1)>0),('float32 export degeneracy: repair generator, not QA',tri[np.linalg.norm(cr,axis=1)==0].tolist());nn=cr/np.linalg.norm(cr,axis=1)[:,None]
buf=bytearray(80)+struct.pack('<I',len(tri))
for nor,face in zip(nn,tri):buf+=struct.pack('<12fH',*nor,*face.ravel(),0)
(O/'model.stl').write_bytes(buf);raw=bytes(buf);n=len(tri)
rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n)
v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
assert np.array_equal(v[f],np.asarray(t.triangles,dtype=np.float32))
t=trimesh.Trimesh(v,f,process=False)
features=FEATURES
features.update(material_provenance='Original Boolean surface run IDs retained through float32 generation and simplification; no nearest-centroid recoloring',parts=part_records)
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
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split(only_watertight=False,repair=False)),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256(raw).hexdigest()}))
