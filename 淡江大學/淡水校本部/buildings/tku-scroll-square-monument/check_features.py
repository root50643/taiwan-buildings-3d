#!/usr/bin/env python3
"""Scroll Square Monument / 書卷廣場竹卷雕塑 raw-STL local occupancy, thickness and overhang diagnostics.
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
assert features['slug']=='tku-scroll-square-monument' and len(features['solid_sheet_samples'])==36
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


from shapely.geometry import LineString
from shapely.ops import nearest_points
import math
BASE=features['base_top_mm'];specs=features['sheet_parameters']
# Test all four sheets at multiple plan positions and height fractions.
for i,sample in enumerate(features['solid_sheet_samples']):
 p=sample['center'];n=sample['normal'];label=f"{sample['sheet']}_t{sample['t']}_h{sample['height_fraction']}"
 ray=ray_intervals(p,n);at_center=[ab for ab in ray['all_solid_intervals_relative_to_center_mm'] if ab[0]<0<ab[1]]
 thickness=at_center[0][1]-at_center[0][0] if len(at_center)==1 else None
 rays.append(dict(feature=label,center_mm=p,nominal_normal_mm=sample['nominal_normal_thickness_mm'],center_inside_solid=len(at_center)==1,thickness_mm=thickness,below_0_8mm=bool(thickness is not None and thickness<.8),**ray))
 T.append(tangent_section(label+'_normal_transverse_slice',p,n))
# Finite full-height central cylinder: no fabricated central core or top cover.
central=m^md.Manifold.cylinder(110.,6.,6.,64).translate((0,0,BASE+.2))
T.append(audit_crop('central_space_no_core_or_cap',central,[BASE+.3,BASE+30.,BASE+65.,BASE+105.],'air',dict(radius_mm=6.,z_range_mm=[BASE+.2,BASE+110.2])))
# Adjacent leaf gaps determined from PREDECLARED design centreline curves, then
# checked against the ACTUAL STL, not inferred by analytic construction alone.
lines=[]
for s in specs:
 theta=np.deg2rad(np.linspace(0,s['span'],97));b=math.radians(s['rotation']);R=np.array([[math.cos(b),-math.sin(b)],[math.sin(b),math.cos(b)]])
 xy=np.column_stack([s['radius']*np.cos(theta)-s['offset'],s['radius']*np.sin(theta)])@R.T;lines.append(LineString(xy))
gap_records=[]
for i in range(4):
 j=(i+1)%4;a,b=nearest_points(lines[i],lines[j]);pa=np.array(a.coords[0]);pb=np.array(b.coords[0]);center=(pa+pb)/2;dist=float(np.linalg.norm(pa-pb));clearance=dist-(specs[i]['thickness']+specs[j]['thickness'])/2
 assert clearance>1.,(i,clearance)
 radius=min(.45,clearance/4);height=min(specs[i]['low'],specs[j]['low'])-.6;z=BASE+.3
 crop=m^md.Manifold.cylinder(height,radius,radius,32).translate((*center,z));label=f"adjacent_sheet_gap_{specs[i]['id']}_{specs[j]['id']}"
 T.append(audit_crop(label,crop,[z+.1,z+height/2,z+height-.1],'air',dict(center_xy_mm=center.tolist(),radius_mm=radius,z_range_mm=[z,z+height]),note='Finite column between predeclared centreline nearest points, wholly through both adjacent sheets lower height range.'))
 gap_records.append(dict(feature=label,estimated_centerline_distance_mm=dist,estimated_clearance_mm=clearance,center_xy_mm=center.tolist(),checked_air_radius_mm=radius))
# Independent sub-base/stair/drum samples ensure the intended support hierarchy.
for i,st in enumerate(features['narrow_steps']):
 r=st['radius_mm']-2.;z=st['bottom_mm'];T.append(local(f"narrow_step_{i+1}_solid",[r-.6,-.6,z+.1],[1.2,1.2,1.4],[z+.2,z+.7,z+1.4]))
T.append(local('broad_outer_platform_solid',[82.,-1.,.1],[2.,2.,1.5],[.2,.8,1.5]))
T.append(local('sloped_high_drum_solid',[35.,-1.,11.],[2.,2.,8.],[11.2,15.,18.8]))
T.append(local('thin_top_lip_solid',[34.,-1.,19.35],[2.,2.,.7],[19.4,19.7,20.]))
# Global horizontal levels where every leaf exists must contain FOUR disconnected
# sheet components; the base below is intentionally one connected printable shell.
separation=[]
for z in [BASE+.4,BASE+3.,BASE+6.]:
 polygons=[];g=GeometryCollection()
 for contour in m.slice(z).to_polygons():
  poly=Polygon(contour);g=g.symmetric_difference(poly)
 components=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
 separation.append(dict(z_mm=z,components=len(components),valid=g.is_valid,areas_mm2=[x.area for x in components]));assert len(components)==4 and g.is_valid
centers=mesh.triangles_center;mask=(mesh.face_normals[:,2]<-np.sqrt(.5))&(centers[:,2]>.0001)
solid=[r for t in T if t['expected']=='solid' for r in t['rows']];air=[r for t in T if t['expected']=='air' for r in t['rows']]
end_hashes={n:sha(A/n) for n in INPUTS}
report=dict(stl_sha256=start_hashes['model.stl'],input_hashes=start_hashes,input_files_unchanged_during_test=start_hashes==end_hashes,method='Raw STL exact-equality welding only; finite-volume actual-mesh air/solid intersections, true even-odd local slices retaining every component, -0.4mm erosion in planes INCLUDING normal thickness, outside-origin actual-mesh normal rays. No repairs, contour rounding or thin exemptions.',tests=T,solid_samples=len(solid),air_samples=len(air),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in T for r in t['rows']),air_volume_mismatches=sum(not t['air_volume_is_zero'] for t in T if t['expected']=='air'),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solid),failed_0_8mm_components=sum(r['failed_0_8mm'] for r in solid),normal_thickness_ray_checks=rays,normal_ray_occupancy_mismatches=sum(not r['center_inside_solid'] or not r['even_hit_count'] for r in rays),axis_thickness_below_0_8mm_samples=sum(r['below_0_8mm'] for r in rays),four_leaf_separation_slices=separation,adjacent_gap_checks=gap_records,downward_faces_over_45deg_above_base=int(mask.sum()),downward_area_mm2=float(mesh.area_faces[mask].sum()),overhang_by_material={p['id']:dict(triangles=int((mask&(materials==i)).sum()),area_mm2=float(mesh.area_faces[mask&(materials==i)].sum())) for i,p in enumerate(palette)},thin_warning='Four tall free-edged white sheets are model-strengthened to nominal 1.35mm normal thickness. Upper tips still create arbitrarily narrow horizontal slices; all global/local warnings retained. Thin drum lip has undercut faces, and high unsupported blades may wobble, break or need supports. Stone and top-edge details simplified; not measured original thickness.',actual_print_tested=False,support_free_certified=False,limitations='Selected finite samples only, not full-surface minimum-thickness, printer slicing, bridge-span, strength, support-removal or physical-print certification.')
(A/'qa/local-features.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['tests','normal_thickness_ray_checks']},ensure_ascii=False,indent=2),flush=True)
assert report['input_files_unchanged_during_test'];assert report['occupancy_mismatches']==0 and report['air_volume_mismatches']==0
assert all(r['valid'] for t in T for r in t['rows']);assert report['normal_ray_occupancy_mismatches']==0
# Thickness/erosion/overhang diagnostics never suppressed or turned into guarantees.
