"""Identity consistency: 建國科技大學綠崗亭."""
from pathlib import Path
import json,hashlib
A=Path(__file__).parent
forbidden=['ND'+'HU','國立東'+'華大學','壽豐'+'校區','Tam'+'kang','淡'+'江','書卷'+'廣場','tku-'+'scroll','成功'+'大學','NC'+'KU']
files=[]
for p in sorted(A.rglob('*')):
 if not p.is_file() or p.suffix in ['.png','.stl','.blend','.3mf'] or p.name in ['SHA256SUMS','identity-validation.json']:continue
 s=p.read_text();assert not any(x in s for x in forbidden),p
 files.append(dict(path=p.relative_to(A).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
for n in ['README.md','SOURCES.md','QA.md','LICENSE','build_model.py','render_model.py','sources.json','release.json']:
 s=(A/n).read_text();assert '建國科技大學' in s and '綠崗亭' in s,n
f=json.loads((A/'qa/design-features.json').read_text());assert f['school']=='建國科技大學' and f['continuous_corner_columns']==4
(A/'qa/identity-validation.json').write_text(json.dumps(dict(name='建國科技大學綠崗亭',all_text_names_consistent=True,files=files),ensure_ascii=False,indent=2)+'\n')
