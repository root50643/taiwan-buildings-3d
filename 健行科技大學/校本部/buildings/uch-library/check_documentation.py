from pathlib import Path
import re,json,hashlib
from PIL import Image
R=Path(__file__).parent;school=R.parents[2];campus=R.parents[1];rows=[]
for folder in [school,campus,R]:
 p=folder/'README.md';s=p.read_text();assert any('front.png' in line and 'rear.png' in line and line.startswith('|')for line in s.splitlines()),p
 rows.append(str(p.relative_to(school)))
for p in school.rglob('*.md'):
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if target.startswith(('http:','https:','#')):continue
  assert (p.parent/target.split('#')[0]).exists(),(p,target)
assert len(list((R/'previews').glob('*.png')))==10
for p in (R/'previews').glob('*.png'):assert Image.open(p).size==(1200,900)
assert not any(p.suffix.lower()in ['.jpg','.jpeg','.webp','.pdf','.pptx']for p in school.rglob('*')if p.is_file())
checks={'three_readmes_same_model_front_rear_same_row':len(rows)==3,'all_relative_document_links_exist':True,'ten_png_dimensions_correct':True,'no_source_photo_pdf_ppt_redistribution':True}
r={'passed':True,'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'readmes':rows};(R/'documentation-check.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(r)
