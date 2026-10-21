"""Independent bounded QA of the actual NYCU 2020 shelter STL.
Exact-coordinate welding only. No repair, contour rounding, deletion, or thin
feature exemptions. Crop erosion is NOT a global normal wall-thickness proof.
"""
from pathlib import Path
import hashlib,json
import numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection,Point
from shapely.geometry.polygon import orient
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
        rows.append(dict(plane_mm=float(z),components=len(polys),valid=geom.is_valid and invalid==0,area_mm2=float(geom.area),component_areas_mm2=[float(p.area) for p in polys],component_bounds_mm=[list(p.bounds) for p in polys],failed_0_8mm=sum(p.is_empty for p in eroded),eroded_areas_mm2=[float(p.area) for p in eroded],expected_occupancy_met=(not polys if expected=='air' else bool(polys))))
        if reference_xy is not None:
            axis_indices=[i for i,p in enumerate(polys) if p.covers(Point(*reference_xy))]
            rows[-1]['target_axis_component_count']=len(axis_indices)
            rows[-1]['target_axis_component_areas_mm2']=[float(polys[i].area) for i in axis_indices]
            rows[-1]['target_axis_component_failed_0_8mm']=sum(eroded[i].is_empty for i in axis_indices)
            rows[-1]['off_axis_component_count']=len(polys)-len(axis_indices)
    volume=float(crop.volume())
    return dict(feature=name,description=description or {},expected=expected,crop_intersection_volume_mm3=volume,air_volume_is_zero=bool(volume==0) if expected=='air' else None,note=note,rows=rows)

def local(name,origin,size,levels,expected='solid',note='',reference_xy=None):
    crop=m ^ md.Manifold.cube(size).translate(origin)
    return audit_crop(name,crop,levels,expected,note,dict(shape='axis-aligned box',origin_mm=origin,size_mm=size),reference_xy)

def polygon_crop(points,z,height,inset=0):
    p=Polygon(points).buffer(-inset,join_style=2)
    assert p.is_valid and not p.is_empty and p.geom_type=='Polygon'
    p=orient(p,sign=1)
    prism=md.CrossSection([np.asarray(p.exterior.coords[:-1])]).extrude(height).translate((0,0,z))
    return m ^ prism,p

frontz=features['roof_front_level_mm'];hinge=features['roof_hinge_y_mm'];reary=max(p[1] for p in features['roof_outer_xy']);slope=(features['roof_rear_level_mm']-frontz)/(reary-hinge)
def roofz(y):return frontz+slope*max(0,y-hinge)

tests=[]
# Each of the 29 load-column axes is tested separately below the roof soffit.
# This records actual STL occupancy, not independent proof of source position.
columns=features['columns_xy_mm'];assert len(columns)==29
for i,(x,y) in enumerate(columns):
    z=roofz(y)
    shaftlevels=([z-10.0,z-9.0] if y<20 else [])+[z-5.5,z-4.7,z-3.3]
    row=local('load column %02d'%i,[x-1.12,y-1.12,min(shaftlevels)-.2],[2.24,2.24,z-3.1-(min(shaftlevels)-.2)],shaftlevels,note='2.24 mm square bounds contain the complete 1.76 mm shaft and 2.06 mm rope-wrap diameter. All samples lie below nominal soffit; wrapped front shafts also include two lower planes beneath the wrap and lamp to test the actual 1.76 mm shaft. A crop may also meet an adjacent deck/terrain; section areas remain recorded and are not exempted. Hidden coordinates are model estimates, not source survey verification. Off-axis fragments created by a nearby component entering the crop are retained and counted, separately from the target-axis component.',reference_xy=[x,y])
    row['source_position_inferred']=i in features['rear_inferred_column_indices'];row['nominal_column_diameter_mm']=features['load_column_diameter_mm'];row['nearest_other_axis_distance_mm']=float(min(np.linalg.norm(np.asarray([x,y])-np.asarray(q)) for j,q in enumerate(columns) if j!=i));tests.append(row)

# Complete flat/sloping roof patches, no removal of tangent-edge slices.
for name,x,y in [('bare front overhang',-80,-70),('left sloping roof',-14,-5),('right sloping roof',80,38)]:
    z=roofz(y)
    tests.append(local(name,[x-2,y-2,z-3.6],[4,4,4.7],[z-2.7,z-1.5,z-.4,z+.60] if name!='bare front overhang' else [z-2.7,z-1.5,z-.1],note='Actual 4 x 4 mm roof patch; horizontal crop erosion does not directly measure normal roof thickness. Covered patches include the disclosed turf overlay. Bare front slab is checked without turf.'))

