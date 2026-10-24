"""NCCU Xuesi Hall — source-relative approximate complete main-building exterior."""
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



SCALE=4.0
palette=[('warm_brown_brick','#8B7058',255),('cream_columns_and_rails','#E1DDCD',255),('opaque_blue_green_glazing','#34545B',255),('dark_bridge_interface_edge','#555B50',255),('roof_concrete','#AAA99A',255),('bounded_grade_proxy','#93917F',255),('entry_stone','#B7AE95',255)]
def poly(points,z0,z1):return CrossSection([points],fillrule=__import__('manifold3d').FillRule.EvenOdd).extrude(z1-z0).translate((0,0,z0))
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def trace(points):return [((x-50)/16,(365-y)/16) for x,y in points]
def pxbox(x0,x1,y0,y1,z0,z1,c,n):
 a,b=trace([(x0,y1),(x1,y0)]);add(cube(a[0],b[0],a[1],b[1],z0,z1),c,n)
outline_px=[(50,45),(497,45),(497,28),(585,28),(585,45),(850,45),(850,365),(675,365),(675,225),(230,225),(230,365),(50,365)]
outline=trace(outline_px)
# Contact is restricted to actual building footprint; front court remains empty.
add(CrossSection([outline],fillrule=__import__("manifold3d").FillRule.EvenOdd).offset(.18).extrude(.65),5,'bounded_building_contact_base')
add(poly(outline,.6,2.1),1,'B1_visible_plinth_proxy_no_hidden_rooms')
# Complete four-floor room mass with real open gallery in front.
pxbox(50,850,45,180,2.05,16.5,0,'complete_nine_bay_four_storey_rear_room_band')
for a,b in [(50,230),(675,850)]:pxbox(a,b,218,365,2.05,16.5,0,'four_storey_projecting_end_classroom_wing')
# Main stair core and west stair/elevator enclosure; no unobserved extra fifth floor.
pxbox(497,585,28,225,2.05,16.5,1,'registered_main_stair_core')
pxbox(15,142,180,225,.6,16.5,1,'west_stair_lift_core_with_own_ground_contact')
pxbox(12,52,177,228,0,.66,5,'west_core_own_base_not_gallery_infill')
for z in [2.1,5.7,9.3,12.9,16.5]:add(poly(outline,z-.18,z+.12),1,'four_floor_slabs_and_complete_flat_roof')
# The front gallery air gap is retained between y180 backwall and y225 front columns.
for x in [230,319,408,497,585,675]:
 pxbox(x-2.7,x+2.7,218,225,2.05,16.5,1,'front_gallery_white_columns')
for z in [5.8,9.4,13.0]:
 for x0,x1 in [(230,497),(585,675)]:
  pxbox(x0,x1,219,225,z,z+.72,1,'gallery_opaque_lower_parapet')
  pxbox(x0,x1,221,223,z+1.02,z+1.10,1,'gallery_upper_handrail')
  for x in range(x0+9,x1,18):pxbox(x,x+1.6,221,223,z+.69,z+1.06,1,'gallery_railing_verticals')
# Flat top follows all occupied4F rooms, not523 cropped six-bay rectangle.
cs=CrossSection([outline],fillrule=__import__("manifold3d").FillRule.EvenOdd);add((cs-cs.offset(-.18)).extrude(.45).translate((0,0,16.57)),0,'complete_flat_roof_low_edge_approximation')
# Inset main roof access core follows523 shared stair coordinates, modest approximate height.
pxbox(502,579,40,142,16.5,18.1,1,'R_registered_stair_access_only')
pxbox(500,581,38,144,18.05,18.23,4,'R_access_flat_cap')
# Window relief: observed front wings + actual gallery back wall, unknown back kept neutral.
def front_window(x0,x1,y,z0,z1,name):
 pxbox(x0,x1,y-1,y+1,z0,z1,2,name)
 for x in [x0,(x0+x1)/2,x1]:pxbox(x-.7,x+.7,y,y+2,z0-.04,z1+.04,1,'pale_window_mullion')
 for z in [z0,z0+.6,z1]:pxbox(x0-.7,x1+.7,y,y+2,z-.04,z+.04,1,'pale_window_transom')
for i in range(4):
 z=2.1+3.6*i
 for a,b in [(50,230),(675,850)]:
  for j in range(3):front_window(a+12+j*(b-a-20)/3,a+12+(j+.85)*(b-a-20)/3,365,z+.65,z+2.75,'516_end_wing_front_window')
 for a,b in [(235,493),(590,670)]:
  for j in range(3 if a<500 else 1):
   w=(b-a)/(3 if a<500 else 1);front_window(a+j*w+5,a+(j+1)*w-5,180,z+.8,z+2.7,'515_true_gallery_back_wall_window')
