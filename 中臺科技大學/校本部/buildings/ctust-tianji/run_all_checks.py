"""Reproduce every current-STL report. --bind-existing avoids repeat of completed
expensive original-face sampling; it requires current-SHA reports and newer outputs.
"""
from pathlib import Path
import argparse,subprocess,sys,json,hashlib
R=Path(__file__).resolve().parent;a=argparse.ArgumentParser();a.add_argument('--bind-existing',action='store_true');args=a.parse_args()
reports={'validate_model.py':'validation.json','check_thin_features.py':'thin-feature-check.json','check_layer_components.py':'layer-component-check.json','check_all_layers.py':'layer-opening-check.json','check_detailed_components.py':'detailed-component-check.json','check_surface_rays.py':'surface-ray-check.json','summarize_warnings.py':'warning-summary.json','check_dense_samples.py':'dense-sampling-binding.json','summarize_dense_samples.py':'dense-summary.json','check_local_back_roots.py':'local-back-roots.json','check_corner_roots.py':'corner-root-check.json','check_family_coverage.py':'family-coverage.json'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();current=sha(R/'model.stl');bindings={};checks={}
for script,report in reports.items():
 if not args.bind_existing:subprocess.run([sys.executable,str(R/script)],cwd=R,check=True)
 f=R/report;j=json.loads(f.read_text());assert f.stat().st_mtime>=(R/'model.stl').stat().st_mtime,report
 if 'stl_sha256' in j:assert j['stl_sha256']==current,report
 ok=j.get('passed',True) and all(j.get('checks',{}).values());assert ok,report;checks[report]=bool(ok);bindings[report]={'script_sha256':sha(R/script),'report_sha256':sha(f),'stl_sha256':current}
assert sha(R/'check_thin_features.py')=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
assert sha(R/'check_layer_components.py')=='365e437af0d3d6defc2f52adf3e8601ac3643a14e15e03c8c8610b10bb8061a5'
(R/'qa-summary.json').write_text(json.dumps({'stl_sha256':current,'passed':True,'checks':checks,'bindings':bindings,'warnings_status':'316 local Polygon loss exceptions remain pending independent review and root approval. Hard checks and nominated roots do not approve warnings or constitute global thickness or a physical print.'},indent=2));print('ALL HARD CHECKS BOUND; local exception approval still pending')
