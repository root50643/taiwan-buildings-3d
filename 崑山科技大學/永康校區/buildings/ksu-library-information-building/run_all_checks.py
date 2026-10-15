"""Full author replay. Exit1 deliberately retains original diagnostic failures pending review."""
from pathlib import Path
import subprocess,json,sys,hashlib
R=Path(__file__).resolve().parent
steps=[('check_raw_mesh.py','raw-mesh-check.json'),('check_layer_components.py','layer-component-check.json'),('check_canonical_thin.py','canonical-script-check.json'),('validate_model.py','validation.json'),('check_preview_rebuild.py','preview-rebuild-check.json'),('check_readme_views.py','readme-view-check.json'),('inspect_backing.py','backing-root-check.json'),('check_root_sections.py','root-section-check.json'),('classify_components.py','component-loss-evidence.json'),('check_short_chord_roots.py','short-chord-root-evidence.json'),('check_dense_original_rays.py','dense-independent-root-evidence.json'),('check_dense_replay.py','dense-replay-check.json'),('check_adaptive_origins.py','adaptive-origin-evidence.json'),('check_all_boundaries.py','all-six-boundary-controls.json'),('check_corrected_roots.py','corrected-origin-root-check.json'),('check_surface_root_summary.py','surface-root-summary.json')]
runs=[]
for script,report in steps:
 p=subprocess.run([sys.executable,str(R/script)],cwd=R,capture_output=True,text=True)
 data=json.loads((R/report).read_text()) if (R/report).exists() else {}
 # Compute completion separately from the unchanged original diagnostic Boolean.
 completed=p.returncode==0
 runs.append({'script':script,'report':report,'exit_code':p.returncode,'completed':completed,'report_passed':data.get('passed')})
 print(script,p.returncode,data.get('passed'),flush=True)
 if not completed:print(p.stdout,p.stderr,flush=True)
summary=json.loads((R/'surface-root-summary.json').read_text())
checks={'all_replay_programs_completed':all(x['completed']for x in runs),'raw_mesh':json.loads((R/'raw-mesh-check.json').read_text())['passed'],'every_original_polygon_survives_unsplit':json.loads((R/'layer-component-check.json').read_text())['passed'],'source_blend_rebuild':json.loads((R/'validation.json').read_text())['passed'],'five_png_byte_replay':json.loads((R/'preview-rebuild-check.json').read_text())['passed'],'three_readme_rows':json.loads((R/'readme-view-check.json').read_text())['passed'],'all_dense_values_exact_replay':json.loads((R/'dense-replay-check.json').read_text())['passed'],'original_dense_diagnostic':summary['original_dense_diagnostic_passed']}
ready=all(v for k,v in checks.items()if k!='original_dense_diagnostic')and summary['ready_for_independent_review']
result={'passed':all(checks.values()),'ready_for_independent_review':ready,'exceptions_independently_approved':False,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'checks':checks,'runs':runs,'retained_exceptions':'830 original component opening-loss samples;12 original fixed-origin/boundary diagnostic samples. All original false values retained; independent approval pending.'};(R/'all-checks.json').write_text(json.dumps(result,indent=2));raise SystemExit(0 if result['passed']else 1)
