"""Run every original check. Preserve unresolved local-proof failures; never waive them."""
from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).resolve().parent
assert hashlib.sha256((R/'check_thin_features.py').read_bytes()).hexdigest()=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
rows=[]
for name in ['validate_model.py','check_raw_mesh.py','check_thin_features.py','check_all_layers.py','check_layer_components.py','check_recess_roots.py','summarize_component_losses.py','diagnose_rectangle_boundaries.py','check_readme_views.py','check_preview_rebuild.py']:
 p=subprocess.run([sys.executable,str(R/name)],capture_output=True,text=True);rows.append(dict(script=name,exit_code=p.returncode));print(name,p.returncode,flush=True)
 if p.returncode and name not in ['check_layer_components.py','summarize_component_losses.py']:raise RuntimeError(name+'\n'+p.stdout+'\n'+p.stderr)
a=json.loads((R/'layer-component-check.json').read_text());d=json.loads((R/'rectangle-boundary-diagnostics.json').read_text());hard=all(json.loads((R/n).read_text())['passed']for n in ['validation.json','raw-mesh-check.json','recess-root-check.json','readme-view-check.json','preview-framing-check.json','preview-rebuild-check.json']) and a['checks']['all_original_components_survive_0_8mm_opening'] and a['checks']['no_original_component_splits_after_erosion_or_opening']
unresolved=[x for x in a['original_component_checks']if x['opening_loss_fraction']>.01 and not x['over_one_percent_local_shape_proof']]
report=dict(passed=all(x['exit_code']==0 for x in rows),hard_geometry_checks_passed=hard,ready_for_independent_review=hard and len(unresolved)==len(d)==10,checks=dict(all_scripts_exit_zero=all(x['exit_code']==0 for x in rows),all_original_polygons_survive_and_do_not_split=a['checks']['all_original_components_survive_0_8mm_opening'] and a['checks']['no_original_component_splits_after_erosion_or_opening'],canonical_v3_sha_verified=True,all_original_local_loss_proofs_pass=a['checks']['all_over_one_percent_loss_within_quantified_corner_regions']),stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),runs=rows,unresolved_original_local_proof_samples=len(unresolved),note='Original local-proof failures are preserved. Author review freeze is not independent approval or a waiver of these ten original Polygon results.')
(R/'all-checks.json').write_text(json.dumps(report,indent=2));raise SystemExit(0 if report['passed']else 1)
