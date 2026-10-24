"""NCCU Daofan Hall — source-relative approximate complete main-building exterior."""
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
palette=[('red_brown_brick','#874F3E',255),('warm_pale_concrete','#D4CDB9',255),('opaque_blue_gray_glazing','#49616B',255),('gray_weathered_concrete','#929383',255),('roof_concrete','#AAA99A',255),('bounded_grade_proxy','#8A8A76',255),('entry_stone','#B7AE95',255)]
def poly(points,z0,z1):return CrossSection([points],fillrule=__import__('manifold3d').FillRule.EvenOdd).extrude(z1-z0).translate((0,0,z0))
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def trace(points):return [((x-115)/16,(386-y)/16) for x,y in points]
def pxbox(x0,x1,y0,y1,z0,z1,c,n):
 a,b=trace([(x0,y1),(x1,y0)]);add(cube(a[0],b[0],a[1],b[1],z0,z1),c,n)
def ppoly(points,z0,z1,c,n):add(poly(trace(points),z0,z1),c,n)
def capring(points,z,h,w,c,n):
 cs=CrossSection([trace(points)],fillrule=__import__('manifold3d').FillRule.EvenOdd);add((cs-cs.offset(-w)).extrude(h).translate((0,0,z-.02)),c,n)
# Master809 registered common stairs. Local dimensions are source-relative approximations.
north=[(170,88),(544,88),(544,164),(170,164)]
east=[(544,22),(650,22),(650,326),(544,326)]
south=[(115,294),(184,294),(184,308),(524,308),(544,294),(568,294),(568,386),(115,386)]
full=[(170,88),(544,88),(544,22),(650,22),(650,326),(568,326),(568,386),(115,386),(115,294),(184,294),(184,308),(524,308),(544,294),(544,180),(524,164),(170,164)]
# B1 only the south wing and southern east leg; no artificial full-C basement.
ppoly(south,0,.65,5,'south_local_grade_contact')
pxbox(568,650,196,326,0,.65,5,'east_lower_local_grade_contact')
pxbox(130,568,329,386,.60,3.40,0,'B1_south_room_band_only')
pxbox(568,650,196,326,.60,3.40,0,'B1_partial_east_leg_only')
# Uphill main north foundations stop at a higher local grade rather than adding B1 rooms.
ppoly(north,2.75,3.42,5,'north_bounded_uphill_contact_not_basement')
pxbox(544,650,22,196,2.75,3.42,5,'east_upper_bounded_grade')
def grade_wedge(x0,x1,y0,y1,zlow,zhigh,name):
 q=trace([(x0,y0),(x1,y0),(x1,y1),(x0,y1)])
 verts=[(x,y,0) for x,y in q]+[(x,y,zlow if i<2 else zhigh) for i,(x,y) in enumerate(q)]
 add(Manifold.hull_points(verts),5,name)
grade_wedge(170,544,88,164,3.25,2.80,'bounded_north_slope_grade_to_common_datum')
grade_wedge(544,650,22,196,3.25,2.80,'bounded_upper_east_slope_grade')
grade_wedge(702,930,-14,90,3.25,2.80,'bounded_annex_slope_grade')
# Thin local pedestals support connector posts, not a full bridge infill.
for x in [650,677,702]:
 for y in [70,106]:pxbox(x-3,x+3,y-3,y+3,0,2.80,5,'neck_post_local_ground_pedestal')

# Room masses. Open corridors remain outside these solids.
pxbox(170,544,88,143,3.35,17.0,0,'north_four_storey_room_wing')
a,b=trace([(568,326),(650,22)]);room=cube(a[0],b[0],a[1],b[1],3.35,17.0)
a,b=trace([(620,254),(652,194)]);recess=cube(a[0],b[0],a[1],b[1],3.30,6.64)
add(room-recess,0,'east_four_storey_room_leg_with_true_recessed_entry')
pxbox(620,621,205,243,3.56,6.02,2,'798_recessed_entry_door_back_plane')
for y in [205,224,243]:pxbox(620,623,y-.8,y+.8,3.55,6.04,1,'798_entry_door_jamb')
pxbox(620,623,205,243,6.02,6.10,1,'798_entry_door_head')
pxbox(130,568,329,386,3.35,13.6,0,'south_three_storey_room_wing_low_roof')
pxbox(115,170,294,386,3.35,13.6,0,'south_end_services')
for z in [3.4,6.8,10.2,13.6]:
 ppoly(full,z-.16,z+.14,1,'main_floor_slab_'+str(z))
