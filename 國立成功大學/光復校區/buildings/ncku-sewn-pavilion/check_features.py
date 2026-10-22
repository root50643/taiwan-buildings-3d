#!/usr/bin/env python3
"""Sewn Pavilion raw-STL local occupancy, thickness and overhang diagnostics.
No repairs, normal fixes, contour rounding or thin-part exemptions. Local samples
are not a global minimum thickness/strength or physical-print certificate.
"""
from pathlib import Path
import hashlib,json,collections
import numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection
from qa_model import raw_read
A=Path(__file__).resolve().parent
INPUTS=['model.stl','mesh.json','palette.json','qa/design-features.json']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
start_hashes={n:sha(A/n) for n in INPUTS}
_,v,f=raw_read(A/'model.stl');mesh=trimesh.Trimesh(v,f,process=False)
m=md.Manifold(md.Mesh(np.asarray(v,dtype=np.float32),np.asarray(f,dtype=np.uint32)))
assert m.status().name=='NoError' and mesh.is_watertight,{'message':'Raw topology gate failed; no repairs allowed here.','stl_sha256':start_hashes['model.stl'],'manifold_status':m.status().name,'raw_exact_weld_watertight':bool(mesh.is_watertight)}
features=json.loads((A/'qa/design-features.json').read_text());fm=json.loads((A/'mesh.json').read_text());materials=np.asarray(fm['face_materials']);palette=json.loads((A/'palette.json').read_text())['materials']
assert np.array_equal(np.asarray(fm['vertices'])[np.asarray(fm['faces'])],v[f]),'Mesh/STL input mismatch, possibly a build in progress.'
assert features['slug']=='ncku-sewn-pavilion' and len(features['solid_band_samples'])==18
assert len(features['central_frame_samples'])>=3
assert {(s['leaf'],s['band']) for s in features['solid_band_samples']}=={(l,b) for l in 'ABC' for b in range(6)}
T=[];rays=[];hole_rays=[]

def audit_crop(name,crop,levels,expected='solid',description=None,note=''):
 rows=[]
 for z in levels:
  geom=GeometryCollection();invalid=0
  for contour in crop.slice(float(z)).to_polygons():
   if len(contour)<3:continue
   poly=Polygon(contour);invalid+=not poly.is_valid;geom=geom.symmetric_difference(poly)
  if geom.geom_type=='MultiPolygon':polys=list(geom.geoms)
  elif geom.is_empty:polys=[]
  else:
   assert geom.geom_type=='Polygon',(name,geom.geom_type)
   polys=[geom]
  eroded=[p.buffer(-.4,quad_segs=16) for p in polys]
  rows.append(dict(plane_mm=float(z),components=len(polys),valid=bool(geom.is_valid and not invalid),area_mm2=float(geom.area),component_areas_mm2=[float(p.area) for p in polys],component_bounds_mm=[list(p.bounds) for p in polys],failed_0_8mm=sum(p.is_empty for p in eroded),expected_occupancy_met=not polys if expected=='air' else bool(polys)))
 vol=float(crop.volume())
 return dict(feature=name,description=description,expected=expected,crop_intersection_volume_mm3=vol,air_volume_is_zero=bool(vol==0) if expected=='air' else None,note=note,rows=rows)

def local(name,origin,size,levels,expected='solid',note=''):
 return audit_crop(name,m^md.Manifold.cube(size).translate(origin),levels,expected,dict(origin_mm=origin,size_mm=size),note)

def frame(n):
 n=np.asarray(n,float);n/=np.linalg.norm(n)
 q=np.eye(3)[np.argmin(abs(n))];tangent=np.cross(n,q);tangent/=np.linalg.norm(tangent);bitangent=np.cross(tangent,n)
 return n,bitangent,tangent

def tangent_section(name,p,n):
 # Section plane INCLUDES panel-normal thickness: local X=normal, Z=tangent.
 # Slicing parallel to a sheet would conceal the thin normal dimension.
 p=np.asarray(p,float);n,bi,tan=frame(n);R=np.vstack([n,bi,tan])
 transformed=m.transform(np.column_stack([R,-R@p]));crop=transformed^md.Manifold.cube((2.4,2.4,1.2)).translate((-1.2,-1.2,-.6))
 return audit_crop(name,crop,[-.4,0.,.4],description=dict(world_center_mm=p.tolist(),normal=n.tolist(),slice_axis_tangent=tan.tolist(),world_to_local_rotation_rows=R.tolist(),local_origin_mm=[-1.2,-1.2,-.6],local_size_mm=[2.4,2.4,1.2]),note='All positive slice components retained. Plane includes normal thickness; finite crop is diagnostic, not a minimum-thickness certificate.')

