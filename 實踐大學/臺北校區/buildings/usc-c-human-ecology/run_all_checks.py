from pathlib import Path
import subprocess,sys,json
r=Path(__file__).resolve().parent
for script,report in [('check_thin_features.py','thin-feature-check.json'),('check_layer_components.py','layer-component-check.json'),('check_screen.py','screen-check.json'),('validate_model.py','validation.json')]:
 subprocess.run([sys.executable,str(r/script)],check=True)
 data=json.loads((r/report).read_text())
 assert data.get('passed',True) and all(data.get('checks',{}).values()),report
print('All fail-closed geometry, layer, screen, rebuild, Blend and PNG checks passed.')
