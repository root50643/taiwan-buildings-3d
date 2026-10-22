"""Reject stale preceding-project labels in every deliverable text file."""
from pathlib import Path
import json,re,hashlib
A=Path(__file__).resolve().parent
# Sentinels split to avoid falsely matching this checker itself.
forbidden=['NCK'+'U','Rotate '+'Truss Pavilion','56 '+'Pavilion','Sewn '+'Pavilion','成功'+'大學','懸鏈'+'榭','56'+'亭','Dream '+'Fountain','夢'+'泉','nck'+'u-'+'sewn','nck'+'u-'+'56','nthu-'+'yuning']
files=[]
for p in sorted(A.rglob('*')):
 if not p.is_file() or p.suffix in ['.blend','.3mf','.stl','.png'] or p.name in ['SHA256SUMS','identity-validation.json']:continue
 text=p.read_text();bad=[s for s in forbidden if (re.search(r'(?<![A-Za-z])'+re.escape(s)+r'(?![A-Za-z])',text,re.I) if s.isascii() else s in text)];assert not bad,(p.name,bad)
 files.append(dict(path=p.relative_to(A).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
for n in ['README.md','SOURCES.md','QA.md','LICENSE','build_model.py','render_model.py','sources.json','release.json']:
 s=(A/n).read_text();assert '書卷廣場竹卷雕塑' in s or 'Scroll Square Monument' in s,n
src=json.loads((A/'sources.json').read_text());assert any(x['id']=='official_identity' for x in src['sources'])
f=json.loads((A/'qa/design-features.json').read_text());assert f['school']=='淡江大學' and f['campus']=='淡水校本部' and f['slug']=='tku-scroll-square-monument'
assert len(f['sheet_parameters'])==4 and f['narrow_step_count']==5 and f['no_top_cover'] and f['no_center_column']
assert len({x['high'] for x in f['sheet_parameters']})==4
(A/'qa/identity-validation.json').write_text(json.dumps(dict(status='PASS',name='書卷廣場竹卷雕塑 / Scroll Square Monument',school=f['school'],campus=f['campus'],checked_text_files=files,forbidden_previous_project_labels_found=0,canonical_identity_required_in_eight_primary_files=True),ensure_ascii=False,indent=2)+'\n')
print('Identity PASS:',len(files),'text files; eight primary-file names; no stale labels')