# Front upper rail bay: the entire rope depth is included, not a thin clip.
tests.append(local('white front diamond guard-net bay',[-78,-61.6,46.7],[48,1.52,12.8],[47.2,48.0,50.0,52.0,54.0,56.0,57.4,58.2],note='Bay between upper posts; full approximately 0.88–0.90 mm rope depth is within the crop. All separate positive sections and near-tangent cable tips are retained; nominal rope diameter is not a printability guarantee.'))
# One straight guard post and one inclined-roof guard post are explicit samples.
for name,x,y in [('front guard post',-26.52,-60.84),('inner ramp guard post',0,21.84)]:
    z=roofz(y)
    tests.append(local(name,[x-.80,y-.80,z+4],[1.6,1.6,10],[z+4.2,z+8,z+13.5],note='Full nominal 1.36 mm guard-post diameter. Connected diagonal ropes can enter crop; this is not a claim of independent free-standing strength.'))

# Isolate hanging net by the true trapezoid aperture, with roof edge excluded.
net_crop,net_poly=polygon_crop(features['hanging_net_hole_xy'],20,25,inset=1.0)
nm=net_crop.to_mesh64();nv=np.asarray(nm.vert_properties)[:,:3]
assert len(nv)>0
lo=float(nv[:,2].min());hi=float(nv[:,2].max())
levels=np.r_[lo+.001,np.linspace(lo+.1,hi-.1,13),hi-.001]
tests.append(audit_crop('open sagging hanging net, roof excluded',net_crop,levels,note='Crop is the real trapezoid aperture inset 1 mm, extruded from z20 to45. Thus surrounding roof/terrace mass cannot hide rope thinness. End-of-crop near-tangent sections are retained; the inset intentionally excludes the perimeter anchoring cable.',description=dict(shape='inset aperture prism',polygon_xy_mm=list(net_poly.exterior.coords),z_mm=20,height_mm=25,actual_net_z_bounds_mm=[lo,hi],aperture_envelope_volume_mm3=float(net_poly.area*25),occupied_fraction=float(net_crop.volume()/(net_poly.area*25)))))

# Roof perimeter rim samples isolate exposed low lip, not the underlying slab.
tests.append(local('exposed front low roof lip',[-70,-76.4,46.05],[20,1.5,.83],[46.10,46.4,46.8],note='Only exposed rim above the slab is sampled. This does not represent total roof thickness; the crop includes its entire ~1.2 mm horizontal depth.'))

# Suspended slabs/edges and their actual air underside.
tests.append(local('main floor front cantilever edge',[-30,-66,3.15],[12,4,1.9],[3.3,4.0,4.65,4.9],note='Full front-floor edge plus timber overlay; underside overhang is separately counted. Horizontal erosion is not vertical slab-thickness measurement.'))
tests.append(local('left raised deck free end',[-92,3,13.1],[4,4,2.3],[13.3,14.0,14.9,15.20],note='Free end, away from simplified central pedestal. Gray slab plus thin timber overlay are retained.'))
tests.append(local('T counter free slab end',[20,-30,15.1],[4,3,2.0],[15.3,16.0,16.9],note='Free counter end away from its pedestal; 1.8 mm nominal vertical slab is not a validated bridge span.'))

# Essential negative spaces: whole crop volume, not merely selected sections.
tests.append(local('central long roof slot remains open',[8,-5,21],[5,55,25],[21.1,25,30,35,40,45.9],'air',note='Conservative internal corridor of the entire long slot above the ground stairs; does not cross the real edge posts. Entire volume must be zero.'))
tree_crop,tree_poly=polygon_crop(features['tree_hole_xy'],20,35,inset=1.2)
tests.append(audit_crop('tree aperture remains unfilled',tree_crop,[20.1,24,28,32,38,46,54.9],'air','Tree omitted in display model, but full internal aperture remains empty. Inset excludes real rim; all volume above ground is tested.',dict(shape='inset tree-aperture prism',polygon_xy_mm=list(tree_poly.exterior.coords),z_mm=20,height_mm=35)))
tests.append(local('front waiting passage remains open',[-8,-65,6],[11,16,34],[6.1,10,20,30,39.9],'air',note='Local person-passage corridor above the low floor and below the roof, avoiding the known load-column axes; not a full accessibility assessment.'))
tests.append(local('air below hanging net',[57,2,18],[6,8,5],[18.1,20,22.9],'air',note='Air below ropes inside the open net aperture; would detect a filled backing slab.'))
# A through-cell probe: u=v=0.25 in the bilinear trapezoid, between grid strands.
c=np.asarray(features['hanging_net_hole_xy'][:4]);u=vv=.25
xy=(c[0]*(1-u)+c[1]*u)*(1-vv)+(c[3]*(1-u)+c[2]*u)*vv
tests.append(local('hanging net cell is genuinely open',[float(xy[0]-.3),float(xy[1]-.3),20],[.6,.6,25],[20.1,27,31,35,40,44.9],'air',note='Small vertical probe inside a wide cell. This certifies one actual open cell, not every knot or aperture.'))
tests.append(local('air below left free deck end',[-92,3,4.1],[4,4,9],[4.2,8,12,13.05],'air',note='Free-end underside remains open; no invented block fills its overhang.'))

