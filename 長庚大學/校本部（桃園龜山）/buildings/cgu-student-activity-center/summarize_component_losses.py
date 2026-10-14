"""Identify each high-loss original Polygon; retain its original WKT in the source report."""
from pathlib import Path
import json,csv,collections,hashlib
R=Path(__file__).resolve().parent
r=json.loads((R/'layer-component-check.json').read_text());rows=[];groups=collections.defaultdict(list)
for a in r['original_component_checks']:
 if a['opening_loss_fraction']<=.01:continue
 x0,y0,x1,y1=a['bounds_xy_mm'];z=a['z_mm']
 if y0>70: family='stage_four_posts';identity=str(round((x0+x1)/2,3));physical_count=4
 elif x0>30: family='low_gallery_posts';identity=str(round((y0+y1)/2,3));physical_count=9
 elif x0<0: family='ridge_cover_upper_lips';identity=str(round((y0+y1)/2,3));physical_count=15
 elif z>=41:family='lantern_tapered_cap';identity='one_cap_varying_sections';physical_count=1
 elif z>=38:family='lantern_four_corner_posts';identity=str((round(x0,2),round(y0,2)));physical_count=4
 else:family='backed_X_tower_combined_body';identity='one_union_body_multiple_levels';physical_count=1
 row=dict(family=family,physical_feature_id=identity,physical_features_in_family=physical_count,z_mm=z,component_index=a['original_component_index'],bounds_xy_mm=a['bounds_xy_mm'],span_xy_mm=a['span_xy_mm'],area_mm2=a['original_area_mm2'],loss_fraction=a['opening_loss_fraction'],loss_outside_corners_mm2=a['loss_outside_corner_regions_mm2'],original_rectangle_difference_mm2=a['original_rectangle_symmetric_difference_mm2'],numeric_fringe=a['numeric_buffer_edge_residual_within_0_005mm_of_original_boundary'],surviving_eroded_components=a['eroded_components'],surviving_opened_components=a['opened_components'])
 rows.append(row);groups[family].append(row)
summary=[]
for name,a in groups.items():
 summary.append(dict(family=name,original_polygon_samples=len(a),represented_feature_ids=len(set(x['physical_feature_id'] for x in a)),physical_features_in_family=a[0]['physical_features_in_family'],z_range_mm=[min(x['z_mm']for x in a),max(x['z_mm']for x in a)],maximum_loss_fraction=max(x['loss_fraction']for x in a),maximum_loss_outside_corners_mm2=max(x['loss_outside_corners_mm2']for x in a),minimum_original_bbox_span_mm=min(min(x['span_xy_mm'])for x in a),note='Sample count includes repeated heights; bbox span is not claimed as minimum normal wall thickness. Original WKT and individual erosion results remain in layer-component-check.json; actual-face roots separately verified.'))
with (R/'component-loss-over-one-percent.csv').open('w')as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
(R/'component-loss-summary.json').write_text(json.dumps(dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),checks={'all_original_components_survive':r['checks']['all_original_components_survive_0_8mm_opening'],'all_losses_within_corner_regions':all(x['loss_outside_corners_mm2']<.0002 for x in rows)},original_polygon_samples=len(r['original_component_checks']),high_loss_samples=len(rows),families=summary,passed=all(x['loss_outside_corners_mm2']<.0002 and x['surviving_eroded_components']==x['surviving_opened_components']==1 for x in rows),note='Corner-loss identification is evidence for independent review, not a waived printability guarantee.'),indent=2))
print(summary)
