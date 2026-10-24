"""NCCU Lohas Shop — source-relative approximate complete main-building exterior."""
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
palette=[('warm_weathered_concrete','#C5C4B8',255),('ivory_screen_blocks','#DDDCCF',255),('opaque_shop_glazing','#536566',255),('canopy_green_metal','#496B5C',255),('flat_roof_concrete','#A6AAA2',255),('bounded_stone_contact','#929086',255),('tan_rail_metal','#BAA272',255),('screen_dark_recess','#71736A',255)]
def q(v):return round(v*1024)/1024
def poly(points,z0,z1):return CrossSection([[(q(x),q(y)) for x,y in points]],fillrule=__import__('manifold3d').FillRule.EvenOdd).extrude(q(z1)-q(z0)).translate((0,0,q(z0)))
def cube(x0,x1,y0,y1,z0,z1):
 x0,x1,y0,y1,z0,z1=map(q,(x0,x1,y0,y1,z0,z1));return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def trace(points):return [((x-525)/25,(510-y)/25) for x,y in points]
def pb(x0,x1,y0,y1,z0,z1,c,n):
 a,b=trace([(x0,y1),(x1,y0)]);add(cube(a[0],b[0],a[1],b[1],z0,z1),c,n)
def pp(points,z0,z1,c,n):add(poly(trace(points),z0,z1),c,n)
# Shared605 column frame;607 affine x=(x-156)*.954+150,y=(y-245)*.964+330.
body=[(150,330),(365,330),(365,383),(525,383),(525,510),(900,510),(900,690),(150,690)]
base=[(685,483),(719,483),(719,510),(900,510),(900,535),(970,535),(970,670),(900,670),(900,690),(685,690)]
# B1 right-two-bay only; enclosing wall shell open into actual stair throat.
b1=poly(trace(base),0,3.2)-poly(trace([(693,491),(711,491),(711,518),(892,518),(892,543),(962,543),(962,662),(892,662),(892,682),(693,682)]),.28,3.30)
add(b1,5,'604_partial_right_two_bay_B1_open_stair_throat')
pb(685,719,483,518,2.85,3.25,5,'604_B1_NW_small_projection_bounded_cover_not_new_upper_wing')
# Minimal uphill contacts, not a full underground storey or overall site slab.
pp(body,2.85,3.25,5,'605_thin_firstfloor_contact_slab_not_fullB1')
# Finite perimeter contact-skirts reach common model datum: not a full B1 room.
# Main non-B1 undersurface stays open between strips; no added landscape/site slab.
for a,b in zip(body,body[1:]+body[:1]):
 if a[0]==b[0]:
  if a[0]<685:pb(a[0]-2.5,a[0]+2.5,min(a[1],b[1]),max(a[1],b[1]),0,2.91,5,'nonB1_finite_perimeter_grade_contact')
 else:
  lo=min(a[0],b[0]);hi=min(max(a[0],b[0]),687)
  if hi>lo:pb(lo,hi,a[1]-2.5,a[1]+2.5,0,2.91,5,'nonB1_finite_perimeter_grade_contact')
# Continuous actual ground-floor occupied rooms, not an open all-floor colonnade.
pp(body,3.2,6.65,0,'605_two_storey_L_ground_shop_mass')
pp(body,6.60,10.0,0,'607_two_storey_L_upper_rooms_mass')
pp(body,9.96,10.20,4,'bounded_flat_roof_no_new_tower')
# B1 stair exterior enclosure attaches to east end, but no third storey.
pb(900,970,535,670,3.05,10.0,0,'right_attached_internal_stair_enclosure')
pb(900,970,535,670,9.96,10.20,4,'right_stair_flat_roof_same_height_no_tower')
# Cut real stair throat from mass/slab. Interior floors not broadly simulated.
for i,r in enumerate(part_records):
 if r['name'] in ['605_thin_firstfloor_contact_slab_not_fullB1','right_attached_internal_stair_enclosure']:
  a,b=trace([(905,664),(964,541)]);parts[i]=(parts[i]-cube(a[0],b[0],a[1],b[1],.25,9.70)).as_original();material_for_id[parts[i].original_id()]=r['material']
# B1 flight ends at first-floor north landing. Grounded risers are connected into eastwall.
for i in range(15):pb(930,966,560+i*6,566+i*6,.24,3.2-i*(2.9/15),5,'B1_internal_returning_flight_distinct_from_outer_stair')
pb(905,966,541,561,2.95,3.25,5,'B1_internal_top_landing')
# Upper returning stair in same finite rightend well, two storeys not a tower.
for i in range(15):
 top=6.65-i*(3.45/15);pb(930,966,560+i*6,566+i*6,top-.32,top,5,'right_internal_upper_finite_thickness_flight')
