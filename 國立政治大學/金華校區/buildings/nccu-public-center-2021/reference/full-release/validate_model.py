"""Recalculate current content bindings and preserve strict geometric failures."""
from pathlib import Path
import argparse,gzip,hashlib,json,sys
from write_validation_manifest import inventory
from check_artifacts import inspect
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def validate(root):
    stl=sha(root/'model.stl');manifest=json.loads((root/'validation-inputs.json').read_text());current=inventory(root)
    changed=sorted(k for k in set(current)|set(manifest['files']) if current.get(k)!=manifest['files'].get(k))
    paths=['qa/raw/raw-mesh-check.json','qa/sections/section-check.json','qa/dense/dense-check.json','qa/controls/control-check.json','qa/qa-summary.json','architectural-features.json','scene-check.json','reproducibility.json','verification-gates.json']
    reports={n:json.loads((root/n).read_text()) for n in paths}
    raw=reports[paths[0]];section=reports[paths[1]];dense=reports[paths[2]];controls=reports[paths[3]];repro=reports['reproducibility.json']
    checkers={p.name:sha(p) for p in sorted((root/'verification').iterdir()) if p.suffix in ['.py','.cpp']}
    artifact_scan=inspect(root)
    checks={'exact_current_distributable_inventory':not changed,'fresh_privacy_scan':artifact_scan['passed'],
      'geometry_reports_bound_to_current_stl':all(reports[n].get('stl_sha256')==stl for n in [paths[0],paths[1],paths[2],paths[4],'architectural-features.json','scene-check.json','reproducibility.json','verification-gates.json']),
      'all_geometry_reports_bound_to_current_checkers':all(reports[n].get('checker_sources_sha256')==checkers for n in paths[:5]),
      'current_scene_container_hash':reports['scene-check.json'].get('blend_sha256')==sha(root/'scene.blend'),
      'all_isolated_replay_sources_current':all((root/n).is_file() and sha(root/n)==h for n,h in repro.get('copied_source_hashes',{}).items()),
      'all_seven_replayed_previews_current':len(repro.get('previews',[]))==7 and all(sha(root/q['path'])==q['sha256'] and q['identical'] is True for q in repro.get('previews',[])),
      'replay_included_render':repro.get('render_replayed') is True,
      'architecture_parameters_current':reports['architectural-features.json'].get('parameters_sha256')==sha(root/'parameters.json')}
    evidence=[]
    for key,rep,sub,hashkey in [('detail_file',section,'sections','detail_sha256'),('failure_file',section,'sections','failure_sha256'),('csv_file',dense,'dense','csv_gzip_sha256'),('short_chords_file',dense,'dense','short_chords_sha256'),('flagged_samples_file',dense,'dense','flagged_samples_sha256')]:
        p=root/'qa'/sub/rep[key];evidence.append(p.is_file() and sha(p)==rep[hashkey])
    checks['all_geometry_detail_hashes_current']=all(evidence)
    with gzip.open(root/'qa/dense'/dense['csv_file'],'rb') as f:checks['lossless_dense_csv_hash_current']=hashlib.file_digest(f,'sha256').hexdigest()==dense['uncompressed_csv_sha256']
    checks['control_detail_reports_current']=all((root/'qa/controls'/q['report_file']).is_file() and sha(root/'qa/controls'/q['report_file'])==q['report_sha256'] for q in controls['controls'])
    geometry={'raw_original_topology_passes':raw.get('strict_passed') is True,
      'maximum_original_extent_le_150mm':max(raw['extents_mm'])<=150.000001,
      'per_polygon_three_offset_sections_pass':section.get('strict_passed') is True and section.get('offsets_from_z_min_mm')==[.031,.071,.137] and section.get('pitch_mm')==.2,
      'every_original_face_has_ten_rays':dense.get('samples')==10*raw.get('triangles',-1),
      'no_short_original_chords':dense.get('under_0p8mm_count')==0 and dense.get('minimum_first_chord_mm',0)>=.8,
      'no_dense_ambiguity_flags':dense.get('flagged_sample_count')==0,
      'strict_dense_original_ray_check':dense.get('strict_passed') is True,
      'all_synthetic_controls_pass':controls.get('strict_passed') is True and controls.get('control_runs')==30,
      'source_critical_features_retained':reports['architectural-features.json'].get('passed') is True,
      'saved_original_oriented_faces_exact':reports['scene-check.json'].get('passed') is True,
      'full_isolated_replay_pass':repro.get('passed') is True,
      'blender_exit_control_pass':reports['verification-gates.json'].get('passed') is True}
    intersections=json.loads((root/'qa/intersections/original-intersections.json').read_text())
    ic=json.loads((root/'qa/intersection-controls/controls-summary.json').read_text())
    contacts=intersections.get('all_actual_intersections',{})
    checks['exact_intersection_evidence_current']=intersections.get('stl_sha256')==stl and intersections.get('tools',{}).get('source_sha256')==sha(root/'check_original_intersections.py') and sha(root/'qa/intersections'/contacts['path'])==contacts['sha256']
    checks['intersection_controls_sources_current']=ic.get('checker_sha256')==sha(root/'check_original_intersections.py') and ic.get('controls_source_sha256')==sha(root/'check_intersection_controls.py')
    checks['intersection_control_reports_current']=all(sha(root/'qa/intersection-controls'/q['report'])==q['report_sha256'] for q in ic['subprocess_executions'])
    geometry['all_exact_original_face_intersections_valid']=intersections.get('strict_passed') is True and intersections.get('bad_pair_count')==0 and intersections.get('broad_phase',{}).get('all_bbox_overlapping_pairs_completed') is True
    geometry['intersection_negative_controls_pass']=ic.get('passed') is True and ic.get('subprocess_execution_count',0)>=48
    aggregate=json.loads((root/'aggregate-controls.json').read_text()) if (root/'aggregate-controls.json').is_file() else {}
    geometry['aggregate_negative_controls_pass']=aggregate.get('passed') is True and aggregate.get('stl_sha256')==stl and all(q.get('rejected') is True for q in aggregate.get('controls',[])) and len(aggregate.get('controls',[]))>=9
    geometry['aggregate_control_sources_current']=aggregate.get('checker_sources_sha256')=={n:sha(root/n) for n in ['check_aggregate_controls.py','validate_model.py','check_artifacts.py','write_validation_manifest.py']}
    geometry['aggregate_control_evidence_current']=(root/'aggregate-control-evidence.json').is_file() and sha(root/'aggregate-control-evidence.json')==aggregate.get('evidence_sha256')
    boundary=json.loads((root/'qa/boundaries/ray-boundary-evidence.json').read_text())
    roots=json.loads((root/'qa/boundaries/previous-short-root-evidence.json').read_text())
    checks['four_original_flag_diagnostic_current']=boundary.get('stl_sha256')==stl and boundary.get('checker_sha256')==sha(root/'diagnose_boundaries.py') and boundary.get('flags_sha256')==sha(root/'qa/dense'/dense['flagged_samples_file'])
    checks['previous_short_root_diagnostic_current']=roots.get('new_stl_sha256')==stl and roots.get('checker_sha256')==sha(root/'check_root_repairs.py') and roots.get('fixtures_sha256')==sha(root/'root-repair-fixtures.json')
    geometry['four_original_flags_fully_diagnosed_without_strict_override']=boundary.get('diagnostic_passed') is True and boundary.get('original_strict_passed') is False and boundary.get('production_acceptance_unchanged') is True and boundary.get('flagged_original_rays')==4 and len(boundary.get('cases',[]))==4 and all(boundary.get('diagnostic_checks',{}).values())
    geometry['previous_short_roots_physically_repaired']=roots.get('all_20_previous_lines_checked') is True and roots.get('all_previous_roots_now_ge_0p8mm') is True and roots.get('minimum_new_root_length_mm',0)>=.8 and roots.get('production_strict_unchanged') is True
    passed=all(checks.values()) and all(geometry.values())
    return {'passed':passed,'strict_passed':passed,'integrity_passed':all(checks.values()),'checks':checks,'artifact_scan':artifact_scan,'geometry_checks':geometry,'current_inventory_changed_paths':changed,'stl_sha256':stl,'input_manifest_sha256':sha(root/'validation-inputs.json'),'dense_flagged_samples':dense.get('flagged_sample_count'),'limits':'Strict finite checks only. Boundary diagnoses do not silently clear flags. Independent acceptance, survey accuracy, slicer toolpaths and physical test printing are separate.'}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--integrity-only',action='store_true',help='Only for stale-evidence negative controls; never means printable approval.');a=ap.parse_args()
    try:out=validate(R)
    except Exception as e:out={'passed':False,'strict_passed':False,'integrity_passed':False,'checks':{'completed':False},'error':str(e),'error_type':type(e).__name__}
    (R/'validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));raise SystemExit(0 if out['integrity_passed' if a.integrity_only else 'strict_passed'] else 1)
