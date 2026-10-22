"""Bounded raw-STL checks for NCU Lulin SLT off-campus main building.
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
# Solid core of each strengthened top guardrail post, no post exemptions.
for x in [33.5,48.0,62.5]:
 for y in [-14.5,14.5]:tests.append(local(f'top guardrail post {x} {y}',[x-.75,y-.75,86.1],[1.5,1.5,8.3],[86.2,87,90,93.5,94.3],reference_xy=[x,y],note='Source counts simplified; actual 1.2 mm diameter post, not a full wall.'))
for y in [-14.5,14.5]:
 for z in [88,91.4,94.6]:tests.append(local(f'guardrail horizontal bar y{y} z{z}',[36,y-.7,z-.56],[8,1.4,1.12],[z-.549,z-.4,z,z+.4,z+.549],note='Near-tangent slices of the true 1.1 mm round bar retained; a thin horizontal cap can fail the 0.8 mm core despite nominal diameter.'))
# Rear ladder stringers, free rungs and cage hoops inspected separately.
for x in [38.3,45.7]:tests.append(local(f'vertical ladder stringer x{x}',[x-.8,33.0,48],[1.6,1.6,16],[48.2,50,54,58,63.8],reference_xy=[x,33.8],note='Strengthened 1.3 mm diameter vertical ladder stringer; no solid backing slab.'))
rung_z=45.3+(66.8-45.3)*(.03+(.97-.03)/6)
tests.append(local('ladder free rung',[40,33.1,rung_z-.55],[4,1.4,1.1],[rung_z-.519,rung_z-.35,rung_z,rung_z+.35,rung_z+.519],note='A 1.04 mm round rung in its free span; actual tangential failures retained.'))
# Cage outer arc excludes its longitudinal central rib at x42.
tests.append(local('rear cage curved hoop',[43.0,35.0,58.45],[2,3,1.1],[58.501,58.7,59,59.3,59.499],note='Outer quadrant of a 1.0 mm diameter protective hoop; boundary and tangent fragments remain in the crop.'))
# Sloped stringer crop around upper ladder, excluding housing surface.
for z in [76,77,79,81.9]:
 y=33.8+(z-66.8)*(17.6-33.8)/(85.7-66.8)
 tests.append(local(f'sloped rear ladder stringer z{z}',[37.5,y-1.05,z-.15],[1.6,2.1,.3],[z],reference_xy=[38.3,y],note='Full horizontal elliptical width around actual sloping rod axis, with any adjoining fragments retained. Probe follows the inclined stringer rather than clipping it with a fixed-Y crop.'))
# Large masses and structural roof edge sampled without erasing attached detail.
tests.append(local('high flat roof outer overhang',[79.5,-34,43.3],[4,8,2.4],[43.5,44.2,45.4],note='High block flat roof plate projects beyond walls; this is an actual mesh corner crop.'))
tests.append(local('wing roof gable free eave',[-65,-35.5,31.4],[8,2.5,2.5],[31.6,32,32.4],note='Shallow roof edge including separate trim and any corrugation, not a global normal-thickness proof.'))
tests.append(local('front shutter closed planar face',[35,-34.9,49],[8,2,17],[49.1,55,65.9],note='Closed proud front shutter geometry; its thin surface ribs and frames are not treated as an opening.'))
tests.append(local('front rail projecting left end',[10.5,-30.6,52.7],[8,3.2,2.8],[52.9,54,55.3],note='Real suspended lateral beam end, kept even though likely needs print support.'))
tests.append(local('porch gable leading edge',[-6,-43.35,33.7],[10,.3,2.3],[33.8,34.2,35.5],note='Thin projecting front lip of estimated entrance roof, not the supporting enclosed vestibule; warnings retained.'))
for i,x in enumerate([-69,-36,31.5,66.7]):tests.append(local(f'front window {i+1} grille lip',[x-4,-35.08,19],[8,.22,5],[19.1,21,23.9],note='Only exposed grille lip, intentionally separated from wall/frame. Thin relief can disappear in FFF; no thin feature exemption.'))
# Entire conservative volume probes establish true air, not just one section.
for y in [-14.5,14.5]:tests.append(local(f'open guardrail bay y{y}',[36,y-1,89],[9,2,1.3],[89.1,89.6,90.2],'air',note='Conservative full-depth core between two horizontal rails and between vertical posts.'))
tests.append(local('top guardrail interior open air',[36,-10,86.3],[8,20,.9],[86.4,86.8,87.1],'air',note='Above narrow flat top and below first guardrail, not a roofless telescope slot.'))
tests.append(local('between rear ladder rungs',[40,33.1,53.4],[4,1.4,1.7],[53.5,54,55.0],'air',note='Full rung-depth central gap between lower ladder rungs; source cage remains open.'))
tests.append(local('rear cage open interior',[40.6,34.8,53.4],[2.8,1.2,3.5],[53.5,55,56.8],'air',note='Full conservative volume between ladder plane and cage outer ribs, not a solid protective slab.'))
tests.append(local('air under left projecting rail',[11,-30.4,47.5],[10,2.8,4.5],[47.6,50,51.9],'air',note='Suspended shutter rail end above roof plate; do not add invented support piers.'))
tests.append(local('air over low wing below tower height',[-80,-25,42],[70,50,20],[42.1,50,61.9],'air',note='Low wing must remain low instead of becoming a uniform tall block.'))
tests.append(local('front outside closed vestibule',[-8,-47,5],[18,3,24],[5.1,16,28.9],'air',note='Outside the closed double doors; no invented open portico or third facade.'))
# Axis-normal multi-hit rays retain all occupied intervals and isolate their target.
rays=[]
def ray_check(name,origin,direction,axis,inside,nominal,meaning,tolerance=.001):
 loc,ri,fi=mesh.ray.intersects_location([origin],[direction],multiple_hits=True)
 vals=np.sort(loc[:,axis]);assert len(vals)%2==0,(name,vals)
 intervals=[[float(a),float(b)] for a,b in zip(vals[::2],vals[1::2])]
 found=[ab for ab in intervals if ab[0]<inside<ab[1]];assert len(found)==1,(name,intervals)
 ab=found[0];th=ab[1]-ab[0]
 rays.append(dict(feature=name,ray_origin_mm=origin,ray_direction=direction,axis='xyz'[axis],all_solid_intervals_mm=intervals,selected_interval_mm=ab,measured_axis_thickness_mm=th,nominal_axis_thickness_mm=nominal,absolute_error_mm=abs(th-nominal),within_tolerance=abs(th-nominal)<tolerance,interpretation=meaning))
for x in [33.5,48,62.5]:ray_check(f'top post x{x}',[x,-100,89.7],[0,1,0],1,-14.5,1.2,'Y-normal diameter through round post axis; separate front/rear intervals retained.')
ray_check('top guardrail bar',[40.123,-14.5,-1],[0,0,1],2,88,1.1,'Vertical diameter through guardrail bar axis, away from posts.')
ray_check('ladder stringer',[38.3,-100,54.123],[0,1,0],1,33.8,1.3,'Y-normal diameter of rear ladder stringer, distinct from solid building and shell.')
ray_check('ladder rung',[41.123,33.8,-1],[0,0,1],2,rung_z,1.04,'Vertical diameter of horizontal rung; all other housing/ladder intervals retained.')
ray_check('flat high roof overhang',[83.5,20.123,-1],[0,0,1],2,44.4,2.2,'Vertical roof-plate thickness at the exterior projecting edge.')
ray_check('projecting shutter rail',[14.123,-29,-1],[0,0,1],2,54,2.6,'Vertical beam-end thickness above the flat roof; no invented column.')
centers=mesh.triangles_center;mask=(mesh.face_normals[:,2]<-np.sqrt(.5))&(centers[:,2]>3.0001)
by_material={p['id']:dict(triangles=int((mask&(materials==i)).sum()),area_mm2=float(mesh.area_faces[mask&(materials==i)].sum())) for i,p in enumerate(palette)}
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=raw_hash,method='Raw binary STL exact-coordinate weld only; actual mesh intersection crops, unrounded horizontal sections, even-odd nesting; exact -0.4mm erosion for every positive component; no healing or thin-feature exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),air_volume_mismatches=sum(not t['air_volume_is_zero'] for t in tests if t['expected']=='air'),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),failed_0_8mm_components=sum(r['failed_0_8mm'] for r in solidrows),axis_ray_checks=rays,downward_faces_over_45deg_above_base=int(mask.sum()),downward_area_mm2=float(mesh.area_faces[mask].sum()),overhang_by_material=by_material,thin_warning='Round rails/rungs/hoops have tangential slice warnings; surface grilles/roof lips may be below 0.8mm. All failures retained. Large connected masses can mask fine parts, so bounded local checks supplement global slices, but are not a global minimum-normal-wall proof.',actual_print_tested=False,support_free_certified=False,limitations='No structural, bridge-span, slicer, support-removal or actual-print certification. White walls are closed solid exterior masses and dark windows/doors are attached relief, not interior rooms or real glass. Dimensions, bar counts and sheet pitch are inferred and simplified.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['tests','axis_ray_checks']},indent=2))
assert report['occupancy_mismatches']==0 and report['air_volume_mismatches']==0
assert all(r['within_tolerance'] for r in rays)
assert all(r['valid'] for t in tests for r in t['rows'])