# Finite well-internal circulation plates: no full interior reconstruction.
pb(905,929,559,667,2.95,3.25,5,'right_well_west_1F_connecting_aisle')
pb(905,966,649,670,2.95,3.25,5,'right_upperflight_south_1F_foot_landing')
pb(905,966,541,561,6.40,6.70,5,'right_internal_secondfloor_landing')
# Entrance opening in south side of B1 staircase housing.
i=next(i for i,r in enumerate(part_records) if r['name']=='right_attached_internal_stair_enclosure');a,b=trace([(910,675),(950,660)]);parts[i]=(parts[i]-cube(a[0],b[0],a[1],b[1],3.2,5.8)).as_original();material_for_id[parts[i].original_id()]=0
# Real two-level sideportal cuts across stair enclosure and main-body mass.
# Interior rooms remain exterior proxies; these bounded entry recesses do not pretend full surveyed interiors.
for i,r in enumerate(part_records):
 if r['name'] in ['605_two_storey_L_ground_shop_mass','607_two_storey_L_upper_rooms_mass','right_attached_internal_stair_enclosure']:
  for z0,z1 in [(3.25,5.85),(6.70,9.30)]:
   a,b=trace([(880,560),(907,542)]);parts[i]=parts[i]-cube(a[0],b[0],a[1],b[1],z0,z1)
  parts[i]=parts[i].as_original();material_for_id[parts[i].original_id()]=r['material']
# Left full-width stair at shortend. Separate from continuous longface walkway/ramp.
pb(70,150,330,730,0,2.01,5,'left_steps_finite_grade_contact')
for i in range(7):pb(70+i*6,150,330,730,2.0,2.0+(i+1)*1.2/7,5,'left_broad_shortend_external_steps')
pb(110,150,330,730,3.14,3.25,5,'left_end_top_platform')
pb(145,970,690,730,3.10,3.26,5,'long_shop_walkway_open_under_canopy')
# Bounded ramp profile rising leftwards from right lower approach, alongside main walkway.
a,b=trace([(150,752),(935,730)])
vs=np.array([[a[0],a[1],0],[b[0],a[1],0],[a[0],b[1],0],[b[0],b[1],0],[a[0],a[1],3.26],[b[0],a[1],2.0],[a[0],b[1],3.26],[b[0],b[1],2.0]])
vs=np.vectorize(q)(vs) # same grid as flush landing; avoid microscopic mismatched top sliver
tm=trimesh.convex.convex_hull(vs);add(Manifold(Mesh(np.asarray(tm.vertices,dtype=np.float32),np.asarray(tm.faces,dtype=np.uint32))),5,'long_front_grounded_ramp_distinct_from_stair')
pb(145,155,730,752,0,3.26,5,'ramp_high_landing_flush_with_walkway')
pb(935,1010,730,767,0,2.0,5,'continuous_ramp_and_right_stair_localgrade_landing')
# Short east outer stair at the end of same continuous walkway, not B1internal flight.
pb(968,1010,675,731,0,2.01,5,'right_outer_steps_finite_grade_contact')
for i in range(7):pb(968,1010,675,683+i*8,2.0,3.2-i*1.2/7,5,'right_outer_short_approach_stair')
pb(960,974,665,731,3.12,3.28,5,'right_outer_stair_top_landing')
# Small inner elbow stair retained as separate five-rise interface.
pb(554,594,485,512,0,2.01,5,'elbow_steps_finite_grade_contact')
for i in range(5):pb(554,594,485+i*5,512,2.0,2.0+(i+1)*1.2/5,5,'inner_elbow_small_external_stair')
# Local grade z2 is distinct from arbitrary B1 cutbase z0. Bounded terrain
# aprons provide visible lowlandings, with approximate cut slopes, not surveyed terrain.
pb(50,71,330,730,0,2.0,5,'left_stair_visible_low_localgrade_landing')
pb(554,594,470,486,0,2.0,5,'inner_elbow_visible_low_localgrade_landing')
def grade_slope(x0,x1,y0,y1,axis,high_at,name):
 a,b=trace([(x0,y1),(x1,y0)]);a=tuple(map(q,a));b=tuple(map(q,b))
 xy=[(a[0],a[1]),(b[0],a[1]),(a[0],b[1]),(b[0],b[1])]
 heights=([0,2,0,2] if high_at=='max' else [2,0,2,0]) if axis=='x' else ([2,2,0,0] if high_at=='max' else [0,0,2,2])
 vs=np.array([[x,y,0] for x,y in xy]+[[x,y,z] for (x,y),z in zip(xy,heights)])
 tm=trimesh.convex.convex_hull(vs);add(Manifold(Mesh(np.asarray(tm.vertices,dtype=np.float32),np.asarray(tm.faces,dtype=np.uint32))),5,name)
