"""Fail closed: run every original-geometry screen, never repair input."""
from pathlib import Path
import subprocess,sys,json,hashlib
r=Path(__file__).resolve().parent
(r/'all-checks.json').unlink(missing_ok=True)
assert hashlib.sha256((r/'check_thin_features.py').read_bytes()).hexdigest()=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
for f in ['validate_model.py','check_thin_features.py','check_all_layers.py','check_layer_components.py','check_recess_roots.py','check_preview_rebuild.py']:
 subprocess.run([sys.executable,str(r/f)],check=True)
for n in ['validation.json','layer-component-check.json','recess-root-check.json','preview-rebuild-check.json']:
 j=json.loads((r/n).read_text());assert j['passed'] and all(j['checks'].values())
(r/'all-checks.json').write_text(json.dumps({'stl_sha256':hashlib.sha256((r/'model.stl').read_bytes()).hexdigest(),'passed':True,'checks':{'all_scripts_exit_zero':True,'all_report_checks_true':True,'canonical_v3_sha_matches':True}},indent=2))
