from pathlib import Path
import subprocess,sys,json
R=Path(__file__).resolve().parent
pairs=[('validate_model.py','validation.json'),('check_contour_validity.py','contour-validity-check.json'),('check_thin_features.py','thin-feature-check.json'),('check_component_opening.py','component-opening-check.json'),('check_recess_rays.py','recess-ray-check.json')]
for script,report in pairs:
 subprocess.run([sys.executable,str(R/script)],check=True)
 d=json.loads((R/report).read_text());assert d['passed'] and d['checks'] and all(d['checks'].values()),report
print('ALL ORIGINAL STL CHECKS PASSED')