# Long white projecting vertical fins on the photographed end-wing fronts.
for a,b in [(50,230),(675,850)]:
 for j in range(4):
  x=a+8+j*(b-a-16)/3;pxbox(x-1.4,x+1.4,364,372,2.65,16.0,1,'516_end_front_long_white_piers')
#515 local vertical sun screen on central stair face, not mirrored onto unseen rear.
for x in range(502,582,7):pxbox(x,x+2.6,224,230,9.5,13.1,1,'515_local_vertical_sun_screen')
pxbox(497,585,223,226,13.15,16.5,0,'515_bounded_upper_core_front_brown_band')
for x in [502,527,552]:front_window(x,x+21,226,13.75,15.9,'515_local_top_core_window_not_unseen_rear')
# 518 broad central front entrance staircase, independently rooted to local grade.
pxbox(405,498,222,265,0,.66,5,'518_central_broad_stair_ground_contact')
for i in range(10):pxbox(408,495,261-i*3.6,265-i*3.6,.6,.75+(i+1)*.135,6,'518_central_broad_entry_steps')
# Separate right-turn flight beside main stairs, not a substitute bridge deck.
pxbox(497,557,221,285,0,.66,5,'518_turning_stair_contact_only')
# Narrow upper flight occupies the traced25px stair width, with an explicit upper arrival.
pxbox(498,585,223,234,.6,2.12,6,'518_turning_entry_top_arrival_landing')
for i in range(8):pxbox(500,527,252-i*3.4,256-i*3.4,.6,1.20+(i+1)*.115,6,'518_turning_entry_upper_flight')
# Quarter-turn fanned treads at foot, anchored to the same flight, not arbitrary rectangular filler.
# Center527,255: forward run north, outer arc turns east towards lower approach.
for i in range(5):
 a0=math.pi/2+i*math.pi/10;a1=math.pi/2+(i+1)*math.pi/10
 pts=[(527,255)]+[(527+28*math.cos(a),255+28*math.sin(a)) for a in np.linspace(a0,a1,5)]
 add(poly(trace(pts),.6,.80+(i+1)*.08),6,'518_quarter_turn_fanned_tread')
pxbox(527,555,255,283,.6,.80,6,'518_lower_turn_arrival_tread')
# Separate east entrance stair shown on518 at the room-band edge.
pxbox(780,850,173,222,0,.66,5,'518_east_entry_stair_ground')
# Cut lower east corridor fill is already open, stair joins rear mass at y180.
for i in range(10):pxbox(783,828,217-i*3.7,222-i*3.7,.6,.75+(i+1)*.135,6,'518_east_entry_steps')
# North/back short exterior approach on518, at its actual local edge.
pxbox(360,404,16,46,0,.66,5,'518_north_entry_contact')
for i in range(8):pxbox(364,400,16+i*3.5,20+i*3.5,.6,.75+(i+1)*.17,6,'518_north_entry_steps')
#519 attached2F landing stops at building interface. Independent bridge span entirely excluded.
pxbox(498,585,221,238,5.48,5.86,1,'519_attached_bridge_interface_landing_not_span')
for x in [502,580]:
 a=trace([(x,233)])[0];add(Manifold.cylinder(5.1,.30,.30,24).translate((*a,.6)),1,'519_landing_support_column')
for x0,x1 in [(498,502),(581,585)]:pxbox(x0,x1,224,238,5.8,6.58,3,'519_landing_side_edge_no_false_end_wall')
# Main entry dark backing is below landing and attached to registered stair wall.
pxbox(508,574,224,226,2.28,4.95,3,'514_dark_stone_entry_backing_not_door')
pxbox(517,566,226,226.8,2.95,4.30,4,'514_neutral_unlettered_sign_panel_not_window')
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學學思樓','revision':'v2','scope':'complete four-storey nine-bay main building and both projecting wings; attached entries and platform only','coordinate_transform':'522 master X=(px-50)/16 Y=(365-py)/16, scale4mm per approximate design unit','outline_reading_pixels':outline_px,'anchors':{'central_stair':[497,585],'bay_spacing_px':89,'west_core':[15,142,180,225]},'R_limit':'523 has six bays vs4F nine, same89px bay; register core translation(-38,-73)px, do not shrink or delete real4F wings','R_registration':{'source_core':[535,623,118,217],'master_core':[497,585,45,144],'translation_px':[-38,-73],'limit':'shared stair-side registration; roof-access elevation approximate'},'bridge_limit':'only519 attached landing y221..238, independent span to Yixian excluded; no invented transverse closure wall','entry_interfaces':['518 central broad steps','518 adjacent turning flight','518 east stairs','518 north short steps','519 second-floor attached platform separate'], 'limits':['Fire equipment plans not as-built measured drawings','Photo year unknown; not verified2026 condition','Unknown back windows omitted, not mirrored','Height, terrain, small roof access elevation approximate','No hidden B1 rooms','No physical print or support-free guarantee']}
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
