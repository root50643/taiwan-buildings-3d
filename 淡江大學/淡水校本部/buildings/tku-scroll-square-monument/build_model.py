"""Tamkang University Scroll Square Monument / 書卷廣場竹卷雕塑.
Four separate curved white plates plus OLD complete circular stair pedestal.
Undated official-photo interpretation, not a survey or 2026 landscape record.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[('white_curved_scroll_plates','#ECEDE9',255),('dark_stone_step_risers','#666965',255),('stone_tread_and_outer_platform','#A3A399',255),('sloped_stone_drum','#85877F',255),('thin_stone_drum_lip','#B4B4AA',255)]
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
def cylinder(z,h,r1,r2=None):return Manifold.cylinder(h,r1,r1 if r2 is None else r2,256).translate((0,0,z))
# One broad low outer platform, then FIVE narrow treads, not six equal rings.
# Positive overlaps create a single coherent base, without filling spaces above it.
add(cylinder(0,1.8,90),2,'outer_broad_low_circular_platform')
steps=[]
for i,r in enumerate([76.,70.,64.,58.,52.]):
 z=1.8+1.8*i;add(cylinder(z-.15,1.6,r),1,f'narrow_circular_step_{i+1}_riser')
 add(cylinder(z+1.35,.45,r),2,f'narrow_circular_step_{i+1}_tread')
 steps.append(dict(index=i+1,radius_mm=r,bottom_mm=z,top_mm=z+1.8))
add(cylinder(10.65,8.8,43.,38.7),3,'high_outward_sloping_stone_drum')
add(cylinder(19.3,.85,39.3),4,'thin_projecting_drum_top_lip')
BASE_Z=20.15
# Four independent off-centre circular-arc sections. Each vertical sheet is
# extruded to its own sloping free upper edge, NOT twisted or a solid sector.
# Independent arc centres/angles, spacing and all model dimensions are estimates.
# Arc centres lie slightly inward of a common display origin; this gives the
# nested-page impression seen in high oblique photos without any hidden bridge.
SPECS=[dict(id='A_highest',rotation=0.,radius=23.,offset=8.,span=96.,high=108.,low=80.,thickness=1.35),dict(id='B_second',rotation=100.,radius=24.4,offset=8.6,span=92.,high=66.,low=39.,thickness=1.35),dict(id='C_low',rotation=195.,radius=25.8,offset=8.0,span=88.,high=43.,low=14.,thickness=1.35),dict(id='D_lowest',rotation=285.,radius=27.,offset=8.,span=90.,high=31.5,low=7.5,thickness=1.35)]
samples=[];gaps=[]
def param(s,t):
 a=math.radians(s['span']*t);b=math.radians(s['rotation']);R=np.array([[math.cos(b),-math.sin(b)],[math.sin(b),math.cos(b)]])
 n=R@np.array([math.cos(a),math.sin(a)]);p=R@np.array([s['radius']*math.cos(a)-s['offset'],s['radius']*math.sin(a)])
 return p,n,s['high']+(s['low']-s['high'])*t
for s in SPECS:
 N=96;verts=[];faces=[]
 for t in np.linspace(0,1,N+1):
  p,n,h=param(s,float(t))
  for side,z in [(-1,BASE_Z-.25),(1,BASE_Z-.25),(-1,BASE_Z+h),(1,BASE_Z+h)]:verts.append([*(p+side*n*s['thickness']/2),z])
 for i in range(N):
  a=4*i;b=a+4
  # bottom, outside, top and inside quads, triangulated consistently.
  for q in [(a,b,b+1,a+1),(a+1,b+1,b+3,a+3),(a+3,b+3,b+2,a+2),(a+2,b+2,b,a)]:faces.extend([(q[0],q[1],q[2]),(q[0],q[2],q[3])])
 faces.extend([(0,1,3),(0,3,2),(4*N,4*N+2,4*N+3),(4*N,4*N+3,4*N+1)])
 tm=trimesh.Trimesh(verts,faces,process=False)
 if tm.volume<0:tm.invert()
 assert tm.is_watertight and tm.is_winding_consistent
 sheet=Manifold(Mesh(np.asarray(tm.vertices,dtype=np.float32),np.asarray(tm.faces,dtype=np.uint32)));add(sheet,0,'independent_open_top_curved_sheet_'+s['id'])
 for t in [.15,.5,.85]:
  p,n,h=param(s,t)
  for frac in [.12,.55,.9]:samples.append(dict(sheet=s['id'],t=t,height_fraction=frac,center=[*p,float(BASE_Z+h*frac)],normal=[*n,0.],nominal_normal_thickness_mm=s['thickness']))
 p,n,h=param(s,0);gaps.append(dict(sheet=s['id'],center=[*(p-n*2.0),BASE_Z+3.],radius_mm=.5,z_range_mm=[BASE_Z+.3,BASE_Z+6.]))
FEATURES=dict(name='書卷廣場竹卷雕塑 / Scroll Square Monument',school='淡江大學',campus='淡水校本部',slug='tku-scroll-square-monument',target_path='淡江大學/淡水校本部/buildings/tku-scroll-square-monument',completed_year=1986,designer='林貴榮',source_capture_dates='unknown; URL storage paths are not capture dates',selected_version='undated official photographs with full old circular stair pedestal; not 2025 new landscape and not certified 2026 condition',landscape_improvement_completion='2025-10-30; separate project not sculpture construction',estimated_not_surveyed=True,display_dimensions_not_survey_scale=True,four_separate_vertical_curved_sheets=True,unequal_sloping_free_upper_edges=True,no_top_cover=True,no_center_column=True,no_sheet_connecting_bridges=True,base_top_mm=BASE_Z,sheet_parameters=SPECS,solid_sheet_samples=samples,inner_edge_air_columns=gaps,central_air_cylinder_radius_mm=6.,outer_platform_radius_mm=90.,outer_platform_height_mm=1.8,narrow_steps=steps,narrow_step_count=5,high_sloped_drum=dict(bottom_mm=10.65,top_mm=19.45,bottom_radius_mm=43.,top_radius_mm=38.7),thin_top_lip=dict(bottom_mm=19.3,top_mm=20.15,radius_mm=39.3),all_materials_opaque=True,no_actual_print=True,support_free_certified=False,uncertain=['all absolute dimensions and proportions, no reliable physical scale','independent arc centres, curvatures and angular spans','sheet height functions, spacing and normal thickness','step heights, tread widths, drum slope and lip thickness','simplified unpatterned stone surfaces and white paint','original photo capture dates and exact historical version date'],omitted=['2025 surrounding landscape and paths','surrounding plaza, grass, plant beds, shrubs and trees','adjacent buildings, people, signs and event equipment','hidden foundations, reinforcement and internal fixings','photo weathering and individual masonry joints','private reference photographs, crops, HTML and PDFs'])
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
