"""Fail closed: stop on every nonzero subprocess; inspect original-STL reports.
No source image, polygon repair, mesh healing, or broad printability claim.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
assert sha(R/'check_thin_features.py')==expected,'Unapproved thin validator changes'
commands=[]
for name in ['validate_model.py','check_layers.py','check_thin_features.py']:
 r=subprocess.run([sys.executable,str(R/name)],cwd=R,capture_output=True,text=True)
 commands.append({'script':name,'exit_code':r.returncode,'script_sha256':sha(R/name)})
 if r.returncode!=0:print(r.stdout);print(r.stderr);raise SystemExit(r.returncode)
v=json.loads((R/'validation.json').read_text());l=json.loads((R/'layer-check.json').read_text());t=json.loads((R/'thin-feature-check.json').read_text())
checks={'all_commands_exit_zero':all(c['exit_code']==0 for c in commands),'all_original_mesh_checks_true':v['passed'] and all(v['checks'].values()),'all_0p2mm_layer_checks_true':l['passed'] and all(l['checks'].values()),'thin_screen_completed':t['sampled_layers']>0,'canonical_fail_closed_v3_sha_matches':sha(R/'check_thin_features.py')==expected,'reports_match_current_stl':v['stl_sha256']==sha(R/'model.stl')}
report={'passed':all(checks.values()),'checks':checks,'commands':commands,'stl_sha256':sha(R/'model.stl'),'blend_sha256':sha(R/'scene.blend'),'dimensions_mm':v['dimensions_mm'],'layer_count_0p2mm':l['sampled_layers'],'thin_layer_count_1mm':t['sampled_layers'],'thin_max_opening_loss_fraction':t['maximum_opening_loss_fraction'],'thin_over_one_percent_layers':t['layers_over_one_percent_opening_loss'],'note':'Morphological opening loss includes corners; visual review and backed detail dimensions are documented in README. Not a slicer toolpath or physical-print test.','source_images_packaged':False}
(R/'qa-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));assert report['passed']
