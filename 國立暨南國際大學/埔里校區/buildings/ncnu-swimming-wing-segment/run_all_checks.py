"""Fail-closed aggregate QA of the current delivered files. No repair performed."""
from pathlib import Path
import json,hashlib,subprocess,sys,tempfile,shutil
R=Path(__file__).resolve().parent
report={'passed':False,'checks':{'completed':False}}
(R/'qa-summary.json').write_text(json.dumps(report,indent=2))
for script in ['validate_model.py','check_contour_validity.py','check_thin_features.py']:
 subprocess.run([sys.executable,str(R/script)],check=True)
v=json.loads((R/'validation.json').read_text());c=json.loads((R/'contour-validity-check.json').read_text())
assert v['passed'] and all(v['checks'].values()) and c['passed'] and all(c['checks'].values())
src=(R/'check_thin_features.py').read_text()
assert hashlib.sha256(src.encode()).hexdigest()=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
negative={}
with tempfile.TemporaryDirectory() as td:
 t=Path(td);shutil.copy2(R/'model.stl',t/'model.stl')
 for name,find,replace in [('individual','p=Polygon(loop)','p=Polygon([(0,0),(1,1),(0,1),(1,0)])'),('combined',"assert shape.is_valid, f'Invalid combined section", "shape=Polygon([(0,0),(1,1),(0,1),(1,0)])\n assert shape.is_valid, f'Invalid combined section")]:
  assert find in src
  (t/'check_thin_features.py').write_text(src.replace(find,replace))
  p=subprocess.run([sys.executable,str(t/'check_thin_features.py')],capture_output=True,text=True)
  negative[name]={'exit_code':p.returncode,'assertion_error':'AssertionError' in p.stderr}
  assert p.returncode!=0 and 'AssertionError' in p.stderr,negative
report={'passed':True,'checks':{'all_original_mesh_checks':True,'source_rebuild_sha_matches':True,'blend_geometry_matches_stl':True,'all_0_2mm_contours_valid':True,'thin_screen_exit_zero':True,'canonical_v3_hash_matches':True,'individual_invalid_polygon_rejected':True,'combined_invalid_polygon_rejected':True},'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'negative_test':negative,'note':'Digital geometry checks only; no physical test print or slicer toolpath claim.'}
(R/'qa-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(report)