grade_slope(20,50,330,730,'x','max','left_landing_bounded_approx_grade_slope_to_B1_cutdatum')
grade_slope(935,1010,767,800,'y','min','right_shared_landing_bounded_approx_grade_slope')
grade_slope(554,594,450,470,'y','max','inner_elbow_landing_bounded_approx_grade_slope')
# Photographic translucent cover represented opaque green structural proxy.
pb(109,151,330,732,6.30,6.44,3,'shortend_green_attached_cover')
pb(145,971,689,736,6.30,6.44,3,'longface_green_attached_cover')
for y in [340,415,510,600,725]:pb(111,114,y-1.5,y+1.5,3.15,6.38,3,'left_cover_support_posts')
for x in [150,257,365,472,579,686,793,900,969]:
 pb(x-1.5,x+1.5,731,734,3.12,6.38,3,'long_cover_support_posts')
 pb(x-1.5,x+1.5,688,737,6.22,6.40,3,'long_cover_crossbars')
# Upper screen stays opaque: backing + coarse shallow block relief, not whole glass floor.
pb(149,151,342,680,6.88,9.35,7,'shortend_opaque_screen_backing')
pb(157,891,689,691,6.88,9.35,7,'longface_opaque_screen_backing')
for row in range(8):
 z=6.90+row*.30
 for y in range(344+(row%2)*5,680,10):pb(147,151,y,y+6,z,z+.24,1,'shortend_coarse_perforated_block_proxy')
 for x in range(160+(row%2)*5,891,10):pb(x,x+6,689,693,z,z+.24,1,'longface_coarse_perforated_block_proxy')
# Shop openings are opaque inset panels with true surrounding walls; no image textures/signs.
for x0,x1 in [(165,242),(270,350),(420,550),(595,710),(750,870)]:
 pb(x0,x1,689,691,3.27,5.85,2,'long_shop_door_window_opaque_proxy')
 for x in [x0,x1,(x0+x1)/2]:pb(x-.8,x+.8,690,692,3.25,5.9,0,'shop_door_frame')
for y0,y1 in [(405,464),(585,645)]:pb(149,151,y0,y1,3.27,5.85,2,'shortend_shop_door_opaque_proxy')
# Narrow rightend photo602 window; unseen rear windows not invented or mirrored.
pb(899,901,674,687,7.0,9.0,2,'602_rightend_upper_narrow_window')
# Front ramp rail follows ramp gradient; walkway guard remains separately horizontal.
for i,x in enumerate(range(155,936,65)):
 z=3.26-(x-150)/785*1.26;pb(x-1,x+1,751,753,z-.03,z+1.0,6,'ramp_tan_guard_posts')
for z in [.48,1.0]:
 a,b=trace([(150,752),(935,752)]);beam((a[0],a[1],3.26+z),(b[0],b[1],2.0+z),.065,6,'sloped_ramp_guard')
# Low rail by external right stair joins walkway top, not neighbour hall.
for x in [969,1009]:
 for y in [680,704,728]:pb(x-1,x+1,y-1,y+1,2.0,4.15-(y-675)/56*1.2,6,'right_outer_stair_guard_posts')
 a,b=trace([(x,675),(x,731)]);beam((a[0],a[1],4.15),(b[0],b[1],2.95),.065,6,'right_outer_stair_sloped_rail')
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學樂活小舖','inventory':'60-13','revision':'v4','scope':'complete two-storey L body, right-two-bay partial B1, five distinct stair/ramp interfaces','coordinate_transform':'605 master X=(px-525)/25 Y=(510-py)/25; scale4mm per approximate unit','outlines':{'aboveground':body,'partial_B1':base},'shared_plan_registration':{'604':'CCW90 then scale.401 offset(642,462) in605','605':'master original','607':'x=(x-156)*.954+150; y=(y-245)*.964+330'},'photo_mapping':'601 left shortend plus lower longface;602 right shortend plus SAME lower longface; same mesh no mirroring','limits':['Fire-layout diagrams not measured as-built','Capture dates unknown not2026condition','A12 is neighbour60-12 notshop60-13; neighbour omitted','Roof bounded flatcap; heights fine openings and colors approximate','Upper block screen opaque coarse relief, no source textures','Interior partitions omitted; partialB1 stair throat only','Localgrade z2 landing and bounded approximate slopes differ from arbitrary B1 cutdatum z0;not measured terrain','NonB1 finite perimeter grade contacts approximate terrain; open underside between strips,not full basement','B1/2F sideportal recesses enter mass;full interior rooms omitted;upperflight usesfinite.32thick plates soB1routeheadspace staysopen','No physical print or supportfree claim']}
# Coalesce same-material construction primitives before final material Boolean. This removes
# artificial coplanar construction seams without nearest recolouring across material boundaries.
grouped=[];group_material_ids={}
for col in range(len(palette)):
 same=[part for part,record in zip(parts,part_records) if record['material']==col]
 g=Manifold.batch_boolean(same,OpType.Add).as_original()
 group_material_ids[g.original_id()]=col;grouped.append(g)
parts=grouped;material_for_id=group_material_ids
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
# Preserve Boolean run provenance through simplification: never nearest-surface paint broad triangles.
m=m.set_tolerance(0.000001).simplify(0.000001)
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