for p in [north,east]:ppoly(p,16.84,17.14,1,'4F_complete_occupied_flat_roof')
for p,z in [(north,17.14),(east,17.14),(south,13.74)]:capring(p,z,.40,.20,0,'roof_edge_low_parapet')
# Main common three stair cores, two with semicircular projecting ends.
pxbox(297,332,100,164,3.35,17.0,1,'north_internal_common_stair')
def rounded_stair(x0,x1,y0,y1,orient,z0,z1,name):
 pxbox(x0,x1,y0,y1,z0,z1,1,name+'_rect')
 if orient=='north':
  center=((x0+x1)/2,y0);r=(x1-x0)/2;pts=[(center[0]+r*__import__('math').cos(a),center[1]+r*__import__('math').sin(a)) for a in __import__('numpy').linspace(__import__('math').pi,2*__import__('math').pi,25)]
 elif orient=='west':
  center=(x0,(y0+y1)/2);r=(y1-y0)/2;pts=[(center[0]+r*__import__('math').cos(a),center[1]+r*__import__('math').sin(a)) for a in __import__('numpy').linspace(__import__('math').pi/2,3*__import__('math').pi/2,25)]
 elif orient=='south':
  center=((x0+x1)/2,y1);r=(x1-x0)/2;pts=[(center[0]+r*__import__('math').cos(a),center[1]+r*__import__('math').sin(a)) for a in __import__('numpy').linspace(0,__import__('math').pi,25)]
 else:
  center=(x1,(y0+y1)/2);r=(y1-y0)/2;pts=[(center[0]+r*__import__('math').cos(a),center[1]+r*__import__('math').sin(a)) for a in __import__('numpy').linspace(-__import__('math').pi/2,__import__('math').pi/2,25)]
 ppoly(pts,z0,z1,1,name+'_round_end')
rounded_stair(184,225,276,329,'north',.6,13.74,'south_common_round_stair')
rounded_stair(488,568,202,233,'west',.6,17.14,'east_common_round_stair')
# Actual gallery air and supporting posts; neutral rear faces are not mirrored windows.
for x in [170,213,256,297,332,384,436,488,540]:pxbox(x-2,x+2,159,164,3.4,17,1,'north_courtyard_gallery_columns')
for y in [110,162,202,253,302,326]:pxbox(544,549,y-2,y+2,3.4,17,1,'east_courtyard_gallery_columns')
for x in [184,225,277,329,381,433,485,540]:pxbox(x-2,x+2,308,313,3.4,13.6,1,'south_courtyard_gallery_columns')
for z in [6.94,10.34,13.74]:
 pxbox(170,544,161,164,z-.03,z+.75,1,'north_gallery_parapet')
 pxbox(544,547,110,202,z-.03,z+.75,1,'east_gallery_parapet_upper')
 pxbox(544,547,233,308,z-.03,z+.75,1,'east_gallery_parapet_lower')
 if z<13: pxbox(225,548,307.5,311,z-.03,z+.75,1,'south_gallery_parapet')
