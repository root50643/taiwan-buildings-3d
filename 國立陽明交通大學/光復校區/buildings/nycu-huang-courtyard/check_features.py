"""Bounded raw-STL checks for NYCU Huang Courtyard 2024 project-photo exterior.
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
assert features['seat_rows']==7 and features['left_half_steps']==7
assert features['seat_counts_front_to_back']==[10,8,7,7,4,3,2]
assert features['visible_cushion_total']==41 and len(features['seat_records'])==41
assert features['front_stage_ring_rail'] is False
rows=features['rows'];seats=features['seat_records'];T=features['rear_shell_vertical_thickness_mm']
def shellz(y):
 u=max(0.,y+10)
 return T+.43*u+.00115*u*u
# Explicit full-volume crops, not a sampled point hidden inside a broad solid.
for row in rows:
 i=row['row'];yf=row['y_front'];yb=row['y_back'];z=row['z']
 # A short isolated span of one genuine longitudinal web, away from crossbars/cushions.
 tests.append(local(f'row {i} longitudinal grating web',[3.68,yf+3.15,z+.20],[.64,1.1,.60],[z+.25,z+.50,z+.75],note='Actual0.56mm grating web, deliberately narrower than0.8mm; no exemption. Crop excludes adjacent transverse grid bars.'))
 tests.append(local(f'row {i} front edge frame',[2.1,yf-.01,z-.54],[3.1,.78,1.38],[z-.45,z,z+.75],note='Thin front lip frame, not a full-height solid riser.'))
 # A small actual lattice cell. This is above the cross-rib, below the cushion tops.
 tests.append(local(f'row {i} true grid cell',[4.62,yf+3.15,z+.21],[1.15,1.1,.52],[z+.25,z+.45,z+.70],'air',note='Entire bounded prism through a genuine open grid cell must have zero occupied volume.'))
 # Major under-row space between adjacent diagonal fins, above the sloping bottom skin.
 xs=row['fin_x'];pairs=list(zip(xs[:-1],xs[1:]));p=min(pairs,key=lambda ab:abs(sum(ab)/2));xc=sum(p)/2
 low=shellz(yf+3.8)+.25;high=z-.85
 assert high>low
 tests.append(local(f'row {i} open air beneath seating terrace',[xc-1.9,yf+1.4,low],[3.8,2.4,high-low],[low+.01,(low+high)/2,high-.01],'air',note='Conservative complete volume between actual fins; does not claim the entire under-row region is clear.'))
 # One fin, with every crop fragment/section retained.
 x=min(xs,key=abs);low=shellz(yf+.8);high=z+.10
 tests.append(local(f'row {i} inclined support plate',[x-.50,yf+.79,low+.02],[1.0,yb-yf-.9,high-low-.03],[low+.25*(high-low),low+.5*(high-low),low+.75*(high-low)],note='0.96mm-wide inclined plate; sliced shape and taper fragments not removed.'))
 # Left U-section half-stair with no fictional mirror staircase.
 x=row['half_step_x'];top=row['half_step_top'];base=T if i==1 else rows[i-2]['z']+.85;cy=yf-3.1
 tests.append(local(f'left half-step {i} front face',[x-3,cy-3.21,base+.08],[6,.84,top-base-.12],[base+.15,(base+top)/2,top-.10],note='Front half-step face, approximately0.8mm thick; all tangent thin warnings retained.'))
 tests.append(local(f'left half-step {i} top plate',[x-3,cy-1.9,top-.79],[6,3.6,.78],[top-.7,top-.4,top-.05],note='Horizontal half-step plate; this is not a new seating row.'))
# Continuous flat stage and curved rear skin: deliberately separate from seat platforms.
tests.append(local('front horizontal wafer stage',[-8,-52,.05],[16,14,T-.1],[.1,T/2,T-.1],note='Actual low stage skin, not an added landscape pedestal.'))
for y in [18.3,42.3,73.3]:
 lo=shellz(y-.8)-T+.05;hi=shellz(y+.8)-.05
 tests.append(local(f'curved rear skin y{y}',[-3,y-.8,lo],[6,1.6,hi-lo],[shellz(y)-T+.15,shellz(y)-T/2,shellz(y)-.15],note='Small strip of curved skin; slope and crop tangencies can create thin components. Not a global normal-thickness test.'))
# Every cushion is tested as a solid dish/skirt: alpha is not geometric air.
for seat in seats:
 x=seat['x'];y=seat['y'];z=seat['z'];name=f"row {seat['row']} cushion {seat['index']}"
 tests.append(local(name+' bowl centre',[x-.6,y-.5,z-.10],[1.2,1,.70],[z,z+.20,z+.40],note='Shallow concave solid cushion centre; visual translucency does not remove material.'))
 tests.append(local(name+' downward skirt',[x-.8,y-2.7,z-1.1],[1.6,.95,1.25],[z-.95,z-.5,z+.1],note='Semicircular hanging skirt physically joins the top and edge beam; no detached ball/chair.'))
# Rear handrail mid-arc segment, and one actual sparse support post.
ra=79.35;top=shellz(ra)+16
# Widths deliberately include the full pipe cross-section rather than trimming it to pass.
tests.append(local('rear arch centre handrail',[-2.5,ra-.8,top-.75],[5,1.6,1.5],[top-.55,top,top+.55],note='Full actual cylindrical-polygonal handrail section including near-tangent caps; not guaranteed0.8mm at every z.'))
postx=0;posty=ra*.99;postbottom=shellz(posty)-.15
mid=(postbottom+top)/2
# This slanted post interpolates in y between its bottom and its top.
postymid=(posty+ra)/2
tests.append(local('rear centre support post',[-.6,postymid-.8,mid-1.5],[1.2,1.6,3],[mid-1.2,mid,mid+1.2],note='One actual1.0mm diameter sparse rail post, not an invented opaque rear fence.'))
# No guardrail or invented objects may occupy the front-stage pedestrian space.
for x in [-45,0,45]:tests.append(local(f'open front stage air x{x}',[x-5,-52,T+.15],[10,12,12],[T+.2,T+5,T+11.9],'air',note='Above low stage: bounded entire volume, no front-ring handrail.'))
# Axis-normal multi-hit rays preserve every occupied interval.
rays=[]
def ray_check(name,origin,direction,axis,inside,nominal,meaning,tolerance=.002):
 loc,ri,fi=mesh.ray.intersects_location([origin],[direction],multiple_hits=True);vals=np.sort(loc[:,axis]);assert len(vals)%2==0,(name,vals)
 intervals=[[float(a),float(b)] for a,b in zip(vals[::2],vals[1::2])];found=[ab for ab in intervals if ab[0]<inside<ab[1]];assert len(found)==1,(name,intervals)
 ab=found[0];th=ab[1]-ab[0];rays.append(dict(feature=name,ray_origin_mm=origin,ray_direction=direction,axis='xyz'[axis],all_solid_intervals_mm=intervals,selected_interval_mm=ab,measured_axis_thickness_mm=th,nominal_axis_thickness_mm=nominal,absolute_error_mm=abs(th-nominal),within_tolerance=abs(th-nominal)<tolerance,interpretation=meaning))
ray_check('flat front wafer stage',[.123,-38.123,-1],[0,0,1],2,T/2,T,'Vertical stage-skin thickness; no architectural scale is implied.')
# Curved skin is measured vertically, explicitly not slope-normal thickness.
for y in [20.123,45.123,73.123]:
 ray_check(f'curved wafer skin at y{y}',[3.123,y,-1],[0,0,1],2,shellz(y)-T/2,T,'Vertical curved-skin thickness. Any higher deck/cushion intervals are retained; normal thickness is smaller.')
for row in rows:
 z=row['z'];yf=row['y_front'];i=row['row']
 ray_check(f'row {i} longitudinal web width',[-150,yf+3.8,z+.5],[1,0,0],0,4.0,.56,'X-normal width of isolated web; all other lattice and frame intervals retained.')
 # Through the complete half-step face, clear of the top and side cheeks.
 base=T if i==1 else rows[i-2]['z']+.85;top=row['half_step_top'];cy=yf-3.1
 ray_check(f'left half-step {i} front plate',[row['half_step_x'],-150,(base+top)/2],[0,1,0],1,cy-2.8,.8,'Y-normal front plate thickness, not the step void or a solid riser.')
# Shallow horizontal cushions can pass XY erosion while being vertically thin.
# Measure actual occupied ray intervals through clear grid holes, not through a web.
cushion_thickness_rays=[]
for row in rows:
 seat=next(q for q in seats if q['row']==row['row'])
 x,y,z=seat['x'],seat['y'],seat['z']
 gridxs=np.arange(-80,80.01,2.4)
 dx=next(d for d in [.7,-.7,1.0,-1.0,1.3,-1.3] if np.min(abs(gridxs-(x+d)))>.40)
 origin=[x+dx,y+.9,-1];direction=[0,0,1]
 loc,_,_=mesh.ray.intersects_location([origin],[direction],multiple_hits=True)
 vals=np.sort(loc[:,2]);assert len(vals)%2==0
 intervals=[[float(a),float(b)] for a,b in zip(vals[::2],vals[1::2])]
 found=[ab for ab in intervals if ab[0]<z+.2<ab[1]];assert len(found)==1
 ab=found[0];th=ab[1]-ab[0]
 assert .60<th<1.08
 cushion_thickness_rays.append(dict(feature=f"row {row['row']} cushion {seat['index']} dish",ray_origin_mm=origin,ray_direction=direction,axis='z',all_solid_intervals_mm=intervals,selected_interval_mm=ab,measured_axis_thickness_mm=th,below_0_8mm=th<.8,interpretation='Actual vertical dish thickness measured above a genuine grid hole; no nominal exact claim for faceted curved upper surface. XY erosion alone does not detect this horizontal thinness.'))
 ray_check(f"row {row['row']} cushion {seat['index']} skirt thickness",[x,-150,z-1.2],[0,1,0],1,y-2.2,.85,'Y-normal physical skirt thickness below the tread; every other encountered solid interval retained.')
 # Half-step horizontal top is also measured vertically, rather than only in XY.
 ray_check(f"left half-step {row['row']} horizontal plate",[row['half_step_x'],row['y_front']-3.1,-1],[0,0,1],2,row['half_step_top']-.4,.8,'Vertical half-step top-plate thickness, away from front face and side cheeks.')
centers=mesh.triangles_center;mask=(mesh.face_normals[:,2]<-np.sqrt(.5))&(centers[:,2]>.0001)
by_material={p['id']:dict(triangles=int((mask&(materials==i)).sum()),area_mm2=float(mesh.area_faces[mask&(materials==i)].sum())) for i,p in enumerate(palette)}
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=raw_hash,method='Raw binary STL exact-coordinate weld only; actual mesh intersection crops, unrounded horizontal sections, even-odd nesting; exact -0.4mm erosion for every positive component; no healing or thin-feature exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),air_volume_mismatches=sum(not t['air_volume_is_zero'] for t in tests if t['expected']=='air'),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),failed_0_8mm_components=sum(r['failed_0_8mm'] for r in solidrows),axis_ray_checks=rays,cushion_thickness_rays=cushion_thickness_rays,cushion_vertical_below_0_8mm_samples=sum(q['below_0_8mm'] for q in cushion_thickness_rays),downward_faces_over_45deg_above_base=int(mask.sum()),downward_area_mm2=float(mesh.area_faces[mask].sum()),overhang_height_threshold_mm=.0001,overhang_by_material=by_material,thin_warning='Genuine0.56mm grid webs,0.8mm half-step plates, cushion shells/skirts and handrail tangencies retain every sub0.8mm erosion warning. Crops test bounded regions, not global normal thickness or strength.',actual_print_tested=False,support_free_certified=False,limitations='No strength, bridge-span, slicer, support-removal or physical-print certification. Seven actual lattice decks and major under-row air gaps remain; solid translucent cushions are not geometric air and STL cannot encode transparency. Curvature, display dimensions, grid density, ribs and sparse rail supports are approximated from2024 project photos, not a2026 survey.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['tests','axis_ray_checks']},indent=2))
assert report['occupancy_mismatches']==0 and report['air_volume_mismatches']==0
assert all(r['within_tolerance'] for r in rays)
assert all(r['valid'] for t in tests for r in t['rows'])
