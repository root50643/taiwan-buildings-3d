from pathlib import Path
import hashlib,subprocess,sys,json
R=Path(__file__).resolve().parent
# Exact canonical identity recorded below; canonical report intentionally has no passed field.
expected='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
sha=hashlib.sha256((R/'check_thin_features.py').read_bytes()).hexdigest();assert sha==expected
p=subprocess.run([sys.executable,str(R/'check_thin_features.py')],cwd=R)
d=json.loads((R/'thin-feature-check.json').read_text());ok=p.returncode==0 and d['sampled_layers']==len(d['layers'])
(R/'canonical-script-check.json').write_text(json.dumps({'passed':ok,'canonical_sha256':sha,'exit_code':p.returncode,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'report_has_no_passed_field':True},indent=2));raise SystemExit(0 if ok else 1)
