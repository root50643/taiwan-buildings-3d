"""Reject stale project labels and verify Sewn Pavilion identity throughout this package."""
from pathlib import Path
import json,re,hashlib
A=Path(__file__).resolve().parent
# Split sentinels keep this checker from containing the exact labels it prohibits.
forbidden=['56'+'亭','56 '+'Pavilion','Rotate '+'Truss','ncku-'+'56-rotate-truss-pavilion','成功'+'校區','NTO'+'U','Dream '+'Fountain','Orchid '+'House','台積'+'電','樹之'+'歌','夢'+'泉','銀杏'+'橋','蘭花'+'屋','ntu-'+'ginkgo','nto'+'u-'+'dream','nthu-'+'yuning']
files=[]
for p in sorted(A.rglob('*')):
 if not p.is_file() or p.suffix in ['.blend','.3mf','.stl','.png','.pyc'] or '__pycache__' in p.parts or p.name in ['SHA256SUMS','identity-validation.json']:continue
 s=p.read_text();bad=[x for x in forbidden if (re.search(r'(?<![A-Za-z])'+re.escape(x)+r'(?![A-Za-z])',s,re.I) if x.isascii() else x in s)];assert not bad,(p.relative_to(A).as_posix(),bad)
 files.append(dict(path=p.relative_to(A).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
primary=['README.md','SOURCES.md','QA.md','LICENSE','build_model.py','render_model.py','sources.json','release.json']
for n in primary:
 s=(A/n).read_text();assert ('懸鏈' in s or 'Sewn Pavilion' in s),n
src=json.loads((A/'sources.json').read_text());f=json.loads((A/'qa/design-features.json').read_text())
for obj in [src,f]:
 assert obj['school']=='國立成功大學' and obj['campus']=='光復校區' and obj['slug']=='ncku-sewn-pavilion'
assert any(x['id']=='official_identity' for x in src['sources'])
assert src['location_basis']['inference_not_direct_geotag'] and src['current_condition_not_certified']
assert src['major_topology']['bands_per_leaf']==6 and len(src['major_topology']['shared_feet'])==3
assert src['raw_reference_files_excluded'] and not src['physical_print_tested'] and not src['support_free_certified']
release=json.loads((A/'release.json').read_text())
for key,value in [('school','國立成功大學'),('campus','光復校區'),('slug','ncku-sewn-pavilion')]:
 if key in release:assert release[key]==value
(A/'qa/identity-validation.json').write_text(json.dumps(dict(status='PASS',name='懸鏈・榭 / Sewn Pavilion',school='國立成功大學',campus='光復校區',slug='ncku-sewn-pavilion',checked_text_files=files,forbidden_previous_project_labels_found=0,canonical_identity_required_in_eight_primary_files=True,primary_files=primary,location_inference_and_historical_scope_verified=True),ensure_ascii=False,indent=2)+'\n')
print('Identity PASS:',len(files),'text files; Sewn Pavilion in eight primary files; school/campus/slug and historical inference scope verified')
