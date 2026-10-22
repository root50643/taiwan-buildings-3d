"""NYCU / TSMC Energy Education Center: completed Hsinchu permanent 2017 Orchid House.
Complete bounded exterior, not the 2014 Versailles temporary prototype.
Dimensions are approximate display millimetres; no measured or current-state claim.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
from shapely.geometry import Polygon,LineString,box as rect
from shapely.geometry.polygon import orient
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
def cross(p):
 loops=[]
 for q in (list(p.geoms) if p.geom_type=='MultiPolygon' else [p]):
  if q.is_empty:continue
  q=orient(q,sign=1);loops.append(np.array(q.exterior.coords[:-1]));loops.extend(np.array(a.coords[:-1]) for a in q.interiors)
 return CrossSection(loops)
def slab(p,z,h):return cross(p).extrude(h).translate((0,0,z))
def xz(p,y,d):return cross(p).extrude(d).transform(np.array([[1,0,0,0],[0,0,1,y],[0,1,0,0]],float))
def yz(p,x,w):return cross(p).extrude(w).transform(np.array([[0,0,1,x],[1,0,0,0],[0,1,0,0]],float))
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def strip(p,t):return LineString(p).buffer(t/2,cap_style=2,join_style=1,quad_segs=8)
def rod(a,b,r=.4):
 a=np.asarray(a,float);b=np.asarray(b,float);d=b-a;length=np.linalg.norm(d);zz=d/length
 q=np.array([0,0,1.]) if abs(zz[2])<.9 else np.array([1.,0,0]);xx=np.cross(q,zz);xx/=np.linalg.norm(xx);yy=np.cross(zz,xx)
 return Manifold.cylinder(length+.10,r,r,12).transform(np.column_stack([xx,yy,zz,a-zz*.05]))
parts=[];material_for_id={};part_records=[]
palette=[('white_aluminum_structure','#F0F3ED',255),('pale_aqua_translucent_envelope','#7DAFB6',185),('clear_glazing_closed_sliding_doors','#B7D6D8',25),('dark_roof_energy_modules','#223F51',255),('brown_timber_deck_and_steps','#956646',255),('gray_stone_plinth','#9A9F98',255),('warm_opaque_L_living_core','#D1BE9B',255),('white_bottle_thermal_glazing_pattern','#DCE8DD',210),('green_wall_foliage','#4C7851',255),('orchid_flower_simplification','#CEB7CB',255)]
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
def line(a,b,name,r=.4,col=5):add(rod(a,b,r),col,name)

# Display coordinates: east/front=-Y, west/back=+Y, north=+X, south=-X.
# All dimensions below are photo-proportioned display millimetres, NOT measured scale.
Y=74.;Z0=8.;EAVE=51.;RIDGE=91.;RX=20.;NORTH=62.;SOUTH=-68.
# A low printable rectangular plate is explicitly additional; stone plinth/deck are real.
add(box(0,-3,0,157,188,1.6),5,'additional_thin_rectangular_print_base_not_site_boundary')
add(box(0,0,1.5,146,164,4.6),5,'raised_stone_faced_foundation_plinth')
add(box(0,-1,5.9,140,160,2.1),4,'timber_platform_and_walk_edge')
# Broad east/front timber terrace, stepped down to surrounding plane.
for i in range(4):
 add(box(0,-92+i*3.5,1.5+i*1.6,137,7.1,1.7),4,f'broad_east_front_step_{i+1}')
add(box(0,-79,6.0,140,14,2.0),4,'front_timber_terrace')
# Sparse board grooves as material strips; not tiny source-exact plank counts.
for x in range(-66,67,6):add(box(x,-82,7.98,.22,15,.10),6,f'approximate_deck_board_seam_{x}')
# Stone joints are visible shallow ribs, bounded to source plinth rather than landscape.
for y in [-81.95,81.95]:
 for i in range(18):add(box(-68+i*8,y,1.8,.30,.20,3.7),0,f'plinth_joint_y{y}_{i}')
for x in [-72.95,72.95]:
 for i in range(20):add(box(x,-77+i*8,1.8,.20,.3,3.7),0,f'plinth_joint_x{x}_{i}')
# North facade is VERTICAL. Lower glass plus upper continuous clerestory.
add(box(NORTH,0,Z0,0.75,148,31.5),2,'north_lower_vertical_closed_glazing')
add(box(NORTH,0,39.5,.75,148,EAVE-39.5),1,'north_upper_horizontal_clerestory')
for z in [Z0,39.5,EAVE]:add(box(NORTH,0,z-.5,1.7,151,1.15),0,f'north_continuous_rail_z{z}')
for i,y in enumerate(np.linspace(-Y,Y,13)):
 add(box(NORTH,float(y),Z0,1.2,1.15,EAVE-Z0+.8),0,f'north_vertical_post_{i+1}')
# SOUTH facade inclines outward: base X=-60, top X=-68.
def southx(z):return -60.-8.*(z-Z0)/(EAVE-Z0)
for i,y in enumerate(np.linspace(-Y,Y,11)):
 add(rod((southx(Z0),float(y),Z0-.4),(southx(EAVE),float(y),EAVE+.4),.85),0,f'south_outward_tilted_primary_post_{i+1}')
# Open glass louver blades with genuine vertical gaps; no opaque replacement wall.
for j,z in enumerate(np.linspace(9.0,49.9,25)):
 x=southx(float(z))
 # 0.55 mm physical leaf inclined about its long axis: fragile by design, QA retained.
 q=Polygon([(x-1.45,z-.10),(x+1.15,z+.45),(x+1.15,z+1.0),(x-1.45,z+.45)])
 add(xz(q,-Y,2*Y),2,f'south_open_horizontal_louver_leaf_{j+1}')
for z in [Z0,EAVE]:add(box(southx(z),0,z-.5,1.8,151,1.2),0,f'south_boundary_rail_z{z}')
# Two different gables: east entrance and west thermal/bottle band.
gable=Polygon([(SOUTH,EAVE),(RX,RIDGE),(NORTH,EAVE)])
for y,label in [(-Y,'east'),(Y,'west')]:
 add(xz(gable,y-.35,.70),1,label+'_upper_translucent_asymmetric_gable')
 add(xz(gable.intersection(rect(-90,66.6,80,67.4)),y-.6,1.2),0,label+'_upper_gable_horizontal_transom')
 add(rod((SOUTH,y,EAVE),(RX,y,RIDGE),1.15),0,label+'_long_south_gable_rafter')
 add(rod((RX,y,RIDGE),(NORTH,y,EAVE),1.15),0,label+'_short_north_gable_rafter')
 add(box(-3,y,EAVE-.45,131,1.5,1.1),0,label+'_gable_base_crossrail')
 for i,x in enumerate(np.linspace(SOUTH+2,NORTH-2,15)):
  high=EAVE+(RIDGE-EAVE)*(x-SOUTH)/(RX-SOUTH) if x<RX else EAVE+(RIDGE-EAVE)*(NORTH-x)/(NORTH-RX)
  if high>EAVE+.3:add(box(float(x),y,EAVE,.50,.86,float(high-EAVE)),0,f'{label}_upper_gable_mullion_{i+1}')
# Main lower east face: tall translucent south field; broad clear sliding doors north.
east_outline=Polygon([(-60,Z0),(NORTH,Z0),(NORTH,EAVE),(SOUTH,EAVE)])
left=east_outline.intersection(rect(-90,0,-22,100));right=east_outline.intersection(rect(-22,0,80,100))
add(xz(left,-Y-.35,.70),1,'east_south_translucent_lower_field')
add(xz(right,-Y-.35,.70),2,'east_broad_closed_sliding_glass_entry')
for x in [-60,-42,-22,-5,12,29,46,62]:
 xx=southx(EAVE) if x==-60 else x
 add(rod((x,-Y,Z0-.2),(xx,-Y,EAVE),.7),0,f'east_lower_frame_x{x}')
add(box(0,-Y,Z0-.3,125,1.7,1.0),0,'east_bottom_entrance_sill')
for x in [-5,29]:add(box(x+1,-Y-.6,22,.5,.8,4),0,f'sliding_door_handle_{x}')
# Western arrangement from reverse aerial: north narrow strip, central small window,
# and broad SOUTH patterned translucent band. Do not copy the south open louvers.
west_outline=east_outline
narrow=rect(42,Z0,47,34.5);window=rect(10,18,28,35);bottle=rect(-57,Z0+1,4,36.5)
remaining=west_outline.difference(narrow.union(window).union(bottle))
add(xz(remaining,Y-.35,.70),1,'west_lower_grouped_translucent_field')
add(xz(narrow,Y-.35,.70),2,'west_narrow_vertical_glazed_opening_unknown_function')
add(xz(window,Y-.35,.70),2,'west_small_two_sash_window')
add(xz(bottle,Y-.40,.80),7,'west_dense_bottle_thermal_translucent_band')
for name,p in [('narrow',narrow),('small_window',window),('bottle_band',bottle)]:
 add(xz(p.buffer(.65).difference(p.buffer(-.35)),Y-.7,1.4),0,'west_'+name+'_white_boundary_frame')
add(box(19,Y,18,.75,1.4,17),0,'west_small_window_central_sash')
# Dense vertical subdivisions and circular bottle-end cues are illustrative, not counted.
for i,x in enumerate(np.linspace(-55.8,2.8,13)):
 add(box(float(x),Y+.35,9,.45,.5,27.6),0,f'west_bottle_band_subdivision_{i+1}')
for i,x in enumerate(np.linspace(-54,1,12)):
 for j,z in enumerate(np.linspace(11,34,7)):
  # flattened transverse cylinders join the thermal glazing; solid, not punched holes.
  c=Manifold.cylinder(.28,.72,.72,12).rotate((90,0,0)).translate((float(x),Y+.65,float(z)))
  add(c,0,f'approximate_bottle_end_{i+1}_{j+1}')
for x in [-60,35,62]:add(rod((x,Y,Z0),(southx(EAVE) if x==-60 else x,Y,EAVE),.70),0,f'west_lower_outer_post_{x}')
add(box(0,Y,Z0-.3,125,1.6,1.0),0,'west_bottom_sill')
# Roof planes: actual aerial zones, not the paper cutaway checkerboard.
def rz(x):return EAVE+(RIDGE-EAVE)*(x-SOUTH)/(RX-SOUTH) if x<=RX else EAVE+(RIDGE-EAVE)*(NORTH-x)/(NORTH-RX)
def roof_piece(x1,x2,y1,y2,t=.65):
 return xz(Polygon([(x1,rz(x1)),(x2,rz(x2)),(x2,rz(x2)-t),(x1,rz(x1)-t)]),y1,y2-y1)
add(roof_piece(SOUTH,RX,-Y,Y),1,'continuous_south_roof_translucent_underpanel')
add(roof_piece(RX,NORTH,-Y,Y),1,'continuous_north_roof_translucent_underpanel')
# Long south slope: five dark parallel bands separated by clear/white strips.
for row in range(5):
 x1=SOUTH+3+row*16.3;x2=x1+13.7
 for col in range(8):
  ya=-Y+2+col*18.0;yb=ya+17.5
  add(roof_piece(x1,x2,ya,yb,.85).translate((0,0,.15)),3,f'south_energy_strip_{row+1}_module_{col+1}')
# Short north slope: dark upper strip and broad clear lower field.
for col in range(12):
 ya=-Y+2+col*12.;yb=ya+10.5
 add(roof_piece(RX+3,RX+15,ya,yb,.85).translate((0,0,.15)),3,f'north_upper_dark_zone_module_{col+1}')
# White rafters/purlins regularized for readability, quantities not as-built claims.
for i,y in enumerate(np.linspace(-Y,Y,13)):
 add(rod((SOUTH,float(y),EAVE-.8),(RX,float(y),RIDGE-.8),.45),0,f'south_roof_underside_rafter_{i+1}')
 add(rod((RX,float(y),RIDGE),(NORTH,float(y),EAVE),.58),0,f'north_roof_rafter_{i+1}')
for x in [SOUTH,-49,-32.7,-16.4,-.1,16.2,RX,RX+16,NORTH]:
 add(box(float(x),0,rz(x)-.15,1.0,151,1.0),0,f'roof_parallel_purlin_x{x}')
# Low L-shaped living core: south arm plus western cross arm, not a solid whole house.
# Keep a large double-height green core/open east+north region.
add(box(-43,0,Z0,1.2,128,30),6,'L_core_inner_south_partition')
add(box(-52,0,37,21,129,1.3),6,'L_core_south_arm_low_ceiling')
add(box(-5,49.5,Z0,78,1.2,30),6,'L_core_inner_west_partition')
add(box(-5,61,37,78,25,1.3),6,'L_core_west_arm_low_ceiling')
# Interior partitions are schematic; exact room doors and furniture are not reconstructed.
# A short opaque return completes the visible low L-core massing.
add(box(-43,-52,Z0,24,1.2,30),6,'L_core_south_east_return')
# Green wall stands in the high space, with a true passage to its north.
add(box(-3,21,Z0,70,1.1,53),0,'central_green_wall_white_backing')
for j,z in enumerate(np.linspace(11,58.5,14)):
 for i,x in enumerate(np.linspace(-35,30,16)):
  add(box(float(x),20.25,float(z),3.6,.85,2.6),8,f'green_wall_leaf_mass_{i+1}_{j+1}')
  if (i+2*j)%5==0:add(box(float(x)+.4,19.7,float(z)+.9,1.2,.45,1.0),9,f'orchid_color_cue_{i+1}_{j+1}')
FEATURES=dict(estimated_not_surveyed=True,school='國立陽明交通大學',campus='新竹科學園區教育研究場域',slug='nycu-tsmc-energy-education-center',target_path='國立陽明交通大學/新竹科學園區教育研究場域/buildings/nycu-tsmc-energy-education-center',name='台積電交大能源教育館（2017永久版蘭花屋）',opening_date='2017-04-21',site='新竹市園區二路101號台積新竹廠區；校外產學教育研究場域，非光復校區',not_2014_versailles_prototype=True,individual_photo_capture_dates_unknown=True,front_direction='east negative Y; west positive Y; north positive X; south negative X',reported_floor_area_m2=183.7,display_dimensions_not_survey_scale=True,roof_ridge_x_mm=RX,roof_ridge_z_mm=RIDGE,north_eave_x_mm=NORTH,south_eave_x_mm=SOUTH,eave_z_mm=EAVE,base_z_mm=Z0,facade_length_mm=2*Y,south_foot_x_mm=-60.,south_tilted_louver_blades_approximate=25,roof_south_dark_bands_approximate=5,roof_south_modules_per_band_approximate=8,roof_north_dark_band_modules_approximate=12,bottle_pattern_approximate=True,additional_print_base=True,inner_L_core=True,double_height_green_core=True,west_openings_distinct_from_east=True,west_not_south_louvers=True,roof_priority='okgo-3 completed aerial; Fig2 cutaway only interpretive, not copied patchwork',STL_has_no_transparency=True,all_glazing_physical_solids=True,uncertain=['all absolute dimensions and member thicknesses','ridge offset, slope and south tilt angles','roof energy module and clear-panel subdivision counts','louver and bottle-cell counts','interior fit-out and green-wall plant species/density','small opening hardware/function'],omitted=['neighboring massive gray building','car park, campus landscape and service systems','live IoT and monitoring systems','minute fittings, signage and furniture','raw source photographs and original paper'],no_actual_print=True,support_free_certified=False)
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.001).simplify(.001)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
centers=vs[fs].mean(axis=1);colors=np.empty(len(fs),dtype=int);maxdist=0
for start in range(0,len(fs),500):
 closest,dist,idx=trimesh.proximity.closest_point(source_tm,centers[start:start+500]);assert dist.max()<.002,dist.max();maxdist=max(maxdist,float(dist.max()));colors[start:start+500]=source_colors[idx]
t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');raw=(O/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0]
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