# Attached two-storey hall. Broken corridors registered by width/direction; chosen neck length approximate.
# 803 hall near stair x363 / far stair574; pair offset(+360,-140) brings corridor to mastery68..108.
hall=[(702,-14),(930,-14),(930,90),(702,90)]
ppoly(hall,2.75,3.42,5,'annex_uphill_local_contact')
# Approximate hollow hall interior, not a claim of surveyed rooms or whole-floor lightwell.
cs=CrossSection([trace(hall)],fillrule=__import__('manifold3d').FillRule.EvenOdd)
wall=(cs-cs.offset(-.42)).extrude(6.8).translate((0,0,3.4));add(wall,0,'annex_two_storey_enclosing_walls')
for z in [3.4,6.8,10.2]:ppoly(hall,z-.14,z+.14,1,'annex_floor_or_roof_'+str(z))
a,b=trace([(702,90),(750,-14)]);service=cube(a[0],b[0],a[1],b[1],3.4,10.2)
a,b=trace([(700,91),(751,50)]);pocket=cube(a[0],b[0],a[1],b[1],3.54,6.64)
add(service-pocket,0,'annex_near_service_band_with_local_mezzanine_pocket')
pxbox(686,704,3,74,2.75,6.8,0,'803_1F_near_side_projecting_service_rooms')
pxbox(684,706,1,76,6.74,6.94,1,'803_side_room_low_roof')
pxbox(787,870,88,110,2.75,6.8,0,'803_1F_lower_projecting_room_band')
pxbox(785,872,88,112,6.74,6.94,1,'803_lower_room_band_low_roof')
grade_wedge(686,704,3,74,3.25,2.8,'annex_side_rooms_local_grade')
grade_wedge(787,870,90,110,2.8,2.8,'annex_lower_rooms_local_grade')
pxbox(702,750,50,90,5.0,5.18,1,'annex_local_first_floor_mezzanine_only')
capring(hall,10.34,.40,.20,0,'annex_roof_edge')
rounded_stair(704,744,90,124,'south',3.4,10.34,'annex_near_south_projecting_stair')
rounded_stair(914,938,-26,-2,'east',3.4,10.34,'annex_far_east_projecting_stair')
# Narrow continuous connection joins main upper east side to annex west at common floor levels.
for z in [3.4,6.8,10.2]:pxbox(646,706,68,108,z-.16,z+.14,1,'neck_continuous_slab_'+str(z))
for x in [650,677,702]:
 for y in [70,106]:pxbox(x-2,x+2,y-2,y+2,2.75,10.2,1,'neck_support_column')
for z in [6.94,10.34]:
 for y in [68,105]:pxbox(650,704,y,y+3,z-.03,z+.75,1,'neck_open_side_parapet')
# Photographed external east facade: pale round columns, brick bands and2/3F lattice.
for y in [112,155,198,241,284,324]:
 xw,yw=trace([(660,y)])[0];add(Manifold.cylinder(10.2,.35,.35,32).translate((xw,yw,3.4)),1,'798_east_facade_round_column')
for y in [112,155,198,241,284,324]:pxbox(648,660,y-2,y+2,3.4,13.6,1,'column_back_attachment')
pxbox(648,656,108,326,13.42,17.0,0,'798_top_brick_front_band')
# Avoid fictitious glazing behind the exposed grid: recess screen 0.3 units outward from wall.
for y in range(119,315,9):pxbox(657,660,y,y+2,7.3,10.1,1,'798_lattice_vertical')
for z in [7.3,8.0,8.7,9.4,10.1]:pxbox(657,660,119,316,z,z+.10,1,'798_lattice_horizontal')
# Tie screen at structural bands, retaining real shallow air behind it.
for z in [7.3,10.1]:pxbox(648,660,119,316,z,z+.12,1,'798_screen_band_attachment')
# Observed windows on photographed outer east face and north end only, not invented rear repeats.
def window_east(y0,y1,x,z0,z1):
 pxbox(x-1,x+1,y0,y1,z0-.04,z1+.04,2,'observed_east_window_approx_bays')
 for y in [y0,(y0+y1)/2,y1]:pxbox(x,x+2,y-.65,y+.65,z0,z1,1,'window_mullion')
 for z in [z0,z0+.55,z1]:pxbox(x,x+2,y0,y1,z-.04,z+.04,1,'window_transom')
for i in range(4):
 z=3.4+3.4*i
 for y in ([116,159,288] if i==0 else [116,159,202,245,288]):window_east(y,y+34,656 if i==3 else 650,z+.65,z+2.45)
# Overlap frame feet into supporting wall/column junction; remove incidental enclosed corner slivers.
for y in [150,193,236,279]:pxbox(649,652,y-.8,y+.8,7.39,7.48,1,'window_frame_foot_overlap')
#799 southern low wing exterior is a source-consistent candidate, not unique surveyed registration.
def window_south(x0,x1,y,z0,z1):
 pxbox(x0,x1,y-1,y+1,z0,z1,2,'799_south_low_wing_window_approximate_bays')
 for x in [x0,(x0+x1)/2,x1]:pxbox(x-.7,x+.7,y,y+2,z0-.03,z1+.03,1,'799_window_mullion')
 for z in [z0,z0+.55,z1]:pxbox(x0,x1,y,y+2,z-.04,z+.04,1,'799_window_transom')
