"""Tree Song, NTU Experimental Forest Xitou: single 2019 exhibition house.
Photograph/drawing-grounded exterior approximation. No measured scale or 2026 claim.
Display millimetres, front=-Y, fixed arched bay=-X. Source images not included.
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
palette=[('warm_timber_shell_floor_and_fascia','#AC754B',255),('woven_cedar_slat_relief','#CC955C',255),('completed_teal_entry_and_window_frame','#639486',255),('dark_green_grey_shingle_roof','#53655F',255),('solid_glazing_display_alpha_not_STL_transparency','#42625E',170),('skylight_metal_seams','#A1ACAD',255),('dark_opaque_screen_backing_and_support_feet','#554739',255)]
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
def line(a,b,name,r=.4,col=5):add(rod(a,b,r),col,name)
# Circle-segment barrel curve, one continuous main roof only.
def rz(y,half=55.,rise=25.,top=101.):
 radius=(half*half+rise*rise)/(2*rise)
 return top-radius+math.sqrt(max(0,radius*radius-y*y))
def curve(half=55,rise=25,top=101,n=80):return [(float(y),rz(float(y),half,rise,top)) for y in np.linspace(-half,half,n+1)]
def band(c,t):return Polygon(c+[(y,z-t) for y,z in c[::-1]])
main_curve=curve();bay_curve=curve(32,18,95,64)
# A shallow raised timber floor, no invented landscape or display pedestal.
footprint=rect(-72,-50,72,50).union(rect(-92,-26,-70,26))
add(slab(footprint,3,3),0,'raised_floor_main_rectangle_and_single_bay')
# Perimeter support legs simplified from visible feet; hidden foundation not surveyed.
for x in [-68,-22,24,68]:
 for y in [-46,46]:add(box(x,y,0,3.5,3.5,3.1),6,'inferred_visible_perimeter_foot')
for y in [-22,22]:add(box(-88,y,0,3.5,3.5,3.1),6,'bay_visible_support_foot')
add(box(-9,-56,0,50,13,2.8),0,'low_entry_step')
add(box(-9,-53.1,2.7,47,6.5,1.2),0,'entry_step_upper_tread')
# Front opening has semicircular crown. Its rectangular glass leaves sit BEHIND it.
entry=Polygon([(-29.5,5.8),(11.5,5.8),(11.5,31.5)]+[(-9+20.5*math.cos(t),31.5+20.5*math.sin(t)) for t in np.linspace(0,math.pi,65)]+[(-29.5,5.8)])
front_shape=rect(-72,5.9,72,79.5).difference(entry)
add(xz(front_shape,-50,2.2),6,'front_opaque_backing_wall_with_real_arch_opening')
add(xz(rect(-32,6,14,78.3).difference(entry),-52.0,2.1),2,'green_outer_panel_arch_is_not_door_leaf')
# Entry painted board relief is shallow and stopped at the true opening.
for x in np.arange(-31.4,14,2.4):
 q=rect(float(x)-.06,6,float(x)+.06,78.1).difference(entry.buffer(.08))
 if not q.is_empty:add(xz(q,-52.12,.18),2,'reduced_teal_board_joint_relief')
add(box(-9,-52.1,53.2,46,.45,.7),2,'green_panel_cross_trim_above_arch')
# Narrow plain left-front return; remaining left/right fields have woven applique.
add(box(-65,-50.8,6,14,1.7,73.5),0,'plain_timber_left_front_return')
# Rear long wall and far short end are genuinely blind, not inferred windows.
add(box(0,48.9,6,144,2.2,73.5),6,'rear_long_blind_opaque_wall')
end_profile=Polygon([(-50,5.9),(50,5.9)]+[(y,rz(y)-1.5) for y in np.linspace(50,-50,73)])
add(yz(end_profile,69.8,2.2),6,'opposite_short_blind_wall')
# Main window-end wall includes shoulder closure and a bay connection aperture.
main_end=end_profile.difference(rect(-26,5.8,26,84.5))
add(yz(main_end,-72,2.2),0,'main_window_end_blind_shoulders_and_upper_gable')
# Window bay is a projecting rectangular box with its own lower curved cap.
bay_end=Polygon([(-26,5.9),(26,5.9)]+[(y,rz(y,32,18,95)-1.7) for y in np.linspace(26,-26,65)])
window=Polygon([(-20.5,11.5),(20.5,11.5),(20.5,24)]+[(20.5*math.cos(t),24+45*math.sin(t)) for t in np.linspace(0,math.pi,81)]+[(-20.5,11.5)])
add(yz(bay_end.difference(window),-92,2.2),0,'projecting_end_wall_with_tall_fixed_window')
for y in [-25,25]:add(box(-81,y,6,22,2.2,77.7),0,'projecting_window_bay_side_return')
add(yz(window.buffer(1.15).difference(window.buffer(-.05)),-92.15,2.4),2,'elongated_arch_fixed_window_teal_surround')
add(yz(window.buffer(.04),-91.3,1.05),4,'fixed_glass_solid_pane_not_an_open_door')
# Repeated, disclosed shallow timber-joint relief; not photogrammetric grain.
for y in np.arange(-49,50,3):
 if abs(y)>27:add(box(-72.08,float(y),6,.18,.16,72.5),0,'main_window_end_reduced_board_seam')
for y in np.arange(-25,26,2.6):
 q=rect(float(y)-.06,6,float(y)+.06,83.2).intersection(bay_end).difference(window.buffer(1.2))
 if not q.is_empty:add(yz(q,-92.1,.2),0,'bay_end_reduced_board_joint')
for y in [-26.12,26.12]:
 for x in np.arange(-90,-72,3):add(box(float(x),y,6,.16,.22,77.5),0,'bay_return_reduced_board_joint')
# Two static inward-open RECTANGULAR glazed door leaves, not quarter-circle leaves.
# They are approximately 90 degrees inward; the exterior semicircle masks top corners.
for side,x in [('left',-29.4),('right',11.4)]:
 add(box(x,-37.6,6,1.15,21.2,1.3),0,'inward_open_'+side+'_rectangular_door_bottom_frame')
 add(box(x,-37.6,51.0,1.15,21.2,1.3),0,'inward_open_'+side+'_rectangular_door_top_frame')
 for y in [-47.55,-27.65]:add(box(x,y,6,1.15,1.3,46.3),0,'inward_open_'+side+'_rectangular_door_stile')
 add(box(x,-37.6,7.2,1.02,19.0,44.0),4,'inward_open_'+side+'_rectangular_door_glass')
 add(box(x+(.65 if side=='left' else -.65),-28.1,26,.65,.8,3),5,'inward_open_'+side+'_door_handle')
# Conservative interior centre divider from plan: rear two-thirds, front aisle kept open.
add(box(-12,12.0,6,2.0,72,75.0),0,'simplified_internal_centre_divider_front_aisle_open')
# No exterior twin roof: the unequal internal ceiling vaults and furniture are omitted.
# Woven slats: paired opposite sine offsets around three horizontal rails.
# Exact count/pitch is deliberately reduced and rear pattern conservatively extrapolated.
def woven_front(xa,xb,y,back=False):
 for z in [6.6,18,40,62,76.5]:add(box((xa+xb)/2,y+(.55 if not back else -.55),z-.45,xb-xa,2.8,.9),1,'woven_horizontal_rail_rear' if back else 'woven_horizontal_rail_front')
 for i,x in enumerate(np.arange(xa+.65,xb-.3,2.5)):
  c=[(y+.65*((-1)**i)*math.cos(math.pi*(z-18)/22),float(z)) for z in np.linspace(6.2,77.0,65)]
  q=Polygon([(yy-.48,z) for yy,z in c]+[(yy+.48,z) for yy,z in c[::-1]])
  add(yz(q,float(x)-.5,1.0),1,'rear_conservatively_extrapolated_woven_slat' if back else 'front_alternating_bent_timber_slat')
woven_front(-58,-32,-51.9);woven_front(14,72,-51.9);woven_front(-72,72,51.9,True)
for z in [6.6,18,40,62,76.5]:add(box(71.35,0,z-.45,2.5,100,.9),1,'blind_end_woven_horizontal_rail')
for i,y in enumerate(np.arange(-49.2,50,2.5)):
 c=[(71.9+.65*((-1)**i)*math.cos(math.pi*(z-18)/22),float(z)) for z in np.linspace(6.2,77.0,65)]
 q=Polygon([(x-.48,z) for x,z in c]+[(x+.48,z) for x,z in c[::-1]])
 add(xz(q,float(y)-.5,1),1,'blind_end_alternating_bent_timber_slat')
# Main roofing is one continuous shell. True open shafts cut through that shell.
roof=yz(band(main_curve,2.4),-74.7,149.4)
well_centres=[(-30.,16.),(32.,16.)]
for x,y in well_centres:roof=roof-box(x,y,82,11.0,11.0,36)
add(roof,3,'single_continuous_main_segmental_barrel_roof')
add(yz(band(bay_curve,2.2),-95,24.1),3,'lower_short_projecting_window_bay_barrel_cap')
# Warm curved fascia at both main ends, and separate lower bay front lip.
for x in [-74.9,73.7]:add(yz(band(main_curve,2.0),x,1.2),0,'main_roof_curved_timber_fascia')
add(yz(band(bay_curve,2.0),-95.2,1.3),0,'lower_window_bay_curved_fascia')
# Shingle surface is simplified to a smooth green-grey shell; no tiny tile geometry.
# Two square raised wood-clad lightwells, each hollow below a four-hip glass cap.
for i,(x,y) in enumerate(well_centres):
 outer=box(x,y,91,14.5,14.5,17.0);inner=box(x,y,89,11,11,21)
 shell=(outer-inner)-box(0,0,0,400,400,0.1)
 # Trim bottom to roof exterior underside using intersection with vertical outside.
 # Lower shaft extends into room only at roof penetrations; intentionally simple vertical well.
 add(shell,0,f'square_raised_lightwell_{i+1}_hollow')
 for xx,yy in [(x-6.5,y),(x+6.5,y)]:add(box(xx,yy,106.6,1.2,15.4,1.2),5,f'skylight_{i+1}_cap_base_edge')
 for xx,yy in [(x,y-6.5),(x,y+6.5)]:add(box(xx,yy,106.6,15.4,1.2,1.2),5,f'skylight_{i+1}_cap_base_edge')
 base=[(x-7.7,y-7.7,107.6),(x+7.7,y-7.7,107.6),(x+7.7,y+7.7,107.6),(x-7.7,y+7.7,107.6)]
 apex=(x,y,113.8)
 glass=Manifold.hull_points(np.array(base+[apex]))-Manifold.hull_points(np.array([(a,b,c-.95) for a,b,c in base]+[(x,y,112.85)]))
 add(glass,4,f'skylight_{i+1}_four_slope_glass_cap_shell')
 for a,b in zip(base,base[1:]+base[:1]):line(a,b,f'skylight_{i+1}_base_metal_seam',.35)
 for a in base:line(a,apex,f'skylight_{i+1}_diagonal_hip_metal_seam',.35)
FEATURES=dict(estimated_not_surveyed=True,school='國立臺灣大學',campus='溪頭自然教育園區（實驗林校外基地）',off_campus=True,slug='ntu-xitou-tree-song',target_path='國立臺灣大學/溪頭實驗林/buildings/ntu-xitou-tree-song',building_completion='2019-02 according to project credits',source_publication='2019-12-03',individual_photo_capture_dates_unknown=True,all_29_source_jpegs_no_EXIF_dates=True,hosting_path_2022_not_capture_date=True,front_direction='negative Y',bay_direction='negative X',reported_area_m2=42,display_dimensions_not_survey_scale=True,main_footprint_mm=[144,100],bay_footprint_mm=[20,52],main_roof_count=1,lower_bay_roof_count=1,raised_square_lightwell_count=2,lightwell_centres_mm=well_centres,lightwell_outer_size_mm=14.5,lightwell_inner_size_mm=11.0,lightwell_glass_cap='hollow four-sided pyramid shell with metal hip seams, not open chimney',door_leaves=2,door_shape='rectangular glazed leaves behind semicircular outer panel',door_display_state='both inward-open approximately 90 degrees, static',bay_glazing='one elongated arched fixed pane',rear_and_far_short_end_blind=True,woven_screen='shallow bent vertical strips and horizontal rails over opaque backing; not through-wall lattice',rear_pattern_extrapolated=True,interior='accessible empty shell and simple centre divider; unequal internal vaults/furniture and sloping shaft internals omitted',no_landscape_plinth=True,visible_footing_count_simplified=10,generator_boolean_tolerance_mm=.001,uncertain=['all display dimensions and absolute scale','rear screen exact pattern and trim count','board counts and bending pitch; roof shingles omitted as subscale surface detail','hidden footing plan and exact roof/shaft thickness','door opening angle and internal divider top'],omitted=['neighboring servicecentre and university lodge','fallen sacred tree, walkways, exterior stairs and signs','temporary scaffolding and installation tape','people, furniture, lighting fixtures and equipment','unequal internal ceiling vaults, sloped inner shaft transitions','source originals and source crops'],physical_glazing_solid=True,STL_has_no_transparency=True,no_actual_print=True,support_free_certified=False)
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