# Rays start outside the complete model, so alternating crossings truly delimit solids.
def ray_intervals(p,n):
 p=np.asarray(p,float);n=np.asarray(n,float);n/=np.linalg.norm(n)
 far=float(np.linalg.norm(mesh.extents)+np.linalg.norm(p-mesh.centroid)+20.)
 origin=p-far*n;locations,_,_=mesh.ray.intersects_location([origin],[n],multiple_hits=True)
 vals=np.sort((locations-origin)@n)
 # Trimesh already coalesces identical hit locations. Never round or merge near hits.
 intervals=[[float(a-far),float(b-far)] for a,b in zip(vals[::2],vals[1::2])]
 return dict(origin_mm=origin.tolist(),direction=n.tolist(),center_ray_distance_mm=far,hit_count=len(vals),even_hit_count=bool(len(vals)%2==0),all_solid_intervals_relative_to_center_mm=intervals)

feet=np.asarray(features['feet_centers_mm'])
for i,p in enumerate(feet):
 T.append(local(f'shared_foot_{i}_solid_core',[float(p[0]-.7),float(p[1]-.7),.1],[1.4,1.4,4.8],[.2,2.5,4.8]))
for i in range(3):
 p=(feet[i]+feet[(i+1)%3])/2
 T.append(local(f'leaf_{"ABC"[i]}_open_arch_below_chord_midpoint',[float(p[0]-3),float(p[1]-3),10.],[6.,6.,35.],[10.1,27.5,44.9],'air'))
T.append(local('central_interior_below_frame',[-2.,-2.,10.],[4.,4.,55.],[10.1,35.,64.9],'air'))
T.append(local('small_central_triangle_true_opening',[-.5,-.5,70.],[1.,1.,23.],[70.1,82.5,92.9],'air',note='Finite prism through the actual central frame height, not merely an empty point above/below the model.'))

# Test every recorded intended perforation, including occlusions rather than silently dropping them.
for h in features['perforation_hole_samples']:
 ray=ray_intervals(h['center'],h['normal']);overlap=[ab for ab in ray['all_solid_intervals_relative_to_center_mm'] if max(ab[0],-1.5)<min(ab[1],1.5)]
 hole_rays.append(dict(feature=f"leaf_{h['leaf']}_band_{h['band']}_hole_{h['index']}",leaf=h['leaf'],band=h['band'],index=h['index'],center_mm=h['center'],finite_air_segment_mm=[-1.5,1.5],open_air_segment=bool(ray['even_hit_count'] and not overlap),intersecting_intervals_mm=overlap,**ray))
 # Predeclared middle hole for every indexed band; not selected after checking.
 if h['index']==6:
  p=np.asarray(h['center']);n,bi,tan=frame(h['normal']);R=np.vstack([bi,tan,n]);oriented=m.transform(np.column_stack([R,-R@p]));cylinder=md.Manifold.cylinder(3.,.10,.10,16).translate((0,0,-1.5));crop=oriented^cylinder
  T.append(audit_crop(f"leaf_{h['leaf']}_band_{h['band']}_hole_6_finite_air_column",crop,[-1.4,0.,1.4],'air',dict(world_center_mm=p.tolist(),normal=n.tolist(),radius_mm=.10,length_mm=3.,sample_index=6),note='Preselected hole 6 of every band, tested as finite 0.20mm diameter column normal to the curved panel.'))

for sample in features['solid_band_samples']:
 p=sample['center'];n=sample['normal'];label=f"leaf_{sample['leaf']}_band_{sample['band']}_solid_normal"
 ray=ray_intervals(p,n);at_center=[ab for ab in ray['all_solid_intervals_relative_to_center_mm'] if ab[0]<0<ab[1]]
 thickness=at_center[0][1]-at_center[0][0] if len(at_center)==1 else None
 rays.append(dict(feature=label,kind='band',leaf=sample['leaf'],band=sample['band'],center_mm=p,nominal_normal_mm=sample['nominal_thickness_mm'],center_inside_solid=len(at_center)==1,thickness_mm=thickness,below_0_8mm=bool(thickness is not None and thickness<.8),**ray))
 T.append(tangent_section(label+'_transverse_slice',p,n))