for i in range(3):
 z=3.4+3.4*i
 if i<2:pxbox(130,568,385.5,387.5,z+.25,z+3.15,3,'799_south_weathered_gray_floor_band')
 for x in [142,208,274,340,406,472]:window_south(x,x+56,387.5 if i<2 else 386,z+.65,z+2.45)
# Photo799 attached external arrival/flight: local extent and elevation approximate, not full terrain.
pxbox(190,252,384,410,3.22,3.54,1,'799_south_attached_entry_landing')
for i in range(12):pxbox(250+i*6,258+i*6,387,410,.60,3.4-i*.225,6,'799_south_external_descending_steps')
for x in [194,246]:pxbox(x-2,x+2,390,406,0,3.3,1,'799_south_landing_supports')
for y in [387,408]:
 a=trace([(250,y)])[0];b=trace([(326,y)])[0];beam((*a,4.15),(*b,1.43),.18,1,'799_sloping_side_handrail')
 for x,z in [(250,3.4),(288,2.0),(326,.70)]:pxbox(x-1.5,x+1.5,y-1.5,y+1.5,z-.03,z+.98,1,'799_side_handrail_posts')
pxbox(190,252,408,410,3.50,4.15,1,'799_landing_outer_parapet')
pxbox(318,332,385,412,0,.75,5,'799_stair_lower_local_contact')
# Small roof projection visible in both photos, approximate height over common north-east service core.
pxbox(260,370,95,148,17,19.60,3,'visible_bounded_roof_service_projection')
pxbox(258,372,93,150,19.55,19.73,4,'visible_roof_projection_flat_cap')
# Main exterior entry flight802 and side grade stair799; no full terrain slab.
pxbox(646,704,192,256,0,.65,5,'east_entry_bounded_ground_contact')
for i in range(14):pxbox(698-i*3.5,704-i*3.5,194,254,.60,.8+(i+1)*.185,6,'main_east_entry_steps')
pxbox(646,655,192,256,3.25,3.54,1,'entry_upper_arrival')
# Basement south approach aligns with801 lower exits, registered by its two common stair anchors.
pxbox(184,230,386,420,0,.65,5,'south_B1_entrance_local_contact')
for i in range(5):pxbox(188,226,414-i*5,420-i*5,.6,.70+(i+1)*.05,6,'B1_south_short_entry_steps')
HEIGHT_SCALE=.75 # common proportional height approximation, not measured floor heights
parts=[p.scale((SCALE,SCALE,SCALE*HEIGHT_SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學道藩樓','revision':'v3','scope':'complete C-shaped main body, narrow attached neck, two-storey hall with local mezzanine, local entrances and grade contacts','coordinate_transform':'809 master X=(px-115)/16 Y=(386-py)/16, scale4mm per approximate unit','outline_reading_pixels':full,'anchors':{'north_stair':[297,332,100,164],'south_round_stair':[184,225,276,329],'east_round_stair':[488,568,202,233]},'floor_elevations_design_units':[3.4,6.8,10.2,13.6,17.0],'common_height_factor':HEIGHT_SCALE,'799_registration':'Southern low wing exterior SW candidate, consistent handedness and three visible rows, not unique surveyed camera. One coarse roof projection over registered north stair; perspective/occlusion tested across both photos, not uniquely measured.','annex_cavities':'Interior proxy only, not inferred full-floor lightwells; local mezzanine pocket separate','annex_mapping':'803 translation(+360,-140)px, width match of40px corridor; selected60px neck length is approximate, never paper whitespace distance','limits':['Fire equipment diagrams not as-built survey','Photo years unknown, not verified2026 condition','Heights, corridor length, roof service height and fine windows approximate','Unknown rear neutral, not mirrored','No physical print certification; enclosed annex cavities and thin lattice need manufacturing assessment']}
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
