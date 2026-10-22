"""Bounded raw-STL checks for TSMC NYCU Energy Education Center Hsinchu 2017 permanent exterior.
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
def sx(z):return -60-8*(z-8)/43
def rz(x):return 51+40*(x+68)/88 if x<=20 else 51+40*(62-x)/42
assert features['not_2014_versailles_prototype'] and features['west_not_south_louvers']
assert features['roof_ridge_x_mm']==20 and features['south_eave_x_mm']==-68
assert features['south_tilted_louver_blades_approximate']==25
# Distinct facades, literal physical glazing solids rather than material-alpha air.
tests.append(local('north lower closed glass',[61.60,5,14],[.8,4,6],[15,17,19],note='0.75mm physical glass thickness; alpha is not geometry removal.'))
tests.append(local('north upper clerestory',[61.60,5,43],[.8,4,5],[43.1,45,47.9],note='Upper translucent horizontal band distinct from lower glass.'))
tests.append(local('east sliding glass panel',[2,-74.40,14],[4,.8,10],[15,18,23],note='0.7mm closed sliding-door glazing; no false claim of open doorway.'))
tests.append(local('east south translucent field',[-34,-74.4,15],[4,.8,10],[16,20,24],note='Opaque/translucent lower left field; not mirrored all-glass front.'))
tests.append(local('west narrow vertical opening',[43,73.6,13],[2,.8,12],[14,19,24],note='Physical glass in narrow opening; no claim whether service door.'))
tests.append(local('west two sash window clear portion',[12,73.6,22],[3,.8,7],[23,25,28],note='Small real glazing zone distinct from continuous thermal band.'))
tests.append(local('west bottle thermal glazing',[-21,73.55,14],[3,.9,9],[15,18,22],note='0.8mm continuous translucent thermal-wall representation. Dense pattern is illustrative, not south louvers.'))
# 25 real louver leaves with true gaps at conservative locations between supports.
for i,z in enumerate(np.linspace(9,49.9,25)):
 x=sx(float(z));tests.append(local(f'south louver {i+1} leaf',[x-.4,5,z+.20],[.8,3,.50],[z+.3,z+.45,z+.6],note='Sloped physical leaf;0.55mm vertical thickness, near-horizontal thin feature retained.'))
 if i<24:
  tests.append(local(f'south louver gap after {i+1}',[x-.35,5,z+1.13],[.55,3,.35],[z+1.15,z+1.30,z+1.45],'air',note='Full bounded prism through a genuine leaf gap, clear of inclined white posts.'))
# Large high interior and lateral passage remain air, not a filled solid glasshouse.
for name,origin,size in [('double_height_east_core',[-15,-35,12],[30,25,38]),('north_passage_beside_greenwall',[40,15,12],[10,13,42]),('above_L_south_arm',[-54,-30,40],[7,20,10])]:
 tests.append(local(name,origin,size,[origin[2]+.1,origin[2]+size[2]/2,origin[2]+size[2]-.1],'air',note='Whole bounded void prism; no assertion that entire house is empty.'))
tests.append(local('L south inner partition',[-43.65,-30,15],[1.3,6,12],[16,21,26],note='Physical interior wall; simplified L living core not furniture fit-out.'))
tests.append(local('L west inner partition',[-14,48.85,15],[6,1.3,12],[16,21,26],note='Other L arm; no copied 2014 plan.'))
tests.append(local('living core low ceiling',[-55,-30,37.05],[8,8,1.15],[37.1,37.6,38.1],note='Horizontal slab; horizontal erosion not a normal-thickness guarantee.'))
tests.append(local('green wall backing',[5,20.4,25],[5,1.2,6],[25.1,28,30.9],note='White wall, simple vegetation attached to visible east side.'))
# End walls/roof remain actual solids; inclined roof and glazing are not full box fill.
for name,x,y in [('long_south_roof',-40,-20),('short_north_clear_roof',49,-20),('north_dark_strip',28,-20)]:
 z=rz(x);tests.append(local(name,[x-.2,y-2,z-.45],[.4,4,.5],[z-.4,z-.2,z],note='Narrow roof intersection includes slope/taper fragments; no thin exemptions.'))
tests.append(local('added print base',[-5,-94,.05],[10,3,1.5],[.1,.8,1.5],note='Extra thin base, not an architectural site outline.'))
# Axis-normal multiple-hit tests retain all intervals, never conceal adjacent solids.
rays=[]
def ray(name,origin,direction,axis,inside,nominal,tolerance=.003):
 loc,_,_=mesh.ray.intersects_location([origin],[direction],multiple_hits=True);vals=np.sort(loc[:,axis]);assert len(vals)%2==0,(name,vals)
 intervals=[[float(a),float(b)] for a,b in zip(vals[::2],vals[1::2])];found=[ab for ab in intervals if ab[0]<inside<ab[1]];assert len(found)==1,(name,intervals)
 ab=found[0];th=ab[1]-ab[0];rays.append(dict(feature=name,ray_origin_mm=origin,ray_direction=direction,all_solid_intervals_mm=intervals,selected_interval_mm=ab,measured_axis_thickness_mm=th,nominal_axis_thickness_mm=nominal,within_tolerance=(th>=.55-1e-4 if nominal is None else abs(th-nominal)<tolerance),below_0_8mm=th<.8,interpretation=('Final leaf is fused into the boundary rail; full combined occupied interval retained, no isolated-leaf nominal equality claimed.' if nominal is None else 'Axis thickness only; not global minimum normal thickness or printability.')))
ray('north lower glass',[-100,7,22],[1,0,0],0,62,.75)
ray('east entry glass',[2,-150,23],[0,1,0],1,-74,.70)
ray('west small window glass',[13,-150,24],[0,1,0],1,74,.70)
ray('west bottle thermal plate',[-20,-150,19],[0,1,0],1,74,.80)
ray('L core south wall',[-100,-24,22],[1,0,0],0,-43,1.2)
ray('L core west wall',[2,-150,23],[0,1,0],1,49.5,1.2)
ray('L core south ceiling',[-52,-24,-1],[0,0,1],2,37.5,1.3)
for i,z in enumerate(np.linspace(9,49.9,25)):
 x=sx(float(z));# At x centre, sloped leaf bounds shift by~0.307mm.
 ray(f'south leaf {i+1} vertical thickness',[x,7,-1],[0,0,1],2,z+.55,(None if i==24 else .55))
# Short roof field physical vertical thickness, away from all purlins/rafters.
ray('north short clear roof vertical thickness',[49,-19,-1],[0,0,1],2,rz(49)-.3,.65)
centers=mesh.triangles_center;mask=(mesh.face_normals[:,2]<-np.sqrt(.5))&(centers[:,2]>.0001)
by_material={p['id']:dict(triangles=int((mask&(materials==i)).sum()),area_mm2=float(mesh.area_faces[mask&(materials==i)].sum())) for i,p in enumerate(palette)}
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=raw_hash,method='Raw binary STL exact-coordinate weld only; actual mesh intersection crops, unrounded horizontal sections, even-odd nesting; exact -0.4mm erosion for every positive component; no healing or thin-feature exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),air_volume_mismatches=sum(not t['air_volume_is_zero'] for t in tests if t['expected']=='air'),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),failed_0_8mm_components=sum(r['failed_0_8mm'] for r in solidrows),axis_ray_checks=rays,axis_thickness_below_0_8mm_samples=sum(q['below_0_8mm'] for q in rays),downward_faces_over_45deg_above_base=int(mask.sum()),downward_area_mm2=float(mesh.area_faces[mask].sum()),overhang_height_threshold_mm=.0001,overhang_by_material=by_material,thin_warning='0.55mm louver leaves,0.65-0.8mm glass/roof sheets, slim frames and geometric tangencies retain sub0.8mm warnings. Every crop fragment counted; bounded local checks are not global normal-thickness/strength proof.',actual_print_tested=False,support_free_certified=False,limitations='No bridge-span, slicer, strength, support-removal or physical-print certification. Large high core and individual louver air gaps remain. Closed translucent glazing is physical material, not air. STEM/architecture teaching approximation, not measured construction or2026 current survey. Module, louver, bottle-pattern counts are approximate.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['tests','axis_ray_checks']},indent=2))
assert report['occupancy_mismatches']==0 and report['air_volume_mismatches']==0
assert all(r['within_tolerance'] for r in rays)
assert all(r['valid'] for t in tests for r in t['rows'])
