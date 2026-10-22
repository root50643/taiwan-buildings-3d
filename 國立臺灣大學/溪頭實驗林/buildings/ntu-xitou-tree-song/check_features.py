"""Bounded raw-STL checks for NTU Xitou Tree Song single 2019 exhibition house.
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

tests=[]
# All tests are against the delivered raw mesh, not design-intent primitives.
for x in [-68,-22,24,68]:
 for y in [-46,46]:tests.append(local(f'visible foot {x} {y}',[x-1.8,y-1.8,.1],[3.6,3.6,2.8],[.2,1.2,2.8],reference_xy=[x,y]))
for y in [-22,22]:tests.append(local(f'bay foot {y}',[-89.8,y-1.8,.1],[3.6,3.6,2.8],[.2,1.2,2.8],reference_xy=[-88,y]))
for x in [14.65,17.15,19.65]:tests.append(local(f'front woven strip x{x}',[x-.55,-53.2,6.2],[1.1,2.6,70.7],[10,24,30,45,56,70],note='Actual bent 1mm-wide slat, full undulating depth; backing wall excluded. Counts reduced.'))
tests.append(local('front horizontal weaving rail',[20,-53,17.54],[7,3.4,.92],[17.56,18,18.44],note='Rail is connected to opaque backing; front strip crossings not deleted.'))
tests.append(local('opaque front backing behind relief gap',[20.8,-49.9,21],[.5,1.9,15],[22,28,35],note='Narrow crop proves backing is occupied; artificial crop width itself is under0.8mm, retained as a bounded-probe warning, not claimed source wall thickness.'))
for x in [-29.4,11.4]:
 tests.append(local(f'open rectangular door glass x{x}',[x-.53,-43,10],[1.06,10,35],[11,25,44],note='Physical solid glass pane, not geometric air; alpha only visualizes glazing.'))
 tests.append(local(f'open rectangular door top frame x{x}',[x-.6,-43,50.99],[1.2,10,1.32],[51.01,51.6,52.29],note='Static rectangular timber leaf top behind exterior arch; unsupported in printed interior.'))
tests.append(local('fixed elongated bay pane',[-91.31,-7,15],[1.07,14,43],[16,35,57],note='Physical fixed glazing closes bay opening.'))
tests.append(local('fixed window arch surround',[-92.2,-22,12],[2.7,3.5,34],[20,30,40],note='Tall arch surround, not entrance arch.'))
tests.append(local('main curved roof fascia',[-74.91,-56,75],[1.22,112,27],[77,85,95,100.9],note='All attached roof fragments retained; near-crown/edge thin sections warned.'))
tests.append(local('lower bay curved cap front overhang',[-95.21,-33,76],[2.1,66,20],[77.2,85,94.9],note='Lower short roof cap, distinct from continuous main roof; tangent fragments retained.'))
for i,(x,y) in enumerate([(-30,16),(32,16)]):
 tests.append(local(f'lightwell {i+1} wood wall',[x-7.3,y-3,101],[1.85,6,6],[101.1,104,106.9],note='Square upstand wall; hollow core tested separately.'))
 tests.append(local(f'lightwell {i+1} pyramid glazing and seams',[x-8.1,y-8.1,108.0],[16.2,16.2,6.2],[108.1,110,112.8,114.1],note='Whole true cap section, retaining narrowing hip seams and apex tangencies.'))
# Conservative full-volume negative-space probes; none is an invented wall opening.
airs=[('entrance arch usable central opening',[-18,-56,8],[20,13,21]),('front internal aisle',[-7,-42,10],[14,15,36]),('left exhibition interior',[-60,-18,10],[38,56,55]),('right exhibition interior',[0,-18,10],[58,56,55]),('underfloor clearance between visible feet',[-57,-47.5,.2],[20,3,2.5]),('shallow relief gap only not through wall',[20.8,-53.1,29],[.5,.7,6])]
for i,(x,y) in enumerate([(-30,16),(32,16)]):airs.append((f'lightwell {i+1} hollow air core',[x-4,y-4,101],[8,8,5.4]))
for name,origin,size in airs:tests.append(local(name,origin,size,[origin[2]+.01,origin[2]+size[2]/2,origin[2]+size[2]-.01],'air',note='Entire conservative volume has zero occupancy, not just selected planes.'))
# Axis-normal multi-hit rays preserve every occupied interval.
rays=[]
def ray_check(name,origin,direction,axis,inside,nominal,meaning,tolerance=.002):
 loc,ri,fi=mesh.ray.intersects_location([origin],[direction],multiple_hits=True);vals=np.sort(loc[:,axis]);assert len(vals)%2==0,(name,vals)
 intervals=[[float(a),float(b)] for a,b in zip(vals[::2],vals[1::2])];found=[ab for ab in intervals if ab[0]<inside<ab[1]];assert len(found)==1,(name,intervals)
 ab=found[0];th=ab[1]-ab[0];rays.append(dict(feature=name,ray_origin_mm=origin,ray_direction=direction,axis='xyz'[axis],all_solid_intervals_mm=intervals,selected_interval_mm=ab,measured_axis_thickness_mm=th,nominal_axis_thickness_mm=nominal,absolute_error_mm=abs(th-nominal),within_tolerance=abs(th-nominal)<tolerance,interpretation=meaning))
ray_check('painted panel plus opaque front backing',[-9,-100,65.123],[0,1,0],1,-50,4.2,'Combined front panel and backing wall thickness, above the arch.')
ray_check('fixed bay glass pane',[-200,0,35.123],[1,0,0],0,-90.8,1.05,'X-normal fixed pane thickness; not an empty passage.')
for x in [-29.4,11.4]:ray_check(f'inward-open glass leaf {x}',[-200,-35.123,20.123],[1,0,0],0,x,1.02,'X-normal rectangular pane at inward-open 90-degree position; every other wall/glass interval retained.')
ray_check('raised floor',[-45.123,-10.123,-1],[0,0,1],2,4.5,3,'Vertical raised timber floor thickness above clear underfloor air.')
ray_check('far blind wall',[-200,12.123,35.123],[1,0,0],0,70.7,2.2,'X-normal blind far-end backing wall, separate from shallow applique.')
for x in [-30,32]:ray_check(f'pyramidal glass cap {x}',[x+1.1,18.3,-1],[0,0,1],2,111.5,.95,'Vertical thickness of glass cap away from hip seam; actual slope-normal thickness is smaller.')
centers=mesh.triangles_center;mask=(mesh.face_normals[:,2]<-np.sqrt(.5))&(centers[:,2]>.0001)
by_material={p['id']:dict(triangles=int((mask&(materials==i)).sum()),area_mm2=float(mesh.area_faces[mask&(materials==i)].sum())) for i,p in enumerate(palette)}
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=raw_hash,method='Raw binary STL exact-coordinate weld only; actual mesh intersection crops, unrounded horizontal sections, even-odd nesting; exact -0.4mm erosion for every positive component; no healing or thin-feature exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),air_volume_mismatches=sum(not t['air_volume_is_zero'] for t in tests if t['expected']=='air'),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),failed_0_8mm_components=sum(r['failed_0_8mm'] for r in solidrows),axis_ray_checks=rays,downward_faces_over_45deg_above_base=int(mask.sum()),downward_area_mm2=float(mesh.area_faces[mask].sum()),overhang_height_threshold_mm=.0001,overhang_by_material=by_material,thin_warning='Pyramid hip seams, thin relief, curved caps and fascia tangencies retain sub0.8mm warnings. A deliberately narrow backing occupancy crop is itself under0.8mm and is not evidence of wall thickness. These tests are not a global normal-thickness proof.',actual_print_tested=False,support_free_certified=False,limitations='No strength, bridge-span, slicer, support-removal or physical-print certification. Hollow shell includes static inward-open doors, fixed glass and glazing cap represented by solid surfaces; STL cannot encode transparency. Interior vaults omitted; dimensions, counts, hidden feet and rear screen pattern estimated.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['tests','axis_ray_checks']},indent=2))
assert report['occupancy_mismatches']==0 and report['air_volume_mismatches']==0
assert all(r['within_tolerance'] for r in rays)
assert all(r['valid'] for t in tests for r in t['rows'])