for i,sample in enumerate(features['central_frame_samples']):
 p=sample['center'];n=sample['normal'];label=f"central_threeway_frame_{sample['leaf']}_sample_{i}"
 ray=ray_intervals(p,n);at_center=[ab for ab in ray['all_solid_intervals_relative_to_center_mm'] if ab[0]<0<ab[1]]
 thickness=at_center[0][1]-at_center[0][0] if len(at_center)==1 else None
 rays.append(dict(feature=label,kind='central_frame',leaf=sample['leaf'],center_mm=p,nominal_vertical_mm=sample['vertical_thickness_mm'],nominal_normal_mm=sample.get('nominal_normal_thickness_mm'),approximate_normal_projection_mm=float(sample['vertical_thickness_mm']*abs(np.asarray(n)[2]/np.linalg.norm(n))),center_inside_solid=len(at_center)==1,thickness_mm=thickness,below_0_8mm=bool(thickness is not None and thickness<.8),**ray))
 T.append(tangent_section(label+'_transverse_slice',p,n))

centers=mesh.triangles_center;mask=(mesh.face_normals[:,2]<-np.sqrt(.5))&(centers[:,2]>.0001)
solid=[r for t in T if t['expected']=='solid' for r in t['rows']];air=[r for t in T if t['expected']=='air' for r in t['rows']]
coverage=[]
for leaf in 'ABC':
 for band in range(6):
  records=[r for r in hole_rays if r['leaf']==leaf and r['band']==band]
  coverage.append(dict(leaf=leaf,band=band,tested_perforations=len(records),open_finite_normal_air_segments=sum(r['open_air_segment'] for r in records),at_least_one_open=any(r['open_air_segment'] for r in records)))
finite_column_count=sum(t['feature'].endswith('_hole_6_finite_air_column') for t in T)
assert finite_column_count==18
end_hashes={n:sha(A/n) for n in INPUTS}
report=dict(stl_sha256=start_hashes['model.stl'],input_hashes=start_hashes,input_files_unchanged_during_test=start_hashes==end_hashes,method='Raw STL exact-equality welding only; actual-mesh finite-volume occupancy and true even-odd local slices; all components subjected to -0.4mm erosion in planes INCLUDING panel-normal thickness; outside-origin actual-mesh normal rays. No repair, rounding or thin exemptions.',tests=T,solid_samples=len(solid),air_samples=len(air),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in T for r in t['rows']),air_volume_mismatches=sum(not t['air_volume_is_zero'] for t in T if t['expected']=='air'),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solid),failed_0_8mm_components=sum(r['failed_0_8mm'] for r in solid),normal_thickness_ray_checks=rays,normal_ray_occupancy_mismatches=sum(not r['center_inside_solid'] or not r['even_hit_count'] for r in rays),axis_thickness_below_0_8mm_samples=sum(r['below_0_8mm'] for r in rays),perforation_ray_checks=hole_rays,perforation_air_ray_count=len(hole_rays),perforation_air_ray_occluded_or_invalid=sum(not r['open_air_segment'] for r in hole_rays),per_leaf_band_perforation_coverage=coverage,all_18_indexed_bands_have_open_perforation=all(r['at_least_one_open'] for r in coverage),preselected_finite_perforation_columns=finite_column_count,downward_faces_over_45deg_above_base=int(mask.sum()),downward_area_mm2=float(mesh.area_faces[mask].sum()),overhang_by_material={p['id']:dict(triangles=int((mask&(materials==i)).sum()),area_mm2=float(mesh.area_faces[mask&(materials==i)].sum())) for i,p in enumerate(palette)},thin_warning='Curved perforated bands are nominal 0.95mm normal thickness. Central frame is model-strengthened toward 0.95mm normal thickness by varying vertical thickness with the local surface normal; the steep footward limit and Boolean overlaps mean actual raw-STL ray measurements govern. This is not measured original construction thickness. Perforations, thin seams and foot tabs remain fragile; arches, flared edges and central frame need support planning. All sampled erosion/ray warnings retained without exemptions.',actual_print_tested=False,support_free_certified=False,limitations='Finite chosen regions only: not a full-surface minimum-thickness, bridge-span, strength, slicer, support-removal or physical-print certificate. Individual hole pattern is approximate, not source-measured.')
(A/'qa/local-features.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['tests','normal_thickness_ray_checks','perforation_ray_checks','per_leaf_band_perforation_coverage']},ensure_ascii=False,indent=2),flush=True)
assert report['input_files_unchanged_during_test'],'Model changed while being checked; rerun on a stable final build.'
assert report['occupancy_mismatches']==0 and report['air_volume_mismatches']==0,[(t['feature'],t['expected']) for t in T if any(not r['expected_occupancy_met'] for r in t['rows']) or (t['expected']=='air' and not t['air_volume_is_zero'])]
assert all(r['valid'] for t in T for r in t['rows'])
assert report['normal_ray_occupancy_mismatches']==0
assert report['all_18_indexed_bands_have_open_perforation']
# Thin erosion/ray warnings and any additional recorded perforation occlusions are
# diagnostics, never deleted, waived or converted into unsupported printability claims.
