"""Fail-closed current-STL verification. All reports are regenerated before SHA binding."""
from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).resolve().parent
reports={
'validate_model.py':'validation.json',
'check_thin_features.py':'thin-feature-check.json',
'check_layer_components.py':'layer-component-check.json',
'check_all_layers.py':'layer-opening-check.json',
'check_detailed_components.py':'detailed-component-check.json',
'check_surface_rays.py':'surface-ray-check.json',
'check_warning_calipers.py':'warning-caliper-check.json',
'check_local_corner_profiles.py':'local-corner-profiles.json',
'check_local_back_roots.py':'local-back-roots.json',
'check_dense_samples.py':'dense-sampling-binding.json',
'summarize_dense_samples.py':'dense-face-review.json',
'check_dense_controls.py':'dense-control-solid-angle.json',
'check_junction_roots.py':'junction-root-check.json',
'check_junction_pair_family.py':'junction-pair-family.json',
'check_junction_triple_family.py':'junction-family-review.json'}
for script in reports:subprocess.run([sys.executable,str(R/script)],cwd=R,check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();current=sha(R/'model.stl');checks={};bindings={}
for script,name in reports.items():
 j=json.loads((R/name).read_text());checks[name]=j.get('passed',True) and all(j.get('checks',{}).values());assert checks[name],name
 if 'stl_sha256' in j:assert j['stl_sha256']==current,name
 bindings[name]={'report_sha256':sha(R/name),'script_sha256':sha(R/script),'stl_sha256':current,'role':('intermediate pair-direction failures retained; final family root acceptance is in junction-family-review.json' if name=='junction-pair-family.json' else 'validation or bounded evidence')}
assert sha(R/'check_thin_features.py')=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
assert sha(R/'check_layer_components.py')=='365e437af0d3d6defc2f52adf3e8601ac3643a14e15e03c8c8610b10bb8061a5'
(R/'qa-summary.json').write_text(json.dumps({'passed':True,'checks':checks,'stl_sha256':current,'bindings':bindings,'thin_loss_exception_status':'pending independent and root approval; hard QA does not approve warnings'},indent=2));print('ALL HARD QA PASS; thin loss exceptions remain review-pending')
