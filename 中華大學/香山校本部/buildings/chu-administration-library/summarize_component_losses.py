from pathlib import Path
import json,hashlib,csv,collections
R=Path(__file__).resolve().parent;j=json.loads((R/'layer-component-check.json').read_text());rows=[];families=collections.defaultdict(list)
for a in j['original_component_checks']:
 if a['opening_loss_fraction']<=.01:continue
 b=a['bounds_xy_mm'];family='four_roof_corner_piers' if max(abs(b[0]),abs(b[2]))>50 and max(abs(b[1]),abs(b[3]))>28 else 'four_open_arch_ears'
 x=dict(family=family,z_mm=a['z_mm'],original_component_index=a['original_component_index'],bounds_xy_mm=b,original_area_mm2=a['original_area_mm2'],original_span_mm=a['span_xy_mm'],opening_loss_fraction=a['opening_loss_fraction'],loss_outside_fixed_0_6_corner_regions_mm2=a['loss_outside_corner_regions_mm2'],loss_outside_adaptive_corner_regions_mm2=a['loss_outside_adaptive_corner_regions_mm2'],adaptive_radius_max_mm=a['maximum_adaptive_radius_mm'],rectangle_symmetric_difference_mm2=a['original_rectangle_symmetric_difference_mm2'],numeric_boundary_band_evidence=a['numeric_buffer_edge_residual_within_0_005mm_of_original_boundary'],original_local_proof_passed=a['over_one_percent_local_shape_proof']);rows.append(x);families[family].append(x)
with (R/'component-loss-over-one-percent.csv').open('w')as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
s=[dict(family=k,physical_feature_count=4,original_polygon_samples=len(v),max_loss=max(x['opening_loss_fraction']for x in v),min_original_bbox_span_mm=min(min(x['original_span_mm'])for x in v),unresolved_original_local_proof_samples=sum(not x['original_local_proof_passed']for x in v))for k,v in families.items()]
(R/'component-loss-summary.json').write_text(json.dumps(dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),original_polygon_count=len(j['original_component_checks']),high_loss_samples=len(rows),families=s,passed=all(x['original_local_proof_passed']for x in rows),checks={'all_original_polygon_erosion_and_opening_nonempty_single':j['checks']['all_original_components_survive_0_8mm_opening'] and j['checks']['no_original_component_splits_after_erosion_or_opening'],'all_local_loss_proofs_pass':all(x['original_local_proof_passed']for x in rows)},note='Samples include repeated heights and paired ear legs; not physical feature count. Original polygons and losses remain unchanged; unresolved local evidence is not automatically waived.'),indent=2))
print(s)

raise SystemExit(0 if all(x["original_local_proof_passed"] for x in rows) else 1)