# Independent vertical-ray intervals demonstrate actual local roof/slab thickness.
# Each query retains all intersections and identifies the occupied interval that
# includes the specified interior z. This does not infer a global minimum.
rays=[]
for name,x,y,inside,nominal,meaning in [
 ('bare gray front roof',-80.123,-70.137,44.5,3.0,'gray slab only'),
 ('left ramp with turf',-14.123,-5.137,roofz(-5.137)-1.5,3.65,'3 mm gray slab plus 0.65 mm exposed turf layer'),
 ('right ramp with turf',80.123,38.137,roofz(38.137)-1.5,3.65,'3 mm gray slab plus 0.65 mm exposed turf layer'),
 ('left free deck slab and wood',-90.123,5.137,14,2.03,'1.8 mm gray slab plus 0.23 mm exposed timber overlay'),
 ('T counter free end',22.123,-28.137,16,1.8,'gray counter slab')]:
    loc,ri,fi=mesh.ray.intersects_location([[x,y,-1]],[[0,0,1]],multiple_hits=True)
    order=np.argsort(loc[:,2]);zs=loc[order,2]
    # Exact ray away from vertices avoids accidental multiple copies. No rounding.
    assert len(zs)%2==0,(name,zs)
    intervals=[[float(a),float(b)] for a,b in zip(zs[::2],zs[1::2])]
    candidates=[ab for ab in intervals if ab[0]<inside<ab[1]];assert len(candidates)==1,(name,intervals)
    ab=candidates[0];th=ab[1]-ab[0]
    rays.append(dict(feature=name,xy_mm=[x,y],all_solid_intervals_mm=intervals,selected_interval_mm=ab,measured_vertical_thickness_mm=th,nominal_composite_vertical_mm=nominal,absolute_error_mm=abs(th-nominal),interpretation=meaning))

# Count overhangs from every raw triangle, not just sampled crops.
centers=mesh.triangles_center;normals=mesh.face_normals
mask=(normals[:,2]<-np.sqrt(.5))&(centers[:,2]>2.5001)
by_material={}
for i,p in enumerate(palette):
    selected=mask&(materials==i)
    by_material[p['id']]=dict(triangles=int(selected.sum()),area_mm2=float(mesh.area_faces[selected].sum()))
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']]
airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=raw_hash,method='Raw binary STL exact-coordinate weld only; actual mesh intersection crops, unrounded horizontal sections, even-odd nesting, exact -0.4 mm Shapely erosion on each positive connected component. No healing, removal of islands, or thin-feature exemption.',tests=tests,column_axes_tested=len(columns),column_primary_component_failed_0_8mm_samples=sum(r['target_axis_component_failed_0_8mm']>0 for t in tests if t['feature'].startswith('load column') for r in t['rows']),column_samples_with_off_axis_fragments=sum(r['off_axis_component_count']>0 for t in tests if t['feature'].startswith('load column') for r in t['rows']),solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),air_volume_mismatches=sum(not t['air_volume_is_zero'] for t in tests if t['expected']=='air'),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),failed_0_8mm_components=sum(r['failed_0_8mm'] for r in solidrows),vertical_ray_checks=rays,downward_faces_over_45deg_above_base=int(mask.sum()),downward_area_mm2=float(mesh.area_faces[mask].sum()),overhang_by_material=by_material,front_direction='negative Y',thin_warning='Fine guard ropes, sagging-net strands, grazing slices at curved cables and slender rim ends can fall below the 0.8 mm erosion core. Global connected-section erosion can hide attached details, hence isolated aperture and rail-bay checks. No failure is exempted. Crop boundaries may create thin end slices; those remain recorded and are explicitly not global normal-wall measurements.',actual_print_tested=False,support_free_certified=False,limitations='29 column axes are verified as model occupancy, not surveyed source positions. Numerical crop/ray samples are not exhaustive wall thickness, loading, cable strength, extrusion-width, bridge, FFF, accessibility or physical-print simulation. Broad roof underside, thin ropes, raised deck ends and T counter require slicer support/orientation review. Downward area is not an automatic support or filament estimate.')
assert raw_hash==hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'STL changed during audit'
(A/'qa/local-features.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:q for k,q in report.items() if k not in ['tests','vertical_ray_checks']},ensure_ascii=False,indent=2))
assert report['occupancy_mismatches']==0,'Expected actual crop occupancy mismatch; diagnose rather than repair'
assert report['air_volume_mismatches']==0,'Expected air volume contains real geometry'
assert all(r['target_axis_component_count']==1 for t in tests if t['feature'].startswith('load column') for r in t['rows']),'Missing or ambiguous column-axis occupancy'
assert all(r['valid'] for t in tests for r in t['rows']),'Invalid local section'
assert all(r['absolute_error_mm']<.001 for r in rays),'Local measured slab thickness differs from specified composite'
