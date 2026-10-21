"""Independent bounded checks of the delivered raw SCU gate STL.
No repair, contour rounding, deletion of thin islands, or thin-feature exemption.
Local crop erosion describes the crop, NOT a global minimum wall thickness proof.
"""
from pathlib import Path
import hashlib,json
import numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection
from qa_model import raw_read
A=Path(__file__).resolve().parent
raw_hash=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest()
_,v,f=raw_read(A/'model.stl')
m=md.Manifold(md.Mesh(np.asarray(v,dtype=np.float32),np.asarray(f,dtype=np.uint32)))
assert m.status().name=='NoError'
def local(name,origin,size,levels,expected='solid',note=''):
    crop=m ^ md.Manifold.cube(size).translate(origin)
    rows=[]
    for z in levels:
        geom=GeometryCollection()
        for contour in crop.slice(float(z)).to_polygons():
            if len(contour)>2:geom=geom.symmetric_difference(Polygon(contour))
        polys=list(geom.geoms) if geom.geom_type=='MultiPolygon' else ([] if geom.is_empty else [geom])
        eroded=[p.buffer(-.4,quad_segs=16) for p in polys]
        rows.append(dict(plane_mm=float(z),components=len(polys),valid=geom.is_valid,area_mm2=float(geom.area),component_areas_mm2=[float(p.area) for p in polys],failed_0_8mm=sum(p.is_empty for p in eroded),eroded_areas_mm2=[float(p.area) for p in eroded],expected_occupancy_met=(not polys if expected=='air' else bool(polys))))
    return dict(feature=name,crop_origin=origin,crop_size=size,expected=expected,crop_intersection_volume_mm3=float(crop.volume()),air_volume_is_zero=bool(crop.volume()==0) if expected=='air' else None,note=note,rows=rows)
tests=[]
for x in [-83,83]:
    tests.append(local('deep faceted pier and tapered cap', [x-7.1,-11.1,3.6],[14.2,22.2,150], [4,40,95,139.8,145,150,153,153.49], note='Full pier-plan bounds, no body-backed crop exemption; near-cap thin slices retained.'))
for x in [-74.5,74.5]:
    tests.append(local('inner vertical support below rounded shoulder',[x-.75,-5.7,3.6],[1.5,11.4,93],[4,40,90,96]))
tests.append(local('single full through-opening, no door leaves',[-70,-15,3.6],[140,30,92],[4,30,60,90,95],'air'))
tests.append(local('central high crown remains open',[-1,-10,110],[2,20,7.49],[110.1,115,117,117.48],'air'))
for x in [-69.8,69.8]:
    tests.append(local('rounded shoulder air below soffit',[x-.4,-7,99],[.8,14,3],[99.1,100,101.5],'air'))
tests.append(local('continuous solid spandrel',[-70,-5.7,120],[140,11.4,17.5],[121,126,132,137]))
tests.append(local('continuous upper cap',[-75,-6.7,137.75],[150,13.4,2],[138,139,139.7]))
tests.append(local('front-only raised bevel plaque',[-10,-8.9,120.5],[20,3,21.5],[121,126,135,141.8]))
tests.append(local('rear remains unlettered and without plaque or seal',[-67,5.9,121],[134,5,16.5],[121.1,126,131.3,136.9],'air',note='Behind main spandrel surface, below cap and above arch band; entire volume also checked empty.'))
for char,x in zip('學大吳東',[-56,-29,29,56]):
    tests.append(local('front raised character '+char,[x-8,-6.81,119.5],[16,1.0,15.5],[121,124,127,130,133],note='Only exposed relief beyond white backing; 1.0 mm Y crop includes real front at -6.8 and excludes backing at -5.8. Erosion may flag serif/island width; not a total structural thickness claim.'))
for y in [-6.36,5.81]:
    tests.append(local('exposed shallow-arch moulding',[-73,y,97],[146,.55,23],[98,105,113,117.8,119.2],note='Exposed moulding projection only, not full backed band thickness; 0.55 mm crop width intentionally reports fine ornament, no exemption.'))
tests.append(local('thin exposed seal rings',[-9.1,-9.70,122.2],[18.2,.27,18.2],[122.5,125,128,131.3,137,140.2],note='Only ring relief in front of disc, actual exposed depth about 0.225 mm. This is ornament resolution risk, not disconnected load-bearing material.'))
tests.append(local('print connector base, not historic site platform',[-96,-19,0],[192,38,3.5],[.2,1.75,3.4]))
mesh=trimesh.Trimesh(v,f,process=False)
centers=mesh.triangles_center;normals=mesh.face_normals
mask=(normals[:,2]<-np.sqrt(.5))&(centers[:,2]>3.501)
# Entire actual STL overhang calculation, independent of the local crops.
regions={
 'seal_and_plaque_front':(centers[:,1]<-6.81)&(np.abs(centers[:,0])<12.1)&(centers[:,2]>118),
 'raised_letters':(centers[:,1]<-5.801)&(centers[:,1]>-6.801)&(np.abs(centers[:,0])>20)&(np.abs(centers[:,0])<66)&(centers[:,2]>119.5)&(centers[:,2]<135),
}
classified=np.zeros(len(f),dtype=bool);overhang_regions={}
for name,region in regions.items():
    selected=mask&region&~classified;classified|=selected
    overhang_regions[name]=dict(triangles=int(selected.sum()),area_mm2=float(mesh.area_faces[selected].sum()))
rest=mask&~classified;overhang_regions['arch_soffit_cap_and_other_structure']=dict(triangles=int(rest.sum()),area_mm2=float(mesh.area_faces[rest].sum()))
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']]
airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=raw_hash,method='Raw binary STL exact-coordinate weld only; actual mesh intersection crops, unrounded horizontal sections, even-odd nesting, exact -0.4 mm Shapely erosion on each positive component. No healing and no thin exemption.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),air_volume_mismatches=sum(not t['air_volume_is_zero'] for t in tests if t['expected']=='air'),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),failed_0_8mm_components=sum(r['failed_0_8mm'] for r in solidrows),downward_faces_over_45deg_above_base=int(mask.sum()),downward_area_mm2=float(mesh.area_faces[mask].sum()),overhang_regions=overhang_regions,pier_depth_mm=22,spandrel_depth_mm=11.6,front_direction='negative Y',rear_blank_volume_verified=True,thin_warning='Raised glyph serifs, exposed arch-band projection, seal rings and near-tangent tapered cap slices can fall below 0.8 mm. Exposed-only crops are identified and must not be mistaken for whole backed-wall thickness. Global connected-section erosion can hide narrow attached details. All failures retained.',actual_print_tested=False,support_free_certified=False,limitations='The wide arch soffit, mouldings, upper cap, plaque bevel and glyph/round-seal undersides require slicer support/orientation review. These bounded samples are not an exhaustive normal wall-thickness, strength, extrusion-width, bridging, FFF, or physical-print simulation.')
assert raw_hash==hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'STL changed during audit'
(A/'qa/local-features.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:q for k,q in report.items() if k!='tests'},ensure_ascii=False,indent=2))
assert report['occupancy_mismatches']==0,'Actual crop occupancy differs from stated expectation; diagnose, do not heal mesh'
assert report['air_volume_mismatches']==0,'An expected air volume contains geometry'
assert all(r['valid'] for t in tests for r in t['rows']),'Invalid local section'
