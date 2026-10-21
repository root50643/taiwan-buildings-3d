"""Bounded raw-STL checks for NYCU 2007 Bamboo Lake / North Gate shelter.
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
# Four rear frame axes checked separately in the actual unified mesh. Attached
# pane edges / bounded white left sheet remain in the crops, never hidden.
axes=features['back_frame_x_mm'];assert len(axes)==4
for i,x in enumerate(axes):
 tests.append(local(f'rear frame {i+1}',[x-1.05,25.9,29],[2.1,2.4,43],[30,45,60,70],note='Nominal 1.8 by 1.65 mm frame; attached glazing edges may enter this full-depth crop. The leftmost crop also meets the bounded white rear sheet. Axis component is distinguished from every retained off-axis fragment. These are model occupancy checks, not independent survey-location proof.',reference_xy=[x,27]))
 # Sample forward arms where the sloped glass is above, not merged into them.
 tests.append(local(f'forward cantilever arm {i+1}',[x-1.05,-20,83.5],[2.1,5,2.0],[83.7,84.1,84.5,85.2],note='Full 1.8 mm width arm patch. The glass canopy is above this patch; bridge length and structural loading are not certified.'))
# Rear and roof panes are tested as solids, not falsely treated as geometric air.
# Transparency belongs to scene/3MF material metadata, and is absent from STL.
for i,(a,b) in enumerate(zip(axes,axes[1:])):
 x=(a+b)/2
 tests.append(local(f'rear glazing pane {i+1}',[x-4,26.4,23],[8,1.5,45],[24,35,50,65],note='Actual strengthened 1.1 mm glazing solid, away from frames. STL is opaque geometry regardless of transparent scene material.'))
 crop=m ^ md.Manifold.cube((8,8,3)).translate((x-4,-29,84.5))
 cv=np.asarray(crop.to_mesh64().vert_properties)[:,:3];lo=float(cv[:,2].min());hi=float(cv[:,2].max())
 tests.append(audit_crop(f'roof glazing pane {i+1}',crop,[lo+.001,lo+.025,lo+.1,(lo+hi)/2,hi-.1,hi-.025,hi-.001],note='Full sloped glass patch away from supporting arms and white shell. Near-tangent end slices are retained, including thin slivers; horizontal erosion does not directly measure normal glass thickness.',description=dict(shape='axis-aligned box',origin_mm=[x-4,-29,84.5],size_mm=[8,8,3],actual_solid_z_bounds_mm=[lo,hi])))
# Opaque shell, seat and return members all remain distinct from the glass.
for name,x in [('left vertical shell',-83),('right ground-reaching shell',83)]:
 tests.append(local(name,[x-1.5,-6,29],[3,12,33],[30,40,50,60],note='Full 2.6 mm white-shell width at a straight segment, away from the bounded rear sheet.'))
for name,x,y in [('left white roof band',-50,0),('middle white roof band',16,5)]:
 tests.append(local(name,[x-4,y-4,75.5],[8,8,3],[75.75,76.5,77.5,78.25],note='White shell roof patch, separately below the glass roof; vertical ray thickness is additionally measured.'))
tests.append(local('left forward rolled-seat top',[-55,-9,13.5],[2,8,3],[13.8,14.5,15.5,16.2],note='Inner end of left seat top away from overlap with the main white-shell turn; nominal 2.5 mm vertical sheet.'))
tests.append(local('left rolled-seat lower return',[-66,-10,3.0],[10,8,3],[3.2,4.0,4.8,5.6],note='Lower return plate above plinth, without a mounting foot. Nominal 2.5 mm thickness.'))
tests.append(local('left rolled front curve',[-66,-26,4.0],[10,8,12],[4.2,6,9.7,13,15.9],note='The front half-round curl is sampled through its full height; tangential curved sections are retained. This crop intentionally excludes the back end of the return.'))
tests.append(local('long rear seat free span',[-12,14,13.5],[8,10,3],[13.8,14.5,15.5,16.2],note='Long suspended seat, away from the central and right returns. No invented solid pedestal backs this span.'))
tests.append(local('central seat return upright',[7.8,15.2,8.5],[2.4,8.8,5],[9,10,11,12.5],note='Full central return upright width; curves near the bottom may broaden the actual section.'))
tests.append(local('central seat lower return',[-34,15.2,4.3],[10,8.8,2.2],[4.5,5,5.6,6.25],note='Nominal 1.9 mm horizontal return, not a slab filling the complete bench underside.'))
tests.append(local('right seat downturned foot',[62.5,14,3.2],[3,10,5.5],[3.3,5,7,8.5],note='Right bench end turns down to the display base; no mirrored left leg is invented.'))
tests.append(local('rear-frame low mounting foot', [30,24.6,3.1],[4,4.5,1.2],[3.2,3.7,4.1],note='Actual low frame foot that enters the backmost seat underside; recorded as solid rather than silently called air.'))
tests.append(local('exposed roof LED seam lip',[-5,-4.1,77.0],[10,.15,.48],[77.01,77.2,77.47],note='Only the shallow dark surface projection in front of the white roof is isolated, not the supporting white-shell thickness. Its approximately 0.13 mm exposure is a retained thin-detail warning and can disappear in FFF. This crop intentionally excludes the structural roof body and is not a minimum-wall test.'))
# Essential air is verified by the entire conservative crop intersection volume,
# not just section samples. Pane areas are deliberately not claimed to be air.
tests.append(local('left tall slot through rear white sheet',[-65.5,23,26],[7,6,35],[26.1,35,45,60.9],'air',note='Internal rectangular portion of the capsule-shaped slot, through the full rear sheet and beyond; full volume must be empty. Rounded ends are outside this conservative core probe.'))
tests.append(local('left rolled-seat horizontal through opening',[-71,-17,6.1],[20,29,7.0],[6.2,8,10,13.0],'air',note='Full width through the left return seat, between its top and bottom plates. Neither an opaque slab nor a pedestal may fill this real opening.'))
tests.append(local('central L-seat under-span opening',[-47,12,6.8],[50,14,6.0],[6.9,8,10,12.7],'air',note='Full depth beneath long bench and above its central lower return, clear of the turning upright and left curl.'))
tests.append(local('right seat under-span opening',[17,12,3.2],[38,12,10],[3.3,6,10,13.1],'air',note='Air between the central return and right downturned end, above display base and below seat. Backmost 1.5 mm of seat depth is excluded because the real modeled back-frame feet project to y24.5 at z3–4.2; this is a conservative clear core, not an assertion that their footings are absent.'))
tests.append(local('open front entrance',[-45,-23,18],[100,32,52],[18.1,30,50,69.9],'air',note='Conservative broad entry volume below white roof and in front of seating and glazing; no white wall is permitted. This is not an accessibility assessment.'))
tests.append(local('air below left suspended shell turn',[-79,-8,3.2],[7,18,10],[3.3,6,10,13.1],'air',note='Left shell does not descend to ground like the right. This crop is below its rounded lower bend, outside the rolled seat.'))
tests.append(local('air under projecting glass canopy',[-24,-29,35],[16,8,49],[35.1,50,70,83.9],'air',note='Front glass canopy is separate from the recessed white roof band; the underside void must not be filled with a white slab.'))
tests.append(local('recessed central roof leading edge',[-24,-9.5,76],[16,4.8,2.0],[76.1,77,77.9],'air',note='Middle/right white roof front edge steps back compared with left band. This checks the actual front-edge notch, not a uniform-depth arch.'))
# Unrounded multi-hit rays isolate local thickness along relevant normals.
# Exact test positions avoid shared edges; all occupied intervals are recorded.
rays=[]
def ray_check(name,origin,direction,axis,inside,nominal,meaning):
 loc,ri,fi=mesh.ray.intersects_location([origin],[direction],multiple_hits=True)
 vals=np.sort(loc[:,axis]);assert len(vals)%2==0,(name,vals)
 intervals=[[float(a),float(b)] for a,b in zip(vals[::2],vals[1::2])]
 found=[ab for ab in intervals if ab[0]<inside<ab[1]];assert len(found)==1,(name,intervals)
 ab=found[0];th=ab[1]-ab[0]
 rays.append(dict(feature=name,ray_origin_mm=origin,ray_direction=direction,axis='xyz'[axis],all_solid_intervals_mm=intervals,selected_interval_mm=ab,measured_axis_thickness_mm=th,nominal_axis_thickness_mm=nominal,absolute_error_mm=abs(th-nominal),interpretation=meaning))
for i,x in enumerate([-16.123,16.123,48.123]):
 ray_check(f'rear glazing pane {i+1}',[x,-100,40.137],[0,1,0],1,27.1,1.1,'True Y-normal thickness of strengthened rear pane; transparent material does not change occupancy.')
 y=-24.137;lo=84.5+.025*(27-y)
 ray_check(f'roof glazing pane {i+1}',[x,y,-1],[0,0,1],2,lo+.5,1.1,'Vertical thickness of sloped roof glass; normal thickness is this value divided by sqrt(1+0.025^2), not a whole-model minimum.')
for name,x,y in [('left white roof',-50.123,.137),('middle white roof',16.123,5.137)]:
 ray_check(name,[x,y,-1],[0,0,1],2,77,2.6,'Vertical white roof slab only; separate glass above is preserved in the full interval list.')
for name,x,inside in [('left white vertical shell',-83.0,-83.0),('right white vertical shell',83.0,83.0)]:
 ray_check(name,[-110,.137,40.137],[1,0,0],0,inside,2.6,'X-normal straight shell thickness, both left and right shell intersections retained.')
ray_check('left rolled-seat top',[-54.137,-5.137,-1],[0,0,1],2,15,2.5,'Vertical sheet thickness at inner seat end away from overlap with main shell.')
ray_check('long rear seat',[-10.137,18.137,-1],[0,0,1],2,15,2.5,'Suspended long seat; full ray also retains the separate lower return.')
ray_check('central lower seat return',[-25.137,18.137,-1],[0,0,1],2,5.4,1.9,'Lower return sheet only; clear air remains between it and upper seat.')
# Overhangs use every raw triangle and the same source face-material mapping.
centers=mesh.triangles_center;mask=(mesh.face_normals[:,2]<-np.sqrt(.5))&(centers[:,2]>3.0001)
by_material={p['id']:dict(triangles=int((mask&(materials==i)).sum()),area_mm2=float(mesh.area_faces[mask&(materials==i)].sum())) for i,p in enumerate(palette)}
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=raw_hash,method='Raw binary STL exact-coordinate weld only; actual mesh intersection crops, unrounded horizontal sections and even-odd nesting; exact -0.4 mm Shapely erosion on every positive component. No healing, island removal or thin-feature exemption.',tests=tests,rear_frame_axes_tested=len(axes),rear_glass_panes_tested=3,roof_glass_panes_tested=3,frame_axis_failed_0_8mm_samples=sum(r['target_axis_component_failed_0_8mm']>0 for t in tests if t['feature'].startswith('rear frame') for r in t['rows']),solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),air_volume_mismatches=sum(not t['air_volume_is_zero'] for t in tests if t['expected']=='air'),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),failed_0_8mm_components=sum(r['failed_0_8mm'] for r in solidrows),axis_ray_checks=rays,downward_faces_over_45deg_above_base=int(mask.sum()),downward_area_mm2=float(mesh.area_faces[mask].sum()),overhang_by_material=by_material,front_direction='negative Y',thin_warning='Sloped-pane tangent slices, curved-shell/seat boundaries, and narrow LED seam lips can fall below a 0.8 mm erosion core. All observed failures remain recorded. Horizontal component erosion is not a global normal-wall thickness proof and connected masses can mask details, hence separate glass/arm/seat crops.',glass_translation='Rear and roof glass sheets are physical STL solids. Scene alpha / 3MF display alpha does not create geometric air and cannot make opaque filament transparent. Glazing crops are therefore tested as solid. True source openings and entrance are separately tested for zero occupied volume.',actual_print_tested=False,support_free_certified=False,limitations='Photos/drawings support bounded visual approximation, not survey dimensions. These numerical samples do not validate complete wall thickness, structural strength, bridge spans, slicer extrusion widths, FFF support removal, accessibility or physical printing. Downward area is not automatic support area or filament consumption.')
assert raw_hash==hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'STL changed during audit'
(A/'qa/local-features.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:q for k,q in report.items() if k not in ['tests','axis_ray_checks']},ensure_ascii=False,indent=2))
assert report['occupancy_mismatches']==0,'Expected actual crop occupancy mismatch; diagnose rather than repair'
assert report['air_volume_mismatches']==0,'Expected air volume contains real geometry'
assert all(r['target_axis_component_count']==1 for t in tests if t['feature'].startswith('rear frame') for r in t['rows']),'Missing or ambiguous frame-axis occupancy'
assert all(r['valid'] for t in tests for r in t['rows']),'Invalid local section'
assert all(r['absolute_error_mm']<.001 for r in rays),'Measured local thickness differs from specified thickness'
