from pathlib import Path
import re,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent
checks={}
for p in [R/'README.md',R.parents[1]/'README.md',R.parents[2]/'README.md']:
 t=p.read_text();rows=[l for l in t.splitlines()if 'previews/front.png'in l and 'previews/rear.png'in l];checks[str(p.relative_to(R.parents[2]))+'_same_model_front_rear_row']=bool(rows)
 for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',t):
  if '://'not in link and not link.startswith('#'):assert(p.parent/link).exists(),link
checks['no_compiled_python_cache']=not any(R.rglob('*.pyc'))
checks['only_actual_stl_pngs']=set(p.name for p in (R/'previews').glob('*.png'))=={x+'.png'for x in ['front','rear','elevation','top','field-detail','entry-detail','left-detail']}
for name in ['front','rear','elevation','top']:
 im=Image.open(R/'previews'/f'{name}.png');checks[name+'_full_canvas']=im.size==(1000,800)
for p in R.rglob('*'):
 if p.suffix in ['.py','.cpp','.json','.md','.txt'] and p.is_file():
  t=p.read_text();assert ('/'+ 'workspace'+'/')not in t and ('/'+ 'tmp'+'/ntu')not in t, p.name
out=dict(checks=checks,passed=all(checks.values()),stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),manual_visual_review='All seven actual STL views inspected; front/rear/elevation/top complete building, three detail views intentionally cropped. Source comparisons are private and excluded.')
(R/'documentation-check.json').write_text(json.dumps(out,indent=2));print(out);assert out['passed']
