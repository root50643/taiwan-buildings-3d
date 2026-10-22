"""Bounded raw-STL checks for NTU Xitou Ginkgo Bridge2017 complete exterior.
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

tests=[];rays=[];fan_counts=[]
P=250/3
KNOTS=[(-150.,29.),(-78.,45.5),(0.,29.),(78.,45.5),(150.,29.)]
def profile(x):
 for (a,za),(b,zb) in zip(KNOTS,KNOTS[1:]):
  if x<=b:
   t=max(0,min(1,(x-a)/(b-a)));return za+(zb-za)*(3*t*t-2*t*t*t)
 return 29.
assert features['official_spans_m']==[8,20,8] and features['official_main_bridge_length_m']==36
assert features['total_fans']==4 and features['primary_ribs_per_fan']==4
assert len([p for p in features['parts'] if p['name'].startswith('primary_fan_')])==16
assert features['not_2014_40m_angular_scheme']
def ray(name,origin,direction,axis,inside,nominal,tolerance=.003):
 loc,_,_=mesh.ray.intersects_location([origin],[direction],multiple_hits=True);vals=np.sort(loc[:,axis]);assert len(vals)%2==0,(name,vals)
 intervals=[[float(a),float(b)] for a,b in zip(vals[::2],vals[1::2])];found=[ab for ab in intervals if ab[0]<inside<ab[1]];assert len(found)==1,(name,intervals)
 ab=found[0];th=ab[1]-ab[0];rays.append(dict(feature=name,ray_origin_mm=origin,ray_direction=direction,all_solid_intervals_mm=intervals,selected_interval_mm=ab,measured_axis_thickness_mm=th,nominal_axis_thickness_mm=nominal,within_tolerance=(abs(th-nominal)<tolerance if nominal is not None else th>0),below_0_8mm=th<.8,interpretation='Axis thickness at bounded sample, not global minimum normal thickness or printability.'))
# Count4 separated radial members in each fan on3 actual raw-mesh lines.
for side in [-1,1]:
 y=side*7.5
 for z in [22.6,24.,26.]:
  loc,_,_=mesh.ray.intersects_location([[-200,y,z]],[[1,0,0]],multiple_hits=True);xx=np.sort(loc[:,0]);assert len(xx)%2==0
  intervals=[[float(a),float(b)] for a,b in zip(xx[::2],xx[1::2])]
  for pier,lo,hi in [('left',-125.,-20.),('right',20.,125.)]:
   bars=[ab for ab in intervals if lo<ab[0]<ab[1]<hi];assert len(bars)==4,(pier,y,z,bars)
   fan_counts.append(dict(pier=pier,side_y_mm=y,plane_z_mm=z,all_ray_intervals_mm=intervals,selected_radial_intervals_mm=bars,count=4))
   if z==24:
    for k,(a,b) in enumerate(bars):
     x=(a+b)/2;tests.append(local(f'{pier} fan side{side} primary rib{k+1}',[x-.22,y-.64,z-.3],[.44,1.28,.6],[z-.25,z,z+.25],note='Narrow crop intentionally retains all clipped fragments; not a global member width proof.'))
     ray(f'{pier} fan side{side} rib{k+1} transverse thickness',[x,-30,z],[0,1,0],1,y,1.26)
    for k,(before,after) in enumerate(zip(bars,bars[1:])):
     x=(before[1]+after[0])/2;tests.append(local(f'{pier} fan side{side} radial gap{k+1}',[x-.25,y-.9,z-.25],[.5,1.8,.5],[z-.2,z,z+.2],'air',note='Full tiny prism through radial opening; no hidden membrane.'))
# Piers, bearings and ends are solids; river opening and paired-plane space are real air.
for i,px in enumerate([-P,P]):
 tests.append(local(f'RC main pier{i+1}',[px-2,-8,3],[4,16,8],[3.2,6,10.8],note='One width-spanning pier, not two separate columns.'))
 for y in [-7.5,7.5]:
  tests.append(local(f'steel bearing{i+1} side{y}',[px-1,y-.9,14],[2,1.8,.35],[14.05,14.18,14.3],note='Physical steel soleplate at wood/RC interface.'))
 tests.append(local(f'between paired fan planes{i+1}',[px-4,-4,24],[8,8,4],[24.1,26,27.9],'air',note='Widthwise bounded open prism avoids actual transverse ties.'))
for label,x in [('left',-151.5),('right',151.5)]:tests.append(local(label+' end abutment',[x-2,-8,3],[4,16,20],[3.2,12,22.8]))
tests.append(local('central underdeck clear space',[-20,-6,3],[40,12,20],[3.2,13,22.8],'air',note='No solid curtain below central sag.'))
tests.append(local('outside fan to left bank opening',[-139,-5,4],[15,10,18],[4.1,13,21.9],'air'))
tests.append(local('outside fan to right bank opening',[124,-5,4],[15,10,18],[4.1,13,21.9],'air'))
# Walking surface and wave heights from actual vertical ray intersections.
for x in [-145,-78,0,78,145]:
 z=profile(x);tests.append(local(f'deck at x{x}',[x-.12,-2,z-.4],[.24,4,.45],[z-.35,z-.15,z+.02],note='Very narrow curve crop includes clipped thin fragments.'))
 ray(f'deck slab near x{x}',[x+.4,1.3,-2],[0,0,1],2,profile(x+.4),None)
# Fine frame parts and air between diagonal slats stay inspectable, not filled panels.
for side in [-1,1]:
 y=side*7.5
 tests.append(local(f'railing diagonal air opening side{side}',[-148.25,y-.8,32.75],[.45,1.6,.45],[32.8,32.95,33.15],'air'))
 # First regular diagonal traverses x=-146.38 atz33.55 (za29+1.1 plus3.45).
 x=-149.5+7.5*((33.55-30.1)/8.3)
 tests.append(local(f'railing diagonal thin slat side{side}',[x-.10,y-.32,33.45],[.20,.64,.20],[33.47,33.55,33.63],note='0.55mm slat in elevation,0.60mm across width; sub0.8mm warnings mandatory.'))
 ray(f'railing infill transverse thickness side{side}',[x,-30,33.55],[0,1,0],1,y,.60)
 ray(f'railing vertical post transverse thickness side{side}',[-140,-30,profile(-140)+5],[0,1,0],1,y,1.66)
# Joist and underside diagonal: actual slim solids with overhang risks.
x=-148+5*(296/60);z=profile(x)
tests.append(local('underdeck transverse joist',[x-.3,-5,z-1.5],[.6,10,.6],[z-1.45,z-1.2,z-.95],note='0.80mm wide joist; no support-free inference.'))
ray('main side chord across width',[-112.3,-30,profile(-112.3)-.9],[0,1,0],1,-7.5,1.66)
tests.append(local('added display base',[-5,-28,.1],[10,6,1.2],[.2,.7,1.2],note='Added physical plate; not measured terrain or buried footing.'))
centers=mesh.triangles_center;mask=(mesh.face_normals[:,2]<-np.sqrt(.5))&(centers[:,2]>.0001)
by_material={p['id']:dict(triangles=int((mask&(materials==i)).sum()),area_mm2=float(mesh.area_faces[mask&(materials==i)].sum())) for i,p in enumerate(palette)}
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=raw_hash,method='Raw binary STL exact-coordinate weld only; actual mesh intersection crops, unrounded horizontal sections, even-odd nesting; exact -0.4mm erosion for EVERY positive component; no healing or thin-feature exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),air_volume_mismatches=sum(not t['air_volume_is_zero'] for t in tests if t['expected']=='air'),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),failed_0_8mm_components=sum(r['failed_0_8mm'] for r in solidrows),axis_ray_checks=rays,radial_member_ray_counts=fan_counts,all_four_fans_have_four_separate_ribs_at_three_planes=True,axis_thickness_below_0_8mm_samples=sum(q['below_0_8mm'] for q in rays),downward_faces_over_45deg_above_base=int(mask.sum()),downward_area_mm2=float(mesh.area_faces[mask].sum()),overhang_height_threshold_mm=.0001,overhang_by_material=by_material,thin_warning='0.55mm railing slats/0.60mm transverse depth,0.74mm diagonal braces, small steel hardware and geometric tangencies retain sub0.8mm warnings. Crop fragments remain counted; no global normal-thickness/strength proof.',actual_print_tested=False,support_free_certified=False,limitations='No long-span, slicer, strength, support-removal or physical-print certification. Full36m bridge is represented, two banks and four fan planes. Added thin base is not site terrain. Fine member sizes and stair count/angle are inferred, not as-built measurement.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['tests','axis_ray_checks','radial_member_ray_counts']},indent=2))
assert report['occupancy_mismatches']==0 and report['air_volume_mismatches']==0
assert all(r['within_tolerance'] for r in rays)
assert all(r['valid'] for t in tests for r in t['rows'])
