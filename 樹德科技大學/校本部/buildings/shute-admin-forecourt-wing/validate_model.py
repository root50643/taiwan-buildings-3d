"""v3 replacement evidence gate. Does not erase the strict diagnostic failures.
All numerical geometry entrypoints and C++ helpers were recovered byte-identically.
This new aggregation gate requires independent review before release.
"""
from pathlib import Path
import csv, gzip, hashlib, json

R = Path(__file__).resolve().parent
EXPECTED = '7e9fdb8a610f566d7f22e06d07545f12d2e761ae16f5b660f8e2f5d52cb5388d'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def reject_constant(value):
    raise ValueError('Nonfinite JSON constant: ' + value)
def read(name):
    if name.endswith('.gz'):
        with gzip.open(R / name, 'rt') as f:
            return json.load(f, parse_constant=reject_constant)
    return json.loads((R / name).read_text(), parse_constant=reject_constant)
def all_true(mapping):
    return bool(mapping) and all(value is True for value in mapping.values())

reports = {name: read(name) for name in [
    'raw-mesh-check.json', 'component-detail.json', 'negative-controls.json',
    'dense-short-chords.json', 'drum-relief-roots.json', 'drum-root-intervals.json',
    'boundary-witnesses.json.gz', 'flag-boundary-classification.json', 'reproducibility.json',
]}
raw = reports['raw-mesh-check.json']
comp = reports['component-detail.json']
dense = reports['dense-short-chords.json']
root = reports['drum-relief-roots.json']
interval = reports['drum-root-intervals.json']
boundary = reports['boundary-witnesses.json.gz']
flags = reports['flag-boundary-classification.json']
repro = reports['reproducibility.json']
shorts = read('dense-short-samples.json.gz')
roots = read('drum-relief-root-samples.json.gz')
root_details = read('drum-root-interval-details.json.gz')
identity = lambda q: (q['original_triangle_index'], q['sample_index'])
short_keys = [identity(q) for q in shorts]
root_keys = [identity(q) for q in roots]
with gzip.open(R / 'dense-original.csv.gz', 'rb') as f:
    original_csv_hash = hashlib.sha256(f.read()).hexdigest()
with gzip.open(R / 'dense-original.csv.gz', 'rt') as f:
    original_rows = list(csv.DictReader(f))

