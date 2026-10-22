"""NTOU Dream Fountain: complete bounded 2018 visible exterior approximation.
2018 is the source-photo year, not a construction date. No measured scale.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[('gray_aggregate_shaft_arms_drum','#AAA99C',255),('light_gray_basin_rim','#C6C5B8',255),('wet_brown_2018_steps','#8B6A40',255),('dark_dry_basin_floor_approximation','#565C50',255),('radial_metal_nozzle_tubes','#969FA0',255)]
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
def cyl(r,z,h,segments=128):return Manifold.cylinder(h,r,r,segments).translate((0,0,z))
def rod(a,b,r,segments=48):
 a=np.asarray(a,float);b=np.asarray(b,float);d=b-a;length=np.linalg.norm(d);zz=d/length
 q=np.array([0,0,1.]) if abs(zz[2])<.9 else np.array([1.,0,0]);xx=np.cross(q,zz);xx/=np.linalg.norm(xx);yy=np.cross(zz,xx)
 return Manifold.cylinder(length,r,r,segments).transform(np.column_stack([xx,yy,zz,a]))
# Display millimetres. D=34 is the central shaft diameter; not a surveyed scale.
D=34.;POOL_R=90.;POOL_INNER_R=78.;FLOOR_Z=3.;RIM_TOP=15.
add(cyl(POOL_R,0,FLOOR_Z),3,'approximate_solid_basin_bottom_unseen_depth_no_added_site_platform')
add(cyl(POOL_R,2.8,RIM_TOP-2.8)-cyl(POOL_INNER_R,2.7,RIM_TOP-2.7+.2),1,'complete_closed_annular_pool_wall_true_open_annular_channel')
# Six lower concentric steps, then a visibly taller upper circular pedestal.
# The 2013 dry gray base is explicitly NOT copied into this 2018 brown base.
STEPS=[(57.,2.8,11.),(53.,10.8,15.1),(49.,14.9,19.2),(45.,19.,23.3),(40.5,23.1,27.4),(35.5,27.2,31.5)]
for i,(r,z,top) in enumerate(STEPS):add(cyl(r,z,top-z),2,f'2018_lower_concentric_step_{i+1}_of_6')
add(cyl(29.,31.3,10.1),2,'2018_tall_upper_circular_pedestal_seventh_level')
add(cyl(D/2,41.2,85.),0,'central_vertical_cylindrical_shaft')
# Four directions AND FOUR separate heights; opposite pairs A/C and B/D.
# This coordinate frame is illustrative, not geodetic north/east.
ARMS=[dict(label='A_highest',axis='+X',direction=[1,0,0],center_z=110.,outer_length=40.),dict(label='B_second',axis='-Y',direction=[0,-1,0],center_z=91.,outer_length=41.),dict(label='C_third',axis='-X',direction=[-1,0,0],center_z=69.,outer_length=39.),dict(label='D_lowest',axis='+Y',direction=[0,1,0],center_z=52.,outer_length=36.)]
for arm in ARMS:
 d=np.array(arm['direction']);z=arm['center_z'];start=d*12.;end=d*(D/2+arm['outer_length']);start[2]=end[2]=z
 add(rod(start,end,10.3,80),0,arm['label']+'_closed_flat_end_horizontal_cylinder')
# Thick top drum overhang, no invented deep bowl, inner plumbing or mechanical hub.
add(cyl(26.,126.,18.),0,'wide_top_drum_flat_unseen_upper_surface_is_simplified_not_measured')
# Three-dimensional upper hemisphere, not a flat fan, cone, or solid ball.
# 37 is an editable representative count; number, angles and1.1mm thickness are NOT as-built claims.
NOZZLES=[];center=np.array([0.,0.,139.5]);radius=22.
for elevation,count,offset in [(90.,1,0.),(70.,8,9.),(50.,12,0.),(30.,16,11.25)]:
 for i in range(count):
  az=math.radians(offset+360.*i/count);el=math.radians(elevation);d=np.array([math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el)])
  end=center+radius*d;add(rod(center,end,.55,16),4,f'approximate_hemisphere_radial_nozzle_{len(NOZZLES)+1:02}')
  NOZZLES.append(dict(elevation_deg=elevation,azimuth_deg=offset+360.*i/count,start=center.tolist(),end=end.tolist(),diameter_mm=1.1))
FEATURES=dict(name='夢泉（2018可見版本）',school='國立臺灣海洋大學',campus='祥豐校區',slug='ntou-dream-fountain-2018',target_path='國立臺灣海洋大學/祥豐校區/buildings/ntou-dream-fountain-2018',estimated_not_surveyed=True,reference_photo_date='2018-07-28 local camera date, no timezone offset',source_year_is_not_construction_year=True,reference_period='2018 visible fountain;2013 photos supplement unchanged shaft/arms only;2025 handbook photo exposure unknown',display_dimensions_not_survey_scale=True,shaft_diameter_mm=D,shaft_z=[41.2,126.2],drum_radius_mm=26.,drum_z=[126.,144.],drum_hidden_internal_depth_unknown=True,drum_top_simplified_flat_surface=True,arms=ARMS,arm_radius_mm=10.3,opposite_pairs=[['A_highest','C_third'],['B_second','D_lowest']],four_distinct_arm_heights=True,closed_arm_end_faces=True,no_geographic_orientation_claim=True,pool_outer_radius_mm=POOL_R,pool_inner_radius_mm=POOL_INNER_R,pool_floor_top_mm=FLOOR_Z,pool_rim_top_mm=RIM_TOP,complete_annular_air_channel=True,lower_steps=[dict(radius=r,bottom=z,top=top) for r,z,top in STEPS],upper_pedestal=dict(radius=29.,bottom=31.3,top=41.4),total_concentric_levels=7,upper_pedestal_taller_than_each_small_step=True,nozzles=NOZZLES,nozzle_count_approximate=37,nozzle_geometry='solid thickened radial rods; hollow bore and tiny fittings omitted',nozzle_diameter_mm=1.1,hemispherical_nozzle_envelope=True,all_materials_opaque=True,added_print_base=False,unseen_basin_floor_depth_approximate=True,uncertain=['all absolute dimensions and ratio-derived heights/lengths','four-arm exact compass orientation and angles','precise step heights and radial widths','top drum hidden interior depth','nozzle count, thickness, elevation, angles and fittings','basin unseen bottom and wall cross-section','photographic wet/dry color variation'],omitted=['dynamic water jets and water surface','hidden plumbing, pumps, lighting and deep drum cavity','plaque and sign stand','whole plaza, restaurants, trees, vehicles and people','raw source photos, PDFs, crops and HTML'],no_actual_print=True,support_free_certified=False)
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
