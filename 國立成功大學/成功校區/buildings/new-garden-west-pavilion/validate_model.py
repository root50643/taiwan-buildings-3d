"""Re-read current files and re-run privacy scanning before aggregating evidence.
No mesh repair. Every failed condition explicitly causes nonzero process exit.
"""
from pathlib import Path
import gzip,hashlib,json,subprocess,sys
from write_validation_manifest import inventory
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected=sha(R/'model.stl')
# Fresh scanner, never only a prior passed flag. The scanner itself is hashed.
p=subprocess.run([sys.executable,str(R/'check_artifacts.py')],capture_output=True,text=True)
if p.returncode!=0:
    print(p.stdout+p.stderr);raise SystemExit(p.returncode)
names=['raw-mesh-check.json','architectural-features.json','component-detail.json','dense-short-chords.json',
       'negative-controls.json','verification-gates.json','scene-check.json',
       'reproducibility.json','artifact-integrity.json']
reports={n:json.loads((R/n).read_text()) for n in names}
manifest=json.loads((R/'validation-inputs.json').read_text())
rep=reports['reproducibility.json'];dense=reports['dense-short-chords.json']
raw=reports['raw-mesh-check.json'];comp=reports['component-detail.json']
current=inventory(R)
checks={
 'exact_current_distributable_inventory':current==manifest['files'],
 'all_reports_bound_to_current_stl':all(r['stl_sha256']==expected for r in reports.values()),
 'all_reports_explicitly_pass':all(r['passed'] is True for r in reports.values()),
 'all_report_check_flags_true':all(all(v is True for v in r['checks'].values()) for r in reports.values()),
 'raw_original_triangles_pass':raw['passed'] is True,
 'maximum_per_polygon_opening_loss_le_one_percent':comp['maximum_individual_polygon_loss_fraction']<=.01,
 'layer_detail_hash_current':comp['detail_sha256']==sha(R/comp['detail_file']),
 'dense_every_face_ten_samples':dense['samples']==10*raw['triangles'],
 'dense_no_short_chords_or_parity_flags':dense['under_0p8mm_count']==0 and not dense['flags'],
 'dense_minimum_ge_0p8mm':dense['minimum_first_chord_mm']>=.8,
 'dense_csv_hash_current':hashlib.sha256(gzip.decompress((R/'dense-original.csv.gz').read_bytes())).hexdigest()==dense['uncompressed_csv_sha256'],
 'dense_short_report_hash_current':sha(R/dense['short_chords_file'])==dense['short_chords_sha256'],
 'saved_scene_hash_current':reports['scene-check.json']['blend_sha256']==sha(R/'scene.blend'),
 'build_and_parameters_current':rep['source_sha256']==sha(R/'build_model.py') and rep['parameters_sha256']==sha(R/'parameters.json'),
 'renderer_current':rep['render_script_sha256']==sha(R/'render_preview.py'),
 'all_replayed_source_hashes_current':all(sha(R/n)==h for n,h in rep['copied_source_hashes'].items()),
 'isolated_full_replay_passes':rep['passed'] is True and rep['render_replayed'] is True,
 'six_current_previews_match_replay':len(rep['previews'])==6 and all(q['sha256']==sha(R/q['path']) for q in rep['previews']),
 'fresh_distribution_privacy_scan':reports['artifact-integrity.json']['passed'] is True,
 'optimized_python_and_blender_error_controls_pass':reports['verification-gates.json']['passed'] is True,
}
changed=sorted(k for k in set(current)|set(manifest['files']) if current.get(k)!=manifest['files'].get(k))
out={'passed':all(checks.values()),'checks':checks,'stl_sha256':expected,
     'current_inventory_changed_paths':changed,
     'current_input_manifest_sha256':sha(R/'validation-inputs.json'),
     'reports':[{'path':n,'sha256':sha(R/n)} for n in names],
     'limits':'Author finite numerical evidence. Independent review is separate. Not a global all-direction wall-thickness proof, slicer toolpath or physical test print.'}
(R/'validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if not out['passed']:raise SystemExit(1)
