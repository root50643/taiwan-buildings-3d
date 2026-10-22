"""Bounded raw-STL checks for NTOU Dream Fountain2018 visible exterior.
Exact coordinate welding only. No mesh repairs, contour rounding, island deletion
or thin-feature exemptions. These samples are not a global normal-thickness proof.
"""
from pathlib import Path
import hashlib,json
import numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection,Point
from qa_model import raw_read
A=Path(__file__).resolve().parent
raw_hash=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest()
_,v,f=raw_read(A/'model.stl')
mesh=trimesh.Trimesh(v,f,process=False)
assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
m=md.Manifold(md.Mesh(np.asarray(v,dtype=np.float32),np.asarray(f,dtype=np.uint32)))
assert m.status().name=='NoError'
features=json.loads((A/'qa/design-features.json').read_text())
fm=json.loads((A/'mesh.json').read_text())
assert np.array_equal(np.asarray(fm['vertices'])[np.asarray(fm['faces'])],v[f]),'Material manifest geometry mismatch'
materials=np.asarray(fm['face_materials']);palette=json.loads((A/'palette.json').read_text())['materials']
assert len(materials)==len(f)

def audit_crop(name,crop,levels,expected='solid',note='',description=None,reference_xy=None):
 rows=[]
 for z in levels:
  geom=GeometryCollection();invalid=0
  for contour in crop.slice(float(z)).to_polygons():
   if len(contour)<3:continue
   p=Polygon(contour);invalid+=not p.is_valid;geom=geom.symmetric_difference(p)
  polys=list(geom.geoms) if geom.geom_type=='MultiPolygon' else ([] if geom.is_empty else [geom])
  eroded=[p.buffer(-.4,quad_segs=16) for p in polys]
  row=dict(plane_mm=float(z),components=len(polys),valid=bool(geom.is_valid and invalid==0),area_mm2=float(geom.area),component_areas_mm2=[float(p.area) for p in polys],component_bounds_mm=[list(p.bounds) for p in polys],failed_0_8mm=sum(p.is_empty for p in eroded),eroded_areas_mm2=[float(p.area) for p in eroded],expected_occupancy_met=(not polys if expected=='air' else bool(polys)))
  if reference_xy is not None:
   indices=[i for i,p in enumerate(polys) if p.covers(Point(*reference_xy))]
   row.update(target_axis_component_count=len(indices),target_axis_component_failed_0_8mm=sum(eroded[i].is_empty for i in indices),off_axis_component_count=len(polys)-len(indices))
  rows.append(row)
 volume=float(crop.volume())
 return dict(feature=name,description=description or {},expected=expected,crop_intersection_volume_mm3=volume,air_volume_is_zero=bool(volume==0) if expected=='air' else None,note=note,rows=rows)

def local(name,origin,size,levels,expected='solid',note='',reference_xy=None):
 crop=m ^ md.Manifold.cube(size).translate(origin)
 return audit_crop(name,crop,levels,expected,note,dict(shape='axis-aligned box',origin_mm=origin,size_mm=size),reference_xy)

tests=[];rays=[]
assert features['four_distinct_arm_heights'] and features['total_concentric_levels']==7
assert len(set(a['center_z'] for a in features['arms']))==4
# All-angle annulus intersection: complete circular channel, not a few sampled holes.
ring=(md.Manifold.cylinder(11.6,77.5,77.5,128)-md.Manifold.cylinder(11.8,57.5,57.5,128).translate((0,0,-.1))).translate((0,0,3.2))
tests.append(audit_crop('full_360_degree_annular_channel',m^ring,[3.3,6,10,14.7],'air','Whole ring volume must be zero, not only chosen radial samples.',dict(inner_radius_mm=57.5,outer_radius_mm=77.5,bottom=3.2,top=14.8)))
for angle in range(0,360,45):
 a=np.deg2rad(angle);x,y=67*np.cos(a),67*np.sin(a)
 tests.append(local(f'annular_channel_sector_{angle}',[x-2,y-2,3.2],[4,4,11.6],[3.4,8,14.6],'air'))
tests.append(local('basin_unseen_approximate_floor',[-3,-68,.1],[6,6,2.8],[.2,1.5,2.8]))
tests.append(local('closed_pool_rim',[81,-2,3.1],[6,4,11.8],[3.2,9,14.8]))
for i,step in enumerate(features['lower_steps']):
 r=step['radius'];z=step['top'];tests.append(local(f'2018_step_{i+1}',[r-1.8,-1,z-.7],[1.3,2,.65],[z-.65,z-.4,z-.1],note='Visible outer tread component; crop erosion warning retained, not a full-step thickness claim.'))
