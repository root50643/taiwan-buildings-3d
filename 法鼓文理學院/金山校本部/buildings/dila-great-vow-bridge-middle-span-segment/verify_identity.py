"""Identity consistency: 法鼓文理學院金山校本部大願橋."""
from pathlib import Path
import json,hashlib
A=Path(__file__).parent
forbidden=['ND'+'HU','東'+'華','壽豐'+'校區','Tam'+'kang','淡'+'江','書卷'+'廣場','tku-'+'scroll','成功'+'大學','NC'+'KU']
files=[]
for p in sorted(A.rglob('*')):
 if not p.is_file() or p.suffix in ['.png','.stl','.blend','.3mf'] or p.name in ['SHA256SUMS','identity-validation.json']:continue
 s=p.read_text();assert not any(x in s for x in forbidden),p
 files.append(dict(path=p.relative_to(A).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
for n in ['README.md','SOURCES.md','QA.md','LICENSE','build_model.py','render_model.py','sources.json','release.json']:
 s=(A/n).read_text();assert '大願橋' in s and '法鼓文理學院' in s and '金山校本部' in s,n
f=json.loads((A/'qa/design-features.json').read_text());assert f['school']=='法鼓文理學院' and f['campus']=='金山校本部' and f['bank_double_tube_groups']==2
(A/'qa/identity-validation.json').write_text(json.dumps(dict(name='法鼓文理學院金山校本部大願橋',all_text_names_consistent=True,files=files),ensure_ascii=False,indent=2)+'\n')
