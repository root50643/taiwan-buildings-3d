"""NCU off-campus Lulin SLT 1999 main building, 2022/2023 visible exterior.
Original photographic approximation, NOT 2026 survey, BIM or operating roof model.
Front = negative Y. All dimensions in display millimetres are inferred, not measured.
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
def octagon(cx,cy,b):
 a=b*math.tan(math.pi/8)
 return Polygon([(cx-a,cy-b),(cx+a,cy-b),(cx+b,cy-a),(cx+b,cy+a),(cx+a,cy+b),(cx-a,cy+b),(cx-b,cy+a),(cx-b,cy-a)])
def loft(a,z,b,w):return Manifold.hull_points(np.array([(x,y,z) for x,y in a.exterior.coords[:-1]]+[(x,y,w) for x,y in b.exterior.coords[:-1]]))
def rod(a,b,r=.6):
 a=np.asarray(a,float);b=np.asarray(b,float);d=b-a;length=np.linalg.norm(d);z=d/length
 q=np.array([0,0,1.]) if abs(z[2])<.9 else np.array([1.,0,0]);x=np.cross(q,z);x/=np.linalg.norm(x);y=np.cross(z,x)
 tr=np.column_stack([x,y,z,a-z*.05]);return Manifold.cylinder(length+.10,r,r,12).transform(tr)
parts=[];material_for_id={};part_records=[]
palette=[('white_sheet_clad_walls','#E8EAE7',255),('cool_white_roofs_and_shutters','#DCE2E2',255),('grey_metal_frames_rails_ladder','#98A3A5',255),('dark_window_and_door_insets','#263E44',255),('entrance_gable_edge_dark_grey_green','#4D605D',255),('invented_neutral_display_base','#747C7C',255)]
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
def line(a,b,name,r=.6,col=2):add(rod(a,b,r),col,name)
# Artificial display base, not site boundary or topographic reconstruction.
add(box(0,-3,0,192,98,3),5,'added_display_plinth_not_real_site')
# Low continuous gable wing adjoins the higher square flat-roof observation block.
add(box(-37,0,2.8,100,68,29.2),0,'low_long_wing_solid_exterior_mass')
add(box(48,0,2.8,70,68,41.2),0,'high_observing_block_solid_exterior_mass')
add(yz(Polygon([(-35.4,31.5),(0,39),(35.4,31.5)]),-88.4,102.8),1,'shallow_gable_long_wing_roof')
add(box(48,0,43.4,73.2,71.2,2.2),1,'high_block_projecting_flat_roof_plate')
# Low eave fascia is a deliberate small relief, not a full-height green awning.
for y in [-35.1,35.1]:add(box(-37,y,31.5,102.7,.9,1.3),2,'wing_eave_trim')
# Sparse source-like corrugation ribs; real corrugation pitch is unknown and reduced.
for x in np.arange(-85,12,4):
 for side in [-1,1]:
  p=[(side*35.1,31.60),(0,39.06)]
  add(yz(strip(p,.32),x-.18,.36),1,'simplified_wing_roof_standing_seam')
# Closed octagonal housing, no hemisphere, telescope, dark open slot or optics.
outer=octagon(48,0,31.8);top=octagon(48,0,17.0)
add(slab(outer,45.3,21.0),0,'upright_octagonal_observing_drum')
add(loft(outer,66.1,top,85.0),1,'inward_sloping_octagonal_top')
add(slab(octagon(48,0,32.0),46.0,1.3),1,'octagonal_lower_band')
add(slab(octagon(48,0,32.0),65.6,.8),1,'octagonal_shoulder_seam')
add(slab(top,84.7,1.2),1,'narrow_flat_top_plate')
# Two proud, side-by-side CLOSED shutters. Their broad front rectangular faces
# continue onto sloping top faces; a slim central separator is not an open slot.
for i,x in enumerate([39.65,56.35]):
 add(box(x,-32.0,47.0,16.25,4.8,22.0),1,f'closed_front_observing_shutter_{i+1}')
 add(yz(Polygon([(-34.4,68.7),(-17.0,85.6),(-10.0,85.6),(-10.0,68.7)]),x-8.125,16.25),1,f'closed_shutter_sloped_top_{i+1}')
 for sx in [-1,1]:add(box(x+sx*7.8,-34.55,47.2,.65,.55,21.8),2,f'shutter_{i+1}_vertical_edge')
 for z in [47.3,68.3]:add(box(x,-34.55,z,16.25,.55,.65),2,f'shutter_{i+1}_horizontal_edge')
 for xx in np.arange(x-6.8,x+7,2):add(box(xx,-34.45,48.2,.20,.25,19.7),1,f'shutter_{i+1}_reduced_corrugation')
# Lateral proud rail/beam ends at distinct levels, intentionally not LOT awnings.
add(box(48,-29.0,52.8,75.2,3.0,2.6),1,'continuous_front_shutter_rail_with_lateral_ends')
for side in [-1,1]:
 add(box(48+side*21.6,0,75.0,14.0,3.0,2.6),1,'upper_lateral_rail_end')
# Rectangular top guardrails with source-like open bars; count strengthened/simplified.
xs=[33.5,48,62.5];ys=[-14.5,14.5]
for x in xs:
 for y in ys:line((x,y,85.0),(x,y,95.0),'top_guardrail_post',.60)
for z in [88.0,91.4,94.6]:
 for y in ys:line((33.5,y,z),(62.5,y,z),'top_guardrail_front_rear_bar',.55)
 for x in [33.5,62.5]:line((x,-14.5,z),(x,14.5,z),'top_guardrail_side_bar',.55)
# Back cage ladder, vertical on drum then inclined over inward-sloping roof.
# The two stringers and their rung/hoop air spaces are real geometry, never a slab.
ladder_x=42.0;half=3.7
stages=[((33.8,45.3),(33.8,66.8)),((33.8,66.8),(17.6,85.7))]
for j,(p,q) in enumerate(stages):
 for x in [ladder_x-half,ladder_x+half]:line((x,*p),(x,*q),f'rear_ladder_stringer_{j}',.65)
 for t in np.linspace(.03,.97,7 if j==0 else 6):
  y=p[0]+t*(q[0]-p[0]);z=p[1]+t*(q[1]-p[1]);line((ladder_x-half,y,z),(ladder_x+half,y,z),f'rear_ladder_rung_{j}',.52)
# Stand-offs physically connect the cage ladder to octagonal drum and roof.
for z in [47,61,66]:
 for x in [ladder_x-half,ladder_x+half]:line((x,30.8,z),(x,34.1,z),'rear_ladder_standoff',.65)
for y,z in [(26.5,75.4),(18.0,85.0)]:
 for x in [ladder_x-half,ladder_x+half]:line((x,y-2,z-1.5),(x,y+.5,z+.5),'sloped_ladder_standoff',.65)
# Five half-round outward cage hoops and three longitudinal safety ribs.
# Hoops are horizontal for vertical stage, tilted normal to slope for upper stage.
hoops=[]
for y,z,angle in [(33.8,51.5,0),(33.8,59,0),(33.8,66.5,0),(27.2,74.5,40.6),(20.2,82.7,40.6)]:
 a=math.radians(angle);curve=[]
 for t in np.linspace(0,math.pi,17):
  s=4.0*math.sin(t);curve.append((ladder_x+4.0*math.cos(t),y+s*math.cos(a),z+s*math.sin(a)))
 for a,b in zip(curve,curve[1:]):line(a,b,'rear_protective_cage_hoop',.50)
 hoops.append(curve)
for k in [4,8,12]:
 for a,b in zip(hoops,hoops[1:]):line(a[k],b[k],'rear_cage_longitudinal_rib',.50)
# Closed, projecting gabled entry vestibule at the wing/block junction.
add(box(1,-37.0,2.8,24.0,8.0,29.0),0,'enclosed_entry_vestibule')
add(xz(Polygon([(-13.5,30.9),(-13.5,31.45),(1,36.65),(15.5,31.45),(15.5,30.9)]),-43.2,10.5),4,'entry_gable_roof_dark_edge')
add(xz(strip([(-13.5,31.8),(1,37.0),(15.5,31.8)],1.0),-43.3,10.6),1,'entry_gable_roof_white_top')
# Double closed doors with lower and upper panels, relief grilles simplified.
for i,x in enumerate([-4.2,6.2]):
 add(box(x,-41.15,3.1,9.7,.7,26.9),2,f'closed_entry_door_leaf_{i+1}')
 for z,h in [(5.0,7.2),(15.1,13.3)]:add(box(x,-41.55,z,7.7,.45,h),3,f'door_leaf_{i+1}_dark_inset')
 for xx in [x-2.6,x,x+2.6]:add(box(xx,-41.65,5.0,.45,.4,23.2),2,f'door_leaf_{i+1}_grille_vertical')
 for z in [8,11,17,21,25]:add(box(x,-41.65,z,7.8,.4,.45),2,f'door_leaf_{i+1}_grille_crossbar')
 add(box(x+(3.4 if i==0 else -3.4),-41.8,12.5,.7,1.0,2.3),2,f'door_leaf_{i+1}_handle')
# Four principal front windows: two in low wing, two in high block, not copied rear.
front_windows=[(-69.0,15.0),(-36.0,15.0),(31.5,14.0),(66.7,14.0)]
for i,(x,z) in enumerate(front_windows):
 w=11.5;h=12.5
 add(box(x,-34.15,z,w+1.5,.75,h+1.5),2,f'front_window_{i+1}_outer_frame')
 add(box(x,-34.6,z+.75,w,.45,h),3,f'front_window_{i+1}_closed_dark_inset')
 for xx in [x-3.8,x,x+3.8]:add(box(xx,-34.9,z+.75,.45,.4,h),2,f'front_window_{i+1}_simplified_grille')
 for zz in [z+4,z+8.5]:add(box(x,-34.9,zz,w,.4,.45),2,f'front_window_{i+1}_grille_crossbar')
# Front narrow wall louver between high-block windows; reduced count.
add(box(49.0,-34.35,25.5,2.5,1.0,6.0),2,'front_high_block_louver')
for z in np.arange(26,31,.95):add(box(49.0,-34.9,z,2.6,.3,.3),1,'front_louver_slat')
# Wing-end two small vents supplied by reverse photo. No invented rear window row.
for y,w,h,col in [(-11,5,6,3),(11,2.5,5,2)]:add(box(-87.25,y,21.0,.8,w,h),col,'wing_gable_end_small_vent')
# Very sparse panel joints distinguish white sheet cladding; shallow attached detail.
for x in [-80,-58,-47,-25,20,43,55,78]:
 add(box(x,-34.04,3.0,.18,.18,28.2 if x<13 else 40.1),1,'reduced_front_sheet_joint_relief')
# Small footing strip only, not fabricated topography, tanks or neighboring sheds.
add(box(0,-37.0,2.7,28,14,1),5,'added_entry_display_step')
FEATURES=dict(estimated_not_surveyed=True,school='國立中央大學',campus='鹿林天文台觀測基地',off_campus=True,slug='ncu-lulin-slt-main-building',target_path='國立中央大學/鹿林天文台觀測基地/buildings/ncu-lulin-slt-main-building',building_completion='1999-01',source_appearance='2022-07-10 front photo page and 2023-06-30 EXIF reverse photos; not asserted 2026 condition',front_direction='negative Y',report_octagonal_roof_m=6.0,report_does_not_specify_across_flats_or_corners=True,display_dimensions_not_real_metric_scale=True,wing_box_mm=[100,68,29.2],high_block_box_mm=[70,68,41.2],front_window_count=4,front_window_centers_x_mm=[x for x,z in front_windows],closed_entry_door_leaf_count=2,closed_shutter_count=2,octagonal_drum_sides=8,octagon_across_flats_display_mm=63.6,octagon_lower_z_mm=45.3,octagon_shoulder_z_mm=66.1,octagon_top_z_mm=85,guardrail_post_diameter_mm=1.2,guardrail_bar_diameter_mm=1.1,ladder_x_mm=ladder_x,ladder_halfwidth_mm=half,ladder_stringer_diameter_mm=1.3,ladder_rung_diameter_mm=1.04,cage_hoop_diameter_mm=1.0,cage_hoop_count_simplified=5,plinth_dimensions_mm=[192,98,3],generator_boolean_tolerance_mm=.001,shutters_closed=True,interior_representation='solid exterior mass; no optical equipment or room partitions',plinth_is_added_not_real_site=True,uncertain=['all display millimetres and proportional dimensions','exact roof slopes and sheet pitch','rear tiny penetrations and unseen fixings','guardrail/ladder/hoop counts simplified and strengthened','shutter rail working mechanism not reconstructed'],omitted=['LOT control centre','separate small instrument sheds','water tanks and temporary ladders/equipment','telescope optics/interior rooms','terrain trees antennae people and cables','source photographs and annual report pages'],no_actual_print=True,support_free_certified=False)
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.001)
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