tests.append(local('tall_seventh_pedestal',[24,-2,32],[4,4,9],[32.1,36,40.9]))
tests.append(local('central_vertical_shaft',[-4,-4,44],[8,8,80],[45,83,122]))
tests.append(local('top_drum_overhang',[20,-2,126.1],[3,4,17.8],[126.2,135,143.8]))
for arm in features['arms']:
 d=np.array(arm['direction'],float);z=arm['center_z'];axis=0 if d[0] else 1
 mid=d*36;mid[2]=z
 tests.append(local(arm['label']+'_body',list(mid-[2,2,3]),[4,4,6],[z-2.9,z,z+2.9]))
 end=d*(17+arm['outer_length']);end[2]=z
 origin=end-d*.5-[.2,.2,.2]
 tests.append(local(arm['label']+'_closed_end_near_center',origin.tolist(),[.4,.4,.4],[z-.15,z,z+.15],note='Solid immediately inside closed end face, not an open pipe.'))
 # Just outside each planar cap remains air.
 outside=end+d*1.2
 tests.append(local(arm['label']+'_outside_end_air',(outside-[.2,.2,.2]).tolist(),[.4,.4,.4],[z-.15,z,z+.15],'air'))
# Each tube checked in its own axis-normal plane; retain all fragments with no exemptions.
for i,nozzle in enumerate(features['nozzles']):
 start=np.array(nozzle['start']);end=np.array(nozzle['end']);d=(end-start)/np.linalg.norm(end-start)
 q=np.array([0.,0.,1.]) if abs(d[2])<.9 else np.array([1.,0.,0.]);xx=np.cross(q,d);xx/=np.linalg.norm(xx);yy=np.cross(d,xx);R=np.vstack([xx,yy,d]);T=np.column_stack([R,-R@start]);oriented=m.transform(T)
 crop=oriented^md.Manifold.cube((2.6,2.6,7.5)).translate((-1.3,-1.3,14.4))
 tests.append(audit_crop(f'nozzle_{i+1}_normal_sections',crop,[15.,18.,21.8],note='Sections normal to this actual slanted tube;1.1mm model thickness is a disclosed approximation.',description=dict(world_axis=d.tolist(),world_origin=start.tolist(),local_crop_min=[-1.3,-1.3,14.4],local_crop_size=[2.6,2.6,7.5]),reference_xy=[0,0]))
 air=oriented^md.Manifold.cube((.35,.35,3.5)).translate((.9,-.175,15))
 tests.append(audit_crop(f'nozzle_{i+1}_adjacent_air',air,[15.1,16.7,18.4],'air','Air beside tube verifies tube bundle is not a solid hemisphere.',dict(local_min=[.9,-.175,15],local_size=[.35,.35,3.5],world_axis=d.tolist())))
 # Ray perpendicular to tube, classify interval through actual tube-axis location.
 origin=start+d*18-xx*3;locations,_,_=mesh.ray.intersects_location([origin],[xx],multiple_hits=True);vals=np.sort((locations-origin)@xx)
 assert len(vals)%2==0,(i,vals)
 intervals=[[float(a),float(b)] for a,b in zip(vals[::2],vals[1::2])];hits=[ab for ab in intervals if ab[0]<3<ab[1]];assert len(hits)==1,(i,intervals)
 th=hits[0][1]-hits[0][0];rays.append(dict(feature=f'nozzle_{i+1}',ray_origin_mm=origin.tolist(),ray_direction=xx.tolist(),all_solid_distance_intervals_mm=intervals,selected_interval_mm=hits[0],measured_axis_thickness_mm=th,nominal_axis_thickness_mm=1.1,within_tolerance=abs(th-1.1)<.008,below_0_8mm=th<.8))
centers=mesh.triangles_center;mask=(mesh.face_normals[:,2]<-np.sqrt(.5))&(centers[:,2]>.0001)
by_material={p['id']:dict(triangles=int((mask&(materials==i)).sum()),area_mm2=float(mesh.area_faces[mask&(materials==i)].sum())) for i,p in enumerate(palette)}
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=raw_hash,method='Raw STL exact welding; real mesh bounded intersections and all-angle annular void; even-odd sections and -0.4mm erosion;37 rod-normal crops and actual-mesh perpendicular rays; no repairs or thin exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),air_volume_mismatches=sum(not t['air_volume_is_zero'] for t in tests if t['expected']=='air'),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),failed_0_8mm_components=sum(r['failed_0_8mm'] for r in solidrows),axis_ray_checks=rays,axis_thickness_below_0_8mm_samples=sum(q['below_0_8mm'] for q in rays),downward_faces_over_45deg_above_base=int(mask.sum()),downward_area_mm2=float(mesh.area_faces[mask].sum()),overhang_height_threshold_mm=.0001,overhang_by_material=by_material,thin_warning='Nozzle tips retain sub0.8mm grazing-layer warnings;1.1mm thickening does not certify printability. Small cropped fragments are counted without exemptions. Four long horizontal arms and drum undercut need support planning.',actual_print_tested=False,support_free_certified=False,limitations='No global normal-minimum thickness, bridge-span, slicer, strength, support-removal or physical-print certification. Ring void and3D nozzle air verified only in explicitly reported bounded volumes.2018 source visible exterior, not measured2026 condition.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['tests','axis_ray_checks']},indent=2))
assert report['occupancy_mismatches']==0 and report['air_volume_mismatches']==0
assert all(r['within_tolerance'] for r in rays)
assert all(r['valid'] for t in tests for r in t['rows'])
