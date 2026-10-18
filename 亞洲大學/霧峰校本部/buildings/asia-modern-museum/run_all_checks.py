"""Fail closed: rerun every geometry check and validate links/checksums."""
from pathlib import Path
import json,hashlib,subprocess,sys,re
R=Path(__file__).resolve().parent
def publication_review_state(stl_sha256):
 # A programmatic independent rebuild is author QA, not reviewer release.
 published_sha='0130b50cd4b44752b86f935dec384faf6326cbacb5270759f5024cdc1614838a'
 matches=stl_sha256==published_sha
 return {'publication':{'status':'published' if matches else 'current_stl_not_matched_to_publication_record',
   'record_commit':'6002ac2bc30d8f17a593b1aa398cc2e0f2920e1d',
   'record_stl_sha256':published_sha,'current_stl_matches_record':matches},
  'independent_review':{'overall_release_status':'unconfirmed',
   'evidence_inventory_checked_date':'2026-10-18',
   'note':'A complete dated and scoped overall independent release record has not been confirmed; this is not a review-failure finding. Programmatic rebuild and PNG comparisons remain author digital QA.'}}

# A stopped rerun must not leave a previous run's passed summary as its result.
initial={'passed':None,'status':'author_digital_QA_incomplete','scope':'This invocation has started but has not completed the checks; inspect its exit status and diagnostics.'}
(R/'qa-summary.json').write_text(json.dumps(initial,indent=2),encoding='utf8',newline='\n')
initial.update(publication_review_state(hashlib.sha256((R/'model.stl').read_bytes()).hexdigest() if (R/'model.stl').is_file() else None))
(R/'qa-summary.json').write_text(json.dumps(initial,indent=2),encoding='utf8',newline='\n')
expected={'check_thin_features.py':'059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915','check_layer_components.py':'365e437af0d3d6defc2f52adf3e8601ac3643a14e15e03c8c8610b10bb8061a5'}
for file,h in expected.items():assert hashlib.sha256((R/file).read_bytes()).hexdigest()==h
for file in ['validate_model.py','check_thin_features.py','check_layer_components.py','check_open_spaces.py']:
 subprocess.run([sys.executable,str(R/file)],check=True)
checks={}
for name in ['validation.json','layer-component-check.json','open-space-check.json','thin-feature-review.json']:
 data=json.loads((R/name).read_text(encoding='utf8'));checks[name]=data['passed'] is True and all(v is True for v in data['checks'].values())
thin=json.loads((R/'thin-feature-check.json').read_text(encoding='utf8'));checks['canonical_opening_all_samples_under_one_percent']=thin['layers_over_one_percent_opening_loss']==0
checks['canonical_validator_hashes_match']=all(hashlib.sha256((R/file).read_bytes()).hexdigest()==h for file,h in expected.items())
broken=[]
for doc in [R/'README.md',R.parents[1]/'README.md',R.parents[2]/'README.md']:
 assert doc.exists()
 for target in re.findall(r'\]\(([^)]+)\)',doc.read_text(encoding='utf8')):
  if '://' not in target and not (doc.parent/target.split('#')[0]).exists():broken.append([str(doc),target])
checks['three_level_readme_relative_links_exist']=not broken
report={'passed':all(checks.values()),'status':'author_digital_QA_passed' if all(checks.values()) else 'author_digital_QA_failed','checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'canonical_validator_hashes':expected,'limitations':'Digital geometry checks only. No slicer toolpath or physical print validation.'}
report.update(publication_review_state(report['stl_sha256']))
(R/'qa-summary.json').write_text(json.dumps(report,indent=2),encoding='utf8',newline='\n');print(json.dumps(report,indent=2));assert report['passed']
