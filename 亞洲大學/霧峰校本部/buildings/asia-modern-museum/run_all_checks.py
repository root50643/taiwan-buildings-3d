"""Fail closed: rerun every geometry check and validate links/checksums."""
from pathlib import Path
import json,hashlib,subprocess,sys,re
R=Path(__file__).resolve().parent
expected={'check_thin_features.py':'059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915','check_layer_components.py':'365e437af0d3d6defc2f52adf3e8601ac3643a14e15e03c8c8610b10bb8061a5'}
for file,h in expected.items():assert hashlib.sha256((R/file).read_bytes()).hexdigest()==h
for file in ['validate_model.py','check_thin_features.py','check_layer_components.py','check_open_spaces.py']:
 subprocess.run([sys.executable,str(R/file)],check=True)
checks={}
for name in ['validation.json','layer-component-check.json','open-space-check.json','thin-feature-review.json']:
 data=json.loads((R/name).read_text());checks[name]=data['passed'] is True and all(v is True for v in data['checks'].values())
thin=json.loads((R/'thin-feature-check.json').read_text());checks['canonical_opening_all_samples_under_one_percent']=thin['layers_over_one_percent_opening_loss']==0
checks['canonical_validator_hashes_match']=True
broken=[]
for doc in [R/'README.md',R.parents[1]/'README.md',R.parents[2]/'README.md']:
 assert doc.exists()
 for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
  if '://' not in target and not (doc.parent/target.split('#')[0]).exists():broken.append([str(doc),target])
checks['three_level_readme_relative_links_exist']=not broken
report={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'canonical_validator_hashes':expected,'limitations':'Digital geometry checks only. No slicer toolpath or physical print validation.'}
(R/'qa-summary.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['passed']
