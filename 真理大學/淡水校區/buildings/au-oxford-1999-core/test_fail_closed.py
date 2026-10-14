"""Prove that the shipped validators reject deliberately injected invalid polygons."""
from pathlib import Path
import json,subprocess,sys,tempfile,shutil,hashlib
R=Path(__file__).resolve().parent;rows=[];checks={}
for script in ['check_thin_features.py','check_layer_components.py']:
 original=(R/script).read_text()
 for mode in ['individual','combined']:
  if mode=='individual':
   marker='   p=Polygon(loop)';replacement=marker+'\n   p=Polygon([(0,0),(1,1),(1,0),(0,1)])'
  else:
   marker=' assert shape.is_valid,';replacement=' shape=Polygon([(0,0),(1,1),(1,0),(0,1)])\n'+marker
  assert marker in original
  mutated=original.replace(marker,replacement,1)
  with tempfile.TemporaryDirectory() as td:
   t=Path(td);shutil.copy(R/'model.stl',t/'model.stl');(t/script).write_text(mutated)
   p=subprocess.run([sys.executable,str(t/script)],capture_output=True,text=True)
   ok=p.returncode!=0 and 'AssertionError' in p.stderr and ('Invalid closed loop' in p.stderr or 'Invalid combined section' in p.stderr)
   checks[f'{script}_{mode}_invalid_rejected']=ok
   rows.append({'validator':script,'original_sha256':hashlib.sha256((R/script).read_bytes()).hexdigest(),'injection':mode,'exit_code':p.returncode,'last_error_line':p.stderr.strip().splitlines()[-1] if p.stderr else ''})
out={'passed':all(checks.values()),'checks':checks,'tests':rows};(R/'fail-closed-selftest.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
