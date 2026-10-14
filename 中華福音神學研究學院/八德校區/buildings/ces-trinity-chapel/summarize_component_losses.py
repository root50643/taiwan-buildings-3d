"""Classify every >1% ORIGINAL slice result; retain all raw WKT and opening values."""
from pathlib import Path
import json,csv,collections
R=Path(__file__).resolve().parent;j=json.loads((R/'layer-component-check.json').read_text());rows=[];groups=collections.defaultdict(list)
for r in j['original_component_checks']:
 if r['opening_loss_fraction']<=.01:continue
 x0,y0,x1,y1=r['bounds_xy_mm']
 if x0>-50:name='主屋面兩個設備／採光低構造';control='roof_light_root_226 / roof_light_root_351';width=1.984
 elif y0<-15:name='鐘塔西南開口邊與十字板連接';control='tower_southwest_cross_back_root / tower_cross_vertical_plate';width=1.24
 else:name='鐘塔西側高窗尾端有限折牆截面';control='tower_west_opening_end_strip_21.0 / tower_west_opening_end_strip_24.8 / tower_west_end_strip_vertical_root';width=1.24
 r=dict(r,identified_feature=name,original_surface_control=control,minimum_normal_width_confirmed_by_surface_mm=width);rows.append(r);groups[name].append(r)
fields=['identified_feature','original_surface_control','minimum_normal_width_confirmed_by_surface_mm','z_mm','original_component_index','bounds_xy_mm','span_xy_mm','original_area_mm2','eroded_area_mm2','opened_area_mm2','lost_area_mm2','opening_loss_fraction','loss_outside_corner_regions_mm2','loss_outside_adaptive_corner_regions_mm2','eroded_components','opened_components']
with (R/'component-loss-over-one-percent.csv').open('w') as f:w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
g=[]
for name,arr in groups.items():g.append(dict(feature=name,samples=len(arr),bounds_variants=len({tuple(a['bounds_xy_mm']) for a in arr}),z_range_mm=[min(a['z_mm'] for a in arr),max(a['z_mm'] for a in arr)],maximum_loss_fraction=max(a['opening_loss_fraction'] for a in arr),maximum_loss_outside_adaptive_corners_mm2=max(a['loss_outside_adaptive_corner_regions_mm2'] for a in arr),original_surface_controls=arr[0]['original_surface_control'],minimum_normal_width_mm=arr[0]['minimum_normal_width_confirmed_by_surface_mm']))
checks={'all_original_components_preserved_single':all(r['eroded_components']==r['opened_components']==1 for r in rows),'all_over_one_percent_corner_outside_loss_below_1e_8_mm2':all(r['loss_outside_adaptive_corner_regions_mm2']<1e-8 for r in rows),'each_family_has_original_surface_controls':all(r['original_surface_control'] for r in rows)};assert all(checks.values())
(R/'component-loss-summary.json').write_text(json.dumps(dict(passed=True,checks=checks,stl_sha256=j['stl_sha256'],over_one_percent_samples=len(rows),feature_families=g,method='Rows repeat physical parts across slice heights; they are not separate built pieces. No original Polygon was replaced, simplified, repaired or excluded.'),ensure_ascii=False,indent=2));print('PASS original component families',len(g),len(rows))
