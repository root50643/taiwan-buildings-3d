"""Fail-closed local publication gate. Run with model dependencies and Blender on PATH.
Rechecks actual STL, rebuilds source in clean temporary directories, and reads Blender.
Does not replace STL, Blender or previews; reports are refreshed next to each model.
"""
from pathlib import Path
import concurrent.futures,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'model-manifest.json').read_text())
def verify(row):
 d=ROOT/Path(row['repo_directory']).relative_to('國立成功大學')
 assert hashlib.sha256((d/'model.stl').read_bytes()).hexdigest()==row['stl_sha256'],d
 for script,report in [('validate_model.py','validation.json'),('validate_sections.py','cross_sections.json'),('check_thin.py','thin-feature-check.json')]:
  proc=subprocess.run([sys.executable,str(d/script)],capture_output=True,text=True)
  assert proc.returncode==0,(d,script,proc.stdout,proc.stderr)
  data=json.loads((d/report).read_text())
  assert data['stl_sha256']==row['stl_sha256'],(d,report)
  if report=='validation.json':assert data['passed'] is True and all(x is True for x in data['checks'].values()),d
  if report=='cross_sections.json':assert data['passed'] is True and not data['failed_samples'],d
 print('PASS',row['repo_directory'],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 list(pool.map(verify,manifest['models']))
assert len(manifest['models'])==30
print('All 30 pass; inspect thin-feature warnings and visual evidence separately. No print/slicer claim.')
