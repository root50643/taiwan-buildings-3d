"""Fail-closed aggregate thin screen. Canonical validator is preserved byte-for-byte."""
from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).resolve().parent
p=R/'check_thin_features.py'
checks={'canonical_v3_sha_matches':hashlib.sha256(p.read_bytes()).hexdigest()=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'}
assert checks['canonical_v3_sha_matches']
subprocess.run([sys.executable,str(p)],check=True)
r=json.loads((R/'thin-feature-check.json').read_text())
checks.update({'all_sampled_layers_under_1_percent_loss':all(x['fraction']<.01 for x in r['layers']),'canonical_completed':r['sampled_layers']>0})
out={'passed':all(checks.values()),'checks':checks,'maximum_opening_loss_fraction':r['maximum_opening_loss_fraction'],'reference_width_mm':.8,'limitation':'Morphological XY screen, not exhaustive minimum wall thickness, toolpath or physical print.'}
(R/'strict-thin-check.json').write_text(json.dumps(out,indent=2));print(out)
raise SystemExit(0 if out['passed'] else 1)
