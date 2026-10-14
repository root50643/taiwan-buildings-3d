"""Fail-closed package audit: original STL, reports, source checksums, previews, links.
Run after validate_model/check_thin_features/check_layer_components/check_voids/
check_ornaments/render_sections/test_fail_closed. Prints JSON without modifying files.
"""
from pathlib import Path
import re,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks={};stl=sha(R/'model.stl')
expected={'check_thin_features.py':'059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915','check_layer_components.py':'365e437af0d3d6defc2f52adf3e8601ac3643a14e15e03c8c8610b10bb8061a5'}
for f,h in expected.items():checks[f+'_canonical_sha']=sha(R/f)==h
for name in ['validation','layer-component-check','void-check','ornament-check','fail-closed-selftest','qa-summary']:
 d=json.loads((R/(name+'.json')).read_text());checks[name+'_all_checks']=d.get('passed') is True and bool(d.get('checks')) and all(x is True for x in d['checks'].values())
 if 'stl_sha256' in d:checks[name+'_same_stl']=d['stl_sha256']==stl
review=json.loads((R/'appearance-review.json').read_text());checks['appearance_review_current_stl']=review['status']=='approved' and review['stl_sha256']==stl
p=json.loads((R/'preview-provenance.json').read_text());checks['previews_bound_to_current_stl']=p['stl_sha256']==stl
checks['seven_actual_stl_previews']=len(p['previews'])==7
for f,h in p['previews'].items():
 checks[f+'_sha_matches']=sha(R/'previews'/f)==h
 with Image.open(R/'previews'/f) as im:im.verify()
q=json.loads((R/'ornament-section-provenance.json').read_text());checks['section_image_same_stl']=q['stl_sha256']==stl;checks['section_image_hash_matches']=sha(R/q['image'])==q['image_sha256']
refs=[]
for md in R.glob('*.md'):
 for href in re.findall(r'\]\(([^)]+)\)',md.read_text()):
  if '://' in href or href.startswith('#'):continue
  refs.append({'document':md.name,'target':href,'exists':(md.parent/href.split('#')[0]).exists()})
checks['all_relative_readme_links_exist']=bool(refs) and all(x['exists'] for x in refs)
checks['source_files_not_in_public_package']=not any(p.suffix.lower() in ['.pdf','.jpg','.jpeg'] or 'qa-private' in str(p.relative_to(R)) for p in R.rglob('*') if p.is_file())
manifest=[]
for line in (R/'SHA256SUMS').read_text().splitlines():
 h,f=line.split('  ',1);manifest.append({'file':f,'matches':(R/f).is_file() and sha(R/f)==h})
checks['all_manifest_files_match']=bool(manifest) and all(x['matches'] for x in manifest)
checks['manifest_lists_every_package_file']=set(x['file'] for x in manifest)=={str(p.relative_to(R)) for p in R.rglob('*') if p.is_file() and p.name!='SHA256SUMS'}
report={'passed':all(checks.values()),'checks':checks,'stl_sha256':stl,'relative_links_checked':len(refs),'manifest_files_checked':len(manifest),'notes':['Geometric pass is not appearance approval, actual slicer toolpath validation, or physical print proof.']}
print(json.dumps(report,indent=2));assert report['passed']
