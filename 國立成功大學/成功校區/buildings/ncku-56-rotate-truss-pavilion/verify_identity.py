"""Reject stale preceding-project labels across every deliverable text file."""
from pathlib import Path
import json,re,hashlib
A=Path(__file__).resolve().parent
# Construct sentinels so this checker itself does not contain the full alien names.
forbidden=['NTO'+'U','Dream '+'Fountain','Orchid '+'House','台積'+'電','樹之'+'歌','夢'+'泉','銀杏'+'橋','蘭花'+'屋','ntu-'+'ginkgo','nto'+'u-'+'dream','nthu-'+'yuning']
files=[]
for p in sorted(A.rglob('*')):
 if not p.is_file() or p.suffix in ['.blend','.3mf','.stl','.png'] or p.name=='SHA256SUMS' or p.name=='identity-validation.json':continue
 text=p.read_text();bad=[s for s in forbidden if (re.search(r'(?<![A-Za-z])'+re.escape(s)+r'(?![A-Za-z])',text,re.I) if s.isascii() else s in text)];assert not bad,(p.name,bad)
 files.append(dict(path=p.relative_to(A).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
for n in ['README.md','SOURCES.md','QA.md','LICENSE','build_model.py','render_model.py','sources.json','release.json']:
 s=(A/n).read_text();assert ('56亭' in s or '56 Pavilion' in s),n
src=json.loads((A/'sources.json').read_text());assert any(x['id']=='official_identity' for x in src['sources'])
f=json.loads((A/'qa/design-features.json').read_text());assert f['school']=='國立成功大學' and f['campus']=='成功校區' and f['slug']=='ncku-56-rotate-truss-pavilion'
(A/'qa/identity-validation.json').write_text(json.dumps(dict(status='PASS',name='56亭 / Rotate Truss Pavilion',school=f['school'],campus=f['campus'],checked_text_files=files,forbidden_previous_project_labels_found=0,canonical_identity_required_in_eight_primary_files=True),ensure_ascii=False,indent=2)+'\n')
print('Identity PASS:',len(files),'text files; required primary-file identity; no preceding-project labels')
