#!/usr/bin/env python3
"""Source-specific whole-building footprint, octagon/circle and asymmetric facade tests."""
import argparse,pathlib,json,hashlib,math
import numpy as np,trimesh,manifold3d as mf
from shapely.geometry import Polygon,GeometryCollection,Point,box
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args();r=a.out
m=trimesh.load_mesh(r/'qihou-lighthouse-main-2020.stl',process=True);s=mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)))
def section(z):
 g=GeometryCollection()
 for v in s.slice(z).to_polygons():g=g.symmetric_difference(Polygon(v))
 return g
cy=97.3
p0=section(30);claims=[]
for name,xy,occupied in [('Whole left office wing',[-100,0],True),('Whole right exhibition wing',[100,0],True),('Actual connecting neck',[0,60],True),('Rear tower',[0,100],True),('Left open reentrant',[-60,75],False),('Right open reentrant',[60,75],False),('Separate precinct not included',[80,120],False)]:
 actual=p0.contains(Point(xy));assert actual==occupied,(name,actual);claims.append({'name':name,'xy_model_mm':xy,'expected_occupied':occupied,'actual_occupied':actual})
def octagon(flat):
 h=flat/2;k=h*(math.sqrt(2)-1)
 return Polygon([(-k,cy-h),(k,cy-h),(h,cy-k),(h,cy+k),(k,cy+h),(-k,cy+h),(-h,cy+k),(-h,cy-k)])
shape=[]
for label,z,flat in [('Eight-facet shaft',130,65.6),('Eight-sided balcony slab',150,110.6)]:
 actual=section(z);target=octagon(flat);delta=actual.symmetric_difference(target).area;assert delta<.01,(label,delta)
 shape.append({'name':label,'z_model_mm':z,'reference_across_flats_model_mm':flat,'symmetric_difference_area_mm2':delta})
actual=section(245);assert actual.geom_type=='Polygon' and len(actual.exterior.coords)>30,'Dome should be circular, not octagonal or square'
rad=np.linalg.norm(np.asarray(actual.exterior.coords)[:-1]-[0,cy],axis=1);assert rad.max()-rad.min()<.5
features=json.loads((r/'editable-parts.json').read_text())['features'];names=[x['name']for x in features]
assert sum(x.startswith('Wing SE window') and x.endswith('opaque inset glass')for x in names)==4
assert sum(x.startswith('Wing NW window') and x.endswith('opaque inset glass')for x in names)==4
assert 'SW opaque side doorway'in names and 'NE blind wall recessed-panel border'in names
assert not any('NE opaque side doorway'in x for x in names)
roof=section(90);assert not roof.contains(Point(70,0)),'Low roof must not become tall full-wing gable'
assert section(87).contains(Point(70,0));assert section(100).contains(Point(0,-56))
report={'all_pass':True,'stl_sha256':hashlib.sha256((r/'qihou-lighthouse-main-2020.stl').read_bytes()).hexdigest(),'footprint_checks':claims,'octagon_sections':shape,'circular_dome_section':{'z_model_mm':245,'vertex_count':len(actual.exterior.coords)-1,'radial_range_mm':[float(rad.min()),float(rad.max())]},'whole_wing_front_and_rear_four_windows_each':True,'sw_door_ne_blind_asymmetry':True,'low_flat_wing_roof_with_front_pediment_only':True,'whole_main_building_not_precinct':True,'geometry_is_approximate_not_survey':True}
(r/'qa/lighthouse-layout-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
