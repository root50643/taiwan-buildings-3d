"""Fail-closed gate: live evidence bindings plus exact frozen file-set verification.
Default mode only reads the sealed package. --preflight is an explicit authoring
mode used before sealing, and does not claim that an immutable package was checked.
"""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
import argparse,json,gzip,csv,io
from integrity_utils import sha,read,require,files,source_inventory,DERIVED
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--preflight',action='store_true');ap.add_argument('--expected-manifest-sha256');ap.add_argument('--check-inventory',action='store_true',help='Also check the provisional inventory in explicit author preflight mode');args=ap.parse_args()
checks={}
def check(name,value):checks[name]=bool(value)
def bind_detail(report,key,hashkey):
 return sha(R/report[key])==report[hashkey]
try:
 expected=sha(R/'model.stl')
 names=['raw-mesh-check.json','component-detail.json','negative-controls.json','scene-check.json','reproducibility.json','artifact-integrity.json','fixed-roots.json','root-intervals.json']
 reports={n:read(R/n) for n in names}
 strict=read(R/'dense-short-chords.json')
 source_deps={'raw-mesh-check.json': ['check_raw_mesh.py'], 'component-detail.json': ['check_component_detail.py'], 'negative-controls.json': ['check_negative_controls.py', 'check_raw_mesh.py', 'check_component_detail.py', 'build_model.py', 'parameters.json'], 'scene-check.json': ['probe_scene.py'], 'reproducibility.json': ['check_reproducibility.py', 'build_model.py', 'parameters.json', 'render_preview.py', 'probe_scene.py'], 'dense-short-chords.json': ['check_dense_surface.py', 'dense_original.cpp', 'original_rays.py'], 'fixed-roots.json': ['check_fixed_roots.py', 'root_rules.py', 'original_rays.py'], 'root-intervals.json': ['check_root_intervals.py', 'root_rules.py', 'all_boundary_screen.cpp', 'winding_parallel.cpp', 'original_rays.py'], 'artifact-integrity.json': ['check_artifacts.py', 'integrity_utils.py']}
 all_reports={**reports,'dense-short-chords.json':strict}
 check('every_report_generator_source_is_current',all(all_reports[n]['evidence_sources']=={p:sha(R/p) for p in dep} for n,dep in source_deps.items()))
 check('all_evidence_bound_to_current_stl',all(q['stl_sha256']==expected for q in reports.values()) and strict['stl_sha256']==expected)
 check('all_bounded_evidence_checks_true',all(q['passed'] is True and all(v is True for v in q['checks'].values()) for q in reports.values()))
 check('strict_original_diagnostic_stays_false',strict['passed'] is False and strict['checks']['all_first_chords_ge_0p8mm'] is False and strict['under_0p8mm_count']==1430 and strict['samples']==41580)
 check('strict_other_controls_pass',all(v is True for k,v in strict['checks'].items() if k!='all_first_chords_ge_0p8mm'))
 check('raw_short_detail_hash',bind_detail(strict,'short_chords_file','short_chords_sha256'))
 raw_csv=gzip.open(R/'dense-original.csv.gz','rb').read()
 import hashlib
 check('all_original_csv_bytes_preserved',hashlib.sha256(raw_csv).hexdigest()==strict['uncompressed_csv_sha256'])
 short=json.load(gzip.open(R/'dense-short-samples.json.gz','rt'));fixed=json.load(gzip.open(R/'fixed-root-samples.json.gz','rt'))
 ids=lambda rows:[(q['original_triangle_index'],q['sample_index']) for q in rows]
 rawids=ids(short);fixedids=ids([q['original'] for q in fixed]);csvrows=list(csv.DictReader(io.StringIO(raw_csv.decode())))
 expectedids={(int(q['face']),int(q['sample'])) for q in csvrows if float(q['first_solid'])<.8}
 check('all_short_points_retained_once',len(rawids)==len(set(rawids))==len(fixedids)==len(set(fixedids))==1430 and set(rawids)==set(fixedids)==expectedids)
 check('original_data_in_root_rows_unchanged',{k:q for k,q in zip(rawids,short)}=={k:q['original'] for k,q in zip(fixedids,fixed)})
 roots=reports['fixed-roots.json'];interval=reports['root-intervals.json']
 check('fixed_roots_bind_raw_details',roots['raw_short_detail_sha256']==sha(R/'dense-short-samples.json.gz') and roots['raw_csv_uncompressed_sha256']==strict['uncompressed_csv_sha256'])
 check('fixed_root_detail_current',bind_detail(roots,'detail_file','detail_sha256'))
 check('interval_detail_current',bind_detail(interval,'detail_file','detail_sha256') and interval['source_detail_sha256']==sha(R/'fixed-root-samples.json.gz'))
 check('no_root_sample_waiver',roots['original_sample_count']==1430 and not roots['unclassified'] and not roots['failed'] and roots['original_strict_passed'] is False and interval['original_strict_passed'] is False and interval['sampled_short_points']==1430 and interval['complete_queries']==7150 and interval['boundary_overlap_count']==0 and not interval['failed_controls'])
 layer=reports['component-detail.json'];check('layer_detail_current',bind_detail(layer,'detail_file','detail_sha256') and layer['maximum_individual_polygon_loss_fraction']<=.01 and layer['sampled_layers']==156)
 scene=reports['scene-check.json'];check('saved_blend_current',scene['blend_sha256']==sha(R/'scene.blend'))
 repro=reports['reproducibility.json'];check('replay_sources_current',repro['source_sha256']==sha(R/'build_model.py') and repro['parameters_sha256']==sha(R/'parameters.json') and repro['render_script_sha256']==sha(R/'render_preview.py'))
 check('all_current_png_bytes_replayed',repro['render_replayed'] is True and len(repro['previews'])==6 and all(q['identical'] is True and q['sha256']==sha(R/q['path']) for q in repro['previews']) and {q['path'] for q in repro['previews']}=={p.relative_to(R).as_posix() for p in (R/'previews').glob('*.png')})
 check('all_checker_and_helper_sources_bound',read(R/'source-bindings.json')['files']==source_inventory(R))
 artifact=reports['artifact-integrity.json'];check('privacy_scan_covers_actual_payload',artifact['scanned_files']==files(R,DERIVED))
 check('privacy_png_hashes_current',len(artifact['pngs'])==6 and all(q['sha256']==sha(R/q['path']) for q in artifact['pngs']))
 if (R/'gate-negative-controls.json').exists():
  required_controls={'missing_gate_controls', 'blender_identity_failure', 'changed_preview', 'fixed_root_modified', 'raw_short_omitted', 'stale_checker_reseal', 'nested_manifest', 'private_readme_path', 'optimized_zero_normal', 'raw_short_omitted_rehash_direct_checker', 'fixed_root_modified_rehash_direct_checker', 'missing_payload', 'extra_payload', 'optimized_thin_root', 'raw_short_modified_rehash_direct_checker', 'noop_checker', 'nested_sums', 'raw_short_modified', 'nested_privacy_report'}
  controls=read(R/'gate-negative-controls.json');check('adversarial_gate_and_optimized_checks_passed',controls['passed'] is True and set(controls['checks'])==required_controls and controls['unmodified_baseline_passed'] is True and controls['stl_sha256']==expected and controls['source_files']==source_inventory(R) and all(v is True for v in controls['checks'].values()))
 else:
  check('gate_negative_controls_present_or_author_preflight',args.preflight)
 if not args.preflight or args.check_inventory:
  manifest=read(R/'freeze-manifest.json');listed={q['path']:{'sha256':q['sha256'],'bytes':q['bytes']} for q in manifest['payload_files']}
  check('manifest_has_unique_safe_relative_paths',len(listed)==len(manifest['payload_files']) and all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in listed))
  check('exact_frozen_file_set_and_bytes',listed==files(R,{'freeze-manifest.json','SHA256SUMS'}))
  check('manifest_current_stl',manifest['stl_sha256']==expected)
  if args.expected_manifest_sha256:check('externally_pinned_manifest',sha(R/'freeze-manifest.json')==args.expected_manifest_sha256)
  lines=(R/'SHA256SUMS').read_text().splitlines();sums={line.split('  ',1)[1]:line.split('  ',1)[0] for line in lines}
  current=files(R,{'SHA256SUMS'});check('sha_file_exact_inventory',len(sums)==len(lines) and set(sums)==set(current) and all(sums[n]==q['sha256'] for n,q in current.items()))
 out={'passed':all(checks.values()),'mode':'author_preflight_not_frozen' if args.preflight else 'frozen_full_inventory','stl_sha256':expected,'checks':checks,'strict_original_normal_passed':False,
      'limits':'A bounded backed-relief finding does not turn short original normal chords into 0.8 mm walls. Not all-direction thickness proof or a physical print test.'}
except Exception as exc:
 out={'passed':False,'mode':'author_preflight_not_frozen' if args.preflight else 'frozen_full_inventory','checks':checks,'error':type(exc).__name__+': '+str(exc)}
print(json.dumps(out,ensure_ascii=False,indent=2));raise SystemExit(0 if out['passed'] else 1)
