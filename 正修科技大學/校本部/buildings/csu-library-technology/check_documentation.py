"""Check relative public links, three README levels and actual front/rear ordering."""
from pathlib import Path
import re,json,hashlib
R=Path(__file__).resolve().parent;campus=R.parent.parent;school=campus.parent
rows=[]
for p in [school/'README.md',campus/'README.md',R/'README.md']:
 t=p.read_text();matches=re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',t)
 for link in matches:
  if '://'not in link and not link.startswith('#'):assert (p.parent/link.split('#')[0]).exists(),(p,link)
 line=next(line for line in t.splitlines()if 'front.png' in line);assert 'rear.png'in line and line.index('front.png')<line.index('rear.png')
 rows.append(dict(relative_level='school'if p.parent==school else 'campus'if p.parent==campus else 'model',relative_links_exist=True,front_rear_same_row=True))
for p in R.rglob('*'):
 if p.suffix in ['.md','.json','.py','.txt']:
  t=p.read_text();assert '/'+'workspace/'not in t and '/'+'tmp/'not in t,(p,'private absolute path')
assert len(list((R/'previews').glob('*.png')))==10
report=dict(passed=True,checks=dict(all_three_readmes_front_rear_same_row=len(rows)==3,relative_links_exist=True,no_private_absolute_paths=True,ten_actual_previews_present=True),readmes=rows,stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest())
(R/'documentation-check.json').write_text(json.dumps(report,indent=2));print(report)
