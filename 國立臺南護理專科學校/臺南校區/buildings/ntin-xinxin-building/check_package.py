"""Fail-closed public links, evidence chain, validator lineage and PNG privacy."""
from pathlib import Path
import hashlib,json,re
from PIL import Image
R=Path(__file__).resolve().parent
school=R.parents[2];campus=R.parents[1]
checks={};links=[]
for path in [R/'README.md',campus/'README.md',school/'README.md']:
 s=path.read_text();assert 'front.png' in s and 'rear.png' in s
 checks[str(path.relative_to(school))+'_front_and_rear_same_row']=any('front.png' in line and 'rear.png' in line for line in s.splitlines())
 for target in re.findall(r'\]\(([^)]+)\)',s):
  target=target.strip('<>')
  if '://' in target or target.startswith('#'):continue
  target=target.split('#')[0];ok=(path.parent/target).exists();links.append({'readme':str(path.relative_to(school)),'target':target,'exists':ok})
checks['all_relative_readme_links_exist']=all(x['exists'] for x in links)
checks['canonical_v3_sha256_unchanged']=hashlib.sha256((R/'check_thin_features.py').read_bytes()).hexdigest()=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
checks['per_component_validator_sha256_unchanged']=hashlib.sha256((R/'check_layer_components.py').read_bytes()).hexdigest()=='365e437af0d3d6defc2f52adf3e8601ac3643a14e15e03c8c8610b10bb8061a5'
checks['all_actual_png_metadata_empty']=all(not Image.open(p).info for p in (R/'previews').glob('*.png'))
checks['public_sources_have_no_private_file_paths']=not any(x in (R/'sources.json').read_text() for x in ['/workspace/','qa-private/','"file":','"reviewed_image":'])
checks['source_images_not_in_public_tree']=not any(p.suffix.lower() in ['.jpg','.jpeg','.pdf'] for p in school.rglob('*') if p.is_file())
for name in ['validation.json','asset-consistency-check.json','layer-component-check.json']:
 d=json.loads((R/name).read_text());checks[name+'_passed']=d['passed'] and all(d['checks'].values())
checks['stl_sha256_matches_saved_blend_validation']=json.loads((R/'asset-consistency-check.json').read_text())['stl_sha256']==hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()
report={'checks':checks,'passed':all(checks.values()),'links':links}
(R/'package-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':checks,'passed':report['passed']},ensure_ascii=False,indent=2));assert report['passed']