checks = {
    'exact_approved_stl_preserved': sha(R / 'model.stl') == EXPECTED,
    'every_report_bound_to_actual_stl': all(r['stl_sha256'] == EXPECTED for r in reports.values()),
    'raw_original_mesh_all_checks': raw['passed'] is True and all_true(raw['checks']) and raw['triangles'] == 5734,
    'all_520_unrounded_sections_and_original_polygons_pass': comp['passed'] is True and all_true(comp['checks']) and comp['sampled_layers'] == 520 and comp['maximum_individual_polygon_loss_fraction'] <= .01,
    'negative_controls_reject_real_failures': reports['negative-controls.json']['passed'] is True and all_true(reports['negative-controls.json']['checks']),
    'strict_false_and_all_original_samples_preserved': dense['passed'] is False and dense['checks']['all_first_chords_ge_0p8mm'] is False and dense['checks']['all_fixed_direction_parity_codes_expected'] is False and dense['samples'] == len(original_rows) == 57340 and dense['under_0p8mm_count'] == len(shorts) == 1977 and len(dense['flags']) == 3,
    'regenerated_raw_numeric_rows_identical_to_v2': original_csv_hash == dense['uncompressed_csv_sha256'] == '90a2529dce035a518b380b19f362c4d73e6b5174ff53fa521a1fb7610a56d56d',
    'all_short_samples_uniquely_covered_by_fixed_roots': len(set(short_keys)) == len(short_keys) and sorted(short_keys) == sorted(root_keys) and len(set(root_keys)) == len(root_keys),
    'zero_unclassified_or_failed_roots': root['passed'] is True and all_true(root['checks']) and root['unclassified'] == [] and root['failed_samples'] == [] and root['assigned_count'] == 1977 and all(q['passed'] is True and all_true(q['checks']) for q in roots),
    'root_points_and_original_normals_preserved': all((s['surface_point_mm'], s['original_outward_normal']) == (r['surface_point_mm'], r['original_outward_normal']) for s, r in zip(shorts, roots)),
    'complete_root_and_next_intervals_have_no_boundary_overlap': interval['passed'] is True and all_true(interval['checks']) and interval['complete_root_and_next_boundary_overlap_count'] == 0 and root_details['overlaps'] == [] and len(root_details['queries']) == 1977,
    'all_full_root_winding_controls_pass': len(root_details['controls']) == interval['winding_controls'] == 11862 and all(c['passed'] is True and abs(c['winding'] - c['expected_winding']) < 1e-7 for c in root_details['controls']),
    'all_original_normals_screened_with_no_first_material_boundary': boundary['total_screened_dense_rays'] == 57340 and boundary['positive_length_first_segment_boundary_ray_count'] == 0,
    'five_after_boundary_rays_explicitly_retained': boundary['positive_length_after_interval_boundary_ray_count'] == len(boundary['rows']) == 5 and boundary['boundary_triangle_interval_count'] == 10 and boundary['control_count'] == 250,
    'all_boundary_material_air_and_finite_triangle_controls_pass': boundary['all_nonboundary_controls_passed'] is True and boundary['off_boundary_failed_controls'] == [] and all(r['all_nonboundary_controls_passed'] is True and r['all_boundary_station_barycentric_strictly_interior'] is True and all(abs(s['plane_distance_mm']) < 1e-10 for b in r['positive_length_boundary_intervals'] for s in b['station_geometry']) for r in boundary['rows']),
    'three_original_flags_have_exact_bounded_explanation': len(flags['rows']) == 3 and all_true(flags['checks']) and all(r['classification'] == 'positive_length_external_surface_boundary' and r['containing_original_triangle_intervals'] for r in flags['rows']),
    'stl_saved_blend_and_four_actual_stl_previews_reproduce': repro['passed'] is True and all_true(repro['checks']) and repro['blend_sha256'] == sha(R / 'scene.blend') and repro['build_script_sha256'] == sha(R / 'build_model.py') and repro['render_script_sha256'] == sha(R / 'render_preview.py') and len(repro['views']) == 4 and all(all_true(v['checks']) and v['sha256'] == sha(R / v['path']) for v in repro['views']),
}
source_provenance = read('validator-provenance.json')
checks['every_recovered_numerical_source_is_byte_identical'] = all(
    sha(R / q['path']) == q['recovered_doc_v2_sha256']
    for q in source_provenance['recovered_source_files']
) and len(source_provenance['recovered_source_files']) >= 15
for report, detail_key, hash_key in [
    (dense, 'short_chords_file', 'short_chords_sha256'),
    (root, 'samples_file', 'samples_sha256'),
    (interval, 'detail_file', 'detail_sha256'),
    (comp, 'detail_file', 'detail_sha256'),
]:
    checks['detail_binding_' + report[detail_key]] = sha(R / report[detail_key]) == report[hash_key]
out = {
    'revision': 'recovered-release-v3',
    'passed': all(checks.values()),
    'status': 'author_bounded_evidence_only_pending_new_independent_review',
    'stl_sha256': EXPECTED,
    'checks': checks,
    'reports': [{'path': n, 'sha256': sha(R / n)} for n in reports],
    'unresolved_unqualified_strict_diagnostics': {
        'original_short_count': 1977,
        'minimum_original_first_chord_mm': dense['minimum_first_chord_mm'],
        'original_fixed_parity_flag_count': 3,
        'strict_diagnostic_passed': False,
        'bounded_classes': ['source-bounded shallow drum relief with direct material roots', 'positive-length original exterior boundary intervals'],
        'does_not_establish_all_direction_minimum_wall_thickness': True,
    },
    'limits': 'A passing bounded evidence gate does not turn the original strict failures into passes, approve publication, certify all-direction wall thickness, or replace physical slicing and test printing. v3 renderer, scene and aggregation source require new independent review.',
}
(R / 'validation.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(out, ensure_ascii=False, indent=2))
assert out['passed'], [key for key, value in checks.items() if not value]
