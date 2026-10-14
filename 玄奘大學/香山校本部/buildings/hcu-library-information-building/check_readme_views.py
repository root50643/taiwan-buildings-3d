"""Verify all three README levels display front/rear on one Markdown table row."""
from pathlib import Path
import re,json,hashlib
R=Path(__file__).resolve().parent;rows=[]
for p in [R/'README.md',R.parents[1]/'README.md',R.parents[2]/'README.md']:
 s=p.read_text();line=next(x for x in s.splitlines() if '![正面' in x and '![背面' in x);targets=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',line);assert len(targets)==2
 for t in targets:
  q=(p.parent/t).resolve();assert q.exists() and q.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
 assert targets[0].endswith('previews/front.png') and targets[1].endswith('previews/rear.png')
 rows.append(dict(readme=str(p.relative_to(R.parents[2])),same_row=True,front=targets[0],rear=targets[1],front_sha256=hashlib.sha256((p.parent/targets[0]).read_bytes()).hexdigest(),rear_sha256=hashlib.sha256((p.parent/targets[1]).read_bytes()).hexdigest()))
(R/'readme-view-check.json').write_text(json.dumps(dict(passed=True,checks={'three_levels_front_rear_same_row':True,'all_six_image_links_exist':True},rows=rows),ensure_ascii=False,indent=2))
print('PASS three README view rows')
