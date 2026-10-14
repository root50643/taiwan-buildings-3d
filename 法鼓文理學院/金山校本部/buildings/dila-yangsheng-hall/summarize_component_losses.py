"""Classify the unchanged original Polygon opening results; never substitute a rectangle."""
from pathlib import Path
import json,csv,hashlib,collections
R=Path(__file__).resolve().parent;j=json.loads((R/'layer-component-check.json').read_text());r=[a for a in j['original_component_checks'] if a['opening_loss_fraction']>.01];groups=collections.defaultdict(list)
def classify(a):
 x0,y0,x1,y1=a['bounds_xy_mm']
 if x0>40:return '東橋端列印支根','bridge_stub_root_997'
 if x0< -30:return '南下段擋牆斜頂有限端截面','sloped_flank_finite_cap_212'
 if x0< -20:return '南上段擋牆斜頂有限端截面','sloped_flank_finite_cap_292'
 if y0>60:return '北橋端列印支根','bridge_stub_root_780'
 if y0< -52:return '南大框內退欄杆中央柱','south_post_width_13'
 if y0<0:return '長棟南下三層角墩','south_lower_corner_pier'
 if x0<14:return '長棟西北屋簷轉角','north_west_roof_corner'
 return '長棟西北端跨間角墩','corridor_pier_0_395'
for a in r:
 name,ray=classify(a);a['identified_feature']=name;a['ray_control_family']=ray;groups[name].append(a)
fields=['identified_feature','ray_control_family','z_mm','original_component_index','bounds_xy_mm','span_xy_mm','original_area_mm2','eroded_area_mm2','opened_area_mm2','lost_area_mm2','opening_loss_fraction','loss_outside_adaptive_corner_regions_mm2','original_rectangle_symmetric_difference_mm2','analytic_rectangle_min_width_mm','numeric_buffer_edge_residual_within_0_005mm_of_original_boundary','eroded_components','opened_components']
with (R/'component-loss-over-one-percent.csv').open('w') as f:
 w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(r)
s=[]
for name,g in groups.items():
 s.append(dict(feature=name,samples=len(g),height_range_mm=[min(a['z_mm'] for a in g),max(a['z_mm'] for a in g)],xy_bounds_variants=len({tuple(a['bounds_xy_mm']) for a in g}),minimum_original_short_side_mm=min(a['analytic_rectangle_min_width_mm'] for a in g),max_original_opening_loss_fraction=max(a['opening_loss_fraction'] for a in g),max_loss_outside_adaptive_corners_mm2=max(a['loss_outside_adaptive_corner_regions_mm2'] for a in g),numeric_fringe_samples=sum(a['loss_outside_adaptive_corner_regions_mm2']>=1e-8 for a in g),all_original_polygon_exact_rectangle=all(a['original_rectangle_symmetric_difference_mm2']<1e-10 for a in g),ray_control_family=g[0]['ray_control_family']))
checks={'all_351_original_results_retained':len(r)==351,'all_original_component_results_nonempty_single':all(a['eroded_components']==a['opened_components']==1 for a in r),'all_original_short_sides_above_reference':all(a['analytic_rectangle_min_width_mm']>=.8 for a in r),'every_over_one_percent_component_is_original_rectangle':all(a['original_rectangle_symmetric_difference_mm2']<1e-10 for a in r),'all_numeric_fringe_samples_proven':all(a['numeric_buffer_edge_residual_within_0_005mm_of_original_boundary'] for a in r if a['loss_outside_adaptive_corner_regions_mm2']>=1e-8)}
assert all(checks.values())
(R/'component-loss-summary.json').write_text(json.dumps(dict(passed=True,checks=checks,stl_sha256=j['stl_sha256'],samples=len(r),physical_feature_families=len(s),groups=s,method='Original Polygon results, WKT, losses and counts stay unchanged in layer-component-check.json. Exact rectangle identity is proved by symmetric-difference area, not replacement. All original short sides exceed 0.8 mm and original eroded/opened polygons survive individually. Repeated layers of the same feature are separate samples, not separate 351 built parts. Numeric straight-edge residues are independently bounded within 0.005 mm of original boundary; no thin strip is excused.'),ensure_ascii=False,indent=2));print('PASS loss families',len(s))
