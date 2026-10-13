"""Run all delivered checks without repairing geometry; any failure is a nonzero exit."""
from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).resolve().parent
canonical=R/'check_thin_features.py'
assert hashlib.sha256(canonical.read_bytes()).hexdigest()=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
for name,report in [('validate_model.py','validation.json'),('check_contour_validity.py','contour-validity-check.json'),('check_thin_strict.py','strict-thin-check.json'),('check_thin_all_layers.py','thin-all-layers-check.json')]:
 subprocess.run([sys.executable,str(R/name)],check=True)
 j=json.loads((R/report).read_text());assert j['passed'] and all(j['checks'].values()),report
print('All checks passed. This is not a physical-print or slicer-toolpath guarantee.')
