"""NCCU Information / Computer Center Complex — source-relative approximate complete main-building exterior."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection,JoinType
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[] # Assigned below from NCCU source observations.
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



SCALE=3.0
palette=[('warm_cream_tile','#C9C6AE',255),('pale_stone_bands','#DDD8C5',255),('opaque_dark_glazing','#344B4B',255),('charcoal_edge_bands','#50534C',255),('roof_concrete','#9B9C8D',255),('limited_grade_proxy','#8E907D',255),('entry_stone','#B5B29E',255)]
def poly(points,z0,z1):return CrossSection([points],fillrule=__import__('manifold3d').FillRule.EvenOdd).extrude(z1-z0).translate((0,0,z0))
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def block(x0,x1,y0,y1,z0,z1,c,n):add(cube(x0,x1,y0,y1,z0,z1),c,n)
def trace(points):return [((x-120)/10,(375-y)/10) for x,y in points]
def pxbox(x0,x1,y0,y1,z0,z1,c,n):block((x0-120)/10,(x1-120)/10,(375-y1)/10,(375-y0)/10,z0,z1,c,n)
low_px=[(175,25),(715,25),(715,190),(610,190),(610,130),(535,130),(535,151),(365,151),(365,130),(295,130),(275,151),(175,151)]
high_px=[(175,110),(275,110),(275,245),(328,245),(328,365),(120,365),(120,154),(175,154)]
six_px=[(175,110),(275,110),(275,245),(328,245),(328,365),(120,365),(120,295),(175,295)]
low=trace(low_px);high=trace(high_px);six=trace(six_px)
# Ground contact follows building outline, not landscape or neighbouring plaza.
foot=CrossSection([low],fillrule=__import__('manifold3d').FillRule.EvenOdd)+CrossSection([high],fillrule=__import__('manifold3d').FillRule.EvenOdd)
add(foot.offset(.35).extrude(.8),5,'tight_building_contact_base_approx')
# B1 exterior proxy retains the actual complete footprint, omitted basement interior.
add(foot.extrude(2.5).translate((0,0,.75)),0,'B1_exterior_only_no_hidden_internal_rooms')
# Low four-storey back room band and attached end room; recessed front circulation is genuinely open.
add(cube(5.5,59.5,27.0,35.0,3.15,17.2)-cube(5.49,10.3,27.0,33.0,3.14,6.4),0,'low_1F_to_4F_room_band_with614_west_entry_recess')
for yy in [44,102]:pxbox(173,178,yy,yy+4,.7,6.6,0,'614_west_entry_support_column')
pxbox(610,715,103,190,3.15,17.2,0,'low_four_storey_far_end_room_block')
pxbox(175,275,103,152,3.15,17.2,0,'low_end_stair_and_shared_high_wing_junction')
for z in [3.2,6.7,10.2,13.7,17.2]:
 add(poly(low,z-.25,z+.18),1,'low_floor_slabs_follow_registered_outline')
for i in range(1,4):
 z=3.2+3.5*i
 # Actual upper central protruding room strip, not a 1F X cut through all floors.
 pxbox(365,535,103,151,z-.1,z+3.45,0,'upper_central_room_strip_1F_X_not_perforated_all_storeys')
# Regular open corridor columns/rails approximate photo610; no literal X diagonal bracing.
for x in [280,305,355,410,465,535,605]:pxbox(x-2,x+2,126,132,3.0,20.6,0,'low_front_columns_and_roof_frame_posts')
for z in [6.9,10.4,13.9,17.4]:
 for x0,x1 in [(277,365),(535,610)]:
  pxbox(x0,x1,128,131,z,z+.50,1,'low_recessed_corridor_solid_low_rail')
  pxbox(x0,x1,129,130,z+.9,z+1.03,1,'low_corridor_upper_rail')
pxbox(175,715,24,26,17.15,17.9,0,'611_low_outer_roof_boundary_coarse_rail_proxy')
# 5F crossed long strip is open top framework over the low building, with bounded end room.
pxbox(275,610,129,154,17.1,17.4,4,'low_roof_walk_strip_deck')
for y in [129,153]:pxbox(275,610,y,y+3,20.15,20.65,0,'open_roof_level_longitudinal_beam')
for x in [277,365,460,535,608]:
 pxbox(x,x+3,129,156,20.15,20.65,0,'open_roof_level_cross_beam')
 pxbox(x,x+3,152,155,17.25,20.4,0,'open_roof_front_post')
pxbox(610,715,108,190,17.1,20.9,0,'5F_bounded_enclosed_far_end_room_not_whole_long_strip')
pxbox(610,715,187,191,20.85,21.05,3,'named_end_roof_dark_cap')
# Semicircular information stair; true projecting half-round with tiered open railing slots.
roundpx=[(542,132),(578,132)]+[(560+18*math.cos(a),142+18*math.sin(a)) for a in np.linspace(0,math.pi,17)]
roundplan=trace(roundpx)
for z in [3.2,6.7,10.2,13.7,17.2]:add(poly(roundplan,z-.2,z+.2),1,'information_semicircular_stair_floor')
cs=CrossSection([roundplan],fillrule=__import__('manifold3d').FillRule.EvenOdd)
for z in [3.3,6.8,10.3,13.8]:add((cs-cs.offset(-.24)).extrude(.85).translate((0,0,z)),0,'information_round_stair_open_parapet')
pxbox(553,567,134,143,3.0,18.7,0,'information_round_stair_inner_structural_core')
add(poly(roundplan,18.55,18.85),1,'information_round_stair_small_canopy')
# High computer wing: 1F entrance undercroft is retained, rather than filling beneath columns.
add(poly(high,6.65,17.22),0,'computer_2F_to_4F_complete_perpendicular_wing')
add(poly(six,17.15,20.72),0,'computer5F_occupied_excludes_labelled_west_terrace')
pxbox(175,275,110,245,3.1,6.8,0,'computer1F_shared_junction_and_internal_core')
pxbox(120,176,162,245,3.1,6.8,0,'621_registered1F_west_room_not_false_undercroft')
pxbox(120,328,295,334,3.1,6.8,0,'computer1F_rear_room_band')
for x in [125,175,225,275,323]:pxbox(x-3,x+3,359,365,3.0,6.85,0,'computer1F_true_south_entry_support_columns_approx')

add(poly(six,20.65,24.2),0,'computer6F_registered627_left_narrower_wing')
add(poly(high,17.17,17.4),4,'computer_5F_labelled_west_terrace_over4F_not_extra_storey')
add(poly(six,24.15,24.45),4,'high_RF_only_not_low_wing')
for pts,z in [(high,17.35),(six,24.42)]:
 cs=CrossSection([pts],fillrule=__import__('manifold3d').FillRule.EvenOdd)
 add((cs-cs.offset(-.22)).extrude(.55).translate((0,0,z)),0,'high_roof_parapet_approx')
# Distinct three anchored cores: flat tall junction core, curved computer stair, low semicircular stair.
pxbox(175,230,110,154,.7,27.0,0,'flat_topped_junction_stair_core_photo611_round_opening')
pxbox(173,232,108,156,26.95,27.18,1,'flat_topped_core_cap')
curvedpx=[(304,245),(328,245)]+[(328+14*math.cos(a),270+25*math.sin(a)) for a in np.linspace(-math.pi/2,math.pi/2,21)]+[(304,295)]
curved=trace(curvedpx)
add(poly(curved,.7,26.1),0,'curved_computer_stair_high_edge_core_610_same_as611')
add(poly(curved,26.05,26.3),1,'curved_stair_cap_approx')
# Roof lift/core inset kept modest, not another entire floor.
pxbox(210,237,112,143,24.3,25.8,0,'high_RF_small_inset_service_core_approx')
#610 photographed central raised short roof-front cap: not an added full storey.
pxbox(175,275,351,365,24.3,26.0,0,'610_south_central_raised_short_parapet')
pxbox(173,277,349,367,25.95,26.4,1,'610_raised_central_thick_cornice')
pxbox(173,277,349,367,26.35,26.5,3,'610_central_cap_dark_top_edge')
# All window panes are opaque relief with source-informed distribution, not photographic textures.
def facade(a,b,z0,z1,count,name):
 a=np.array(a,dtype=float);b=np.array(b,dtype=float);t=(b-a)/np.linalg.norm(b-a);L=np.linalg.norm(b-a);n=np.array([t[1],-t[0]])
 def patch(u0,u1,v0,v1,h0,h1,col,label):
  c=a+(u0+u1)/2*t+(v0+v1)/2*n;add(Manifold.cube((u1-u0,v1-v0,h1-h0),True).transform([[t[0],n[0],0,c[0]],[t[1],n[1],0,c[1]],[0,0,1,(h0+h1)/2]]),col,label)
 for i in range(count):
  u0=(i+.13)*L/count;u1=(i+.87)*L/count;patch(u0,u1,-.08,.08,z0,z1,2,name)
  for u in [u0,(u0+u1)/2,u1]:patch(u-.04,u+.04,.02,.14,z0-.05,z1+.05,3,'approx_window_mullion')
  for z in [z0,z1]:patch(u0-.04,u1+.04,.02,.14,z-.05,z+.05,3,'approx_window_border')
def pf(a,b,z0,z1,n,name):facade(*trace([a,b]),z0,z1,n,name)
for i in range(4):
 z=3.2+3.5*i
 pf((610,190),(715,190),z+.7,z+2.8,2,'610_low_end_front_paired_windows')
 pf((715,25),(175,25),z+.8,z+2.8,10,'611_low_long_outer_side_windows_approx')
 if i>0:pf((175,25),(175,110),z+.8,z+2.8,1,'611_low_near_end_broad_window')
 else:pf((223,50),(223,105),z+.4,z+2.8,1,'614_recessed_entry_door_behind_columns')
 if i>0:pf((365,151),(535,151),z+.7,z+2.8,3,'610_middle_upper_room_windows')
 pf((275,105),(610,105),z+.8,z+2.8,7,'recessed_low_corridor_back_windows')
for i in range(1,6):
 z=3.2+3.5*i
 if i>=4:pf((135,365),(314,365),z+.65,z+2.7,3,'610_high_south_upper_two_storey_window_band')
 elif i==3:pf((193,365),(250,365),z+.8,z+2.6,2,'610_blank_southwall_only_central_pair')
 if i==3:pf((120,154),(120,295),z+1.7,z+2.5,5,'611_low_west_blankwall_only_upper_small_square_windows')
 if i>=4:
  pf((175,154),(175,290),z+.75,z+2.7,4,'611_high_top_window_band')
  pf((275,245),(275,155),z+.75,z+2.7,3,'610_high_upper_side_windows')
pf((185,365),(265,365),24.75,25.05,1,'610_south_central_narrow_vent_under_cap')
for xx in [135,195,254,314]:pxbox(xx-1,xx+1,364,367,21.2,24.0,1,'610_upper_window_band_projecting_piers')
pxbox(134,315,364,367,23.8,24.08,1,'610_upper_window_band_thick_header')
#611 bounded arched opening on existing southwest6F end wall.
#Its relationship to the distinct610 curved stair is not uniquely established; no added tower.
def arch_patch(radius,stem,x0,depth,yy,zz,col,name):
 outline=[(-radius,0),(radius,0),(radius,stem)]+[(radius*math.cos(a),stem+radius*math.sin(a)) for a in np.linspace(0,math.pi,25)]+[(-radius,0)]
 m=CrossSection([outline],fillrule=__import__('manifold3d').FillRule.EvenOdd).extrude(depth)
 add(m.transform([[0,0,1,x0],[1,0,0,yy],[0,1,0,zz]]),col,name)
arch_patch(.95,.65,-.10,.18,(375-320)/10,22.0,3,'611_existing_southwest_high_end_arched_opening_border')
arch_patch(.72,.55,-.13,.08,(375-320)/10,22.17,2,'611_arched_opening_opaque_relief_not_new_core')
# Flat junction core horizontal slits facing photo611, circular dark inset impression near its top.
for z in [7.3,10.8,14.3,17.8,21.3]:pf((175,110),(175,152),z,z+.30,1,'flat_junction_core_horizontal_slit')
# Circle built as attached disc relief, not an unsupported floating clock or invented actual dial.
cx,cy=trace([(203,110)])[0]
add(Manifold.cylinder(.16,.60,.60,40).rotate((90,0,0)).translate((cx,cy+.08,25.0)),3,'611_round_dark_opening_relief_no_clock_claim')
add(Manifold.cylinder(.17,.40,.40,40).rotate((90,0,0)).translate((cx,cy+.10,25.0)),1,'611_round_opening_inner_pale_disc')
# Vertical slit and top arched indication on curved stair, not duplicated on flat core.
for j in range(10,13):pf(curvedpx[j],curvedpx[j+1],5.1,21.4,1,'610_curved_core_long_vertical_slit_conforming_facets')
for j in range(5,11):pf(curvedpx[j],curvedpx[j+1],23.4,24.8,1,'610_curved_core_upper_dark_opening_conforming_facets')
# Dark horizontal roof/string courses characteristic of cream complex.
for z in [13.65,20.55]:
 pf((120,365),(328,365),z,z+.18,1,'computer_dark_stringcourse')
# Main entry steps approach the actual undercroft; support contacts start on low base.
for i in range(12):pxbox(160,260,387-i*1.8,389-i*1.8,.65,.85+(i+1)*.19,6,'621_registered_south_main_entry_steps')
pxbox(155,265,333,367,2.9,3.25,6,'registered_south_entry_landing_under_high_wing')
for x0,x1 in [(155,160),(260,265)]:pxbox(x0,x1,333,390,.7,3.65,0,'south_entry_stair_solid_side_wall')
pxbox(152,268,331,392,0,.76,5,'limited_south_entry_ground_contact')
# 614 low-wing west entrance is distinct from621 computer south entrance.
for i in range(12):pxbox(135+i*3.3,139+i*3.3,53,87,.65,.85+(i+1)*.19,6,'614_registered_west_information_entry_steps')
pxbox(171,224,50,104,2.9,3.25,6,'614_west_entry_landing_under_low_wing')
for yy in [49,103]:pxbox(133,224,yy,yy+3,.7,3.6,0,'614_west_entry_sidewall')
pxbox(131,225,47,108,0,.76,5,'614_entry_ground_contact_only')
#621 attached two-flight outside approach; unmeasured grades represented locally only.
#Small east-going flight descends from computer1F, broad flight turns north to low1F platform.
pxbox(328,341,250,291,2.95,3.25,6,'621_curved_core_attached_entry_landing')
for i in range(10):pxbox(338.6+i*3,342.6+i*3,248,290,.65,3.15-i*.235,6,'621_short_east_descending_flight')
for i in range(14):pxbox(367,521,287-i*3,291-i*3,.65,.82+(i+1)*.17,6,'621_broad_north_ascending_external_flight')
pxbox(366,535,240,249,2.95,3.25,6,'621_broad_flight_top_landing')
#Only attached stair flight and its immediate landing are modeled.
#The long narrow landscape route/round far end beyond it is not asserted to be building fabric.
pxbox(335,537,239,293,0,.76,5,'621_stairs_only_contact_ground_not_foreground_plaza')
pxbox(533,536,239,250,3.2,3.8,0,'621_immediate_landing_outer_low_rim')
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學資訊大樓（含電算中心）','scope':'complete connected L-shaped information/computer building; attached entries and bounded grade only','coordinate_transform':'626 master X=(px-120)/10,Y=(375-py)/10; proper y-up; scale3mm/design unit','low_outline_reading_pixels':low_px,'high_outline_reading_pixels':high_px,'six_outline_reading_pixels':six_px,'three_anchors_reading_pixels':{'shared_information_end_stair_anchor':[245,130],'curved_computer_core':[328,270],'semicircular_information_core':[560,145]},'high_5F_occupied_outline_reading_pixels':six_px,'5F_west_terrace_deck_top_mm':52.2,'611_arch_face_proxy':'existing southwest6F end wall; not uniquely same610 curved stair face; no added mass','entry_interfaces':['614 west information recessed1F stair','621 inset south computer door/stair','621 curved core east connecting flight and complete broad flight; outside path beyond landing omitted'],'low_4F_roof_mm':51.6,'open_frame_top_mm':61.95,'high_RF_mm':73.35,'flat_core_top_mm':81.54,'nominal_scale_mm_per_approx_design_unit':SCALE,'limits':['Official fire equipment simple plans are not measured architectural/as-built plans','Photo date unknown; not verified2026 condition','Dimensions, fine windows, small core heights and terrain approximate','Basement exterior proxy; no invented hidden interior','Original source pixels excluded from deliverables; no broad source license claimed','No physical print or support-free guarantee']}
# Coalesce same-material construction primitives before final material Boolean. This removes
# artificial coplanar construction seams without nearest recolouring across material boundaries.
grouped=[];group_material_ids={}
for col in range(len(palette)):
 same=[part for part,record in zip(parts,part_records) if record['material']==col]
 g=Manifold.batch_boolean(same,OpType.Add).as_original().set_tolerance(.001).simplify(.001)
 group_material_ids[g.original_id()]=col;grouped.append(g)
parts=grouped;material_for_id=group_material_ids
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
# Preserve Boolean run provenance through simplification: never nearest-surface paint broad triangles.
m=m.set_tolerance(.001).simplify(.001)
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
features.update(material_assignment_method="Boolean original-run provenance retained through simplification; no nearest recolouring",parts=part_records)
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
