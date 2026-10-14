"""Check all package references and metadata without changing the delivered mesh."""
from pathlib import Path
import hashlib,json,re
from PIL import Image
R=Path(__file__).resolve().parent;U=R.parents[2]
checks={};links=[]
for p in U.rglob('README.md'):
 for ref in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text()):
  if ref.startswith(('http:','https:','#')):continue
  target=p.parent/ref;ok=target.exists();links.append({'from':p.relative_to(U).as_posix(),'target':ref,'exists':ok});assert ok,(p,ref)
checks['all_readme_relative_links_exist']=all(v['exists'] for v in links)
checks['all_seven_previews_are_actual_stl']=len(list((R/'previews').glob('*.png')))==7 and json.loads((R/'render-reproduction-check.json').read_text())['passed']
checks['all_preview_metadata_empty']=all(not Image.open(p).info for p in (R/'previews').glob('*.png'))
checks['all_previews_900px_and_under_1400px_high']=all(Image.open(p).width==900 and Image.open(p).height<=1400 for p in (R/'previews').glob('*.png'))
checks['no_third_party_source_images']=not any(p.suffix.lower() in ['.jpg','.jpeg','.pdf','.webp'] for p in U.rglob('*') if p.is_file())
checks['six_source_records']=len(json.loads((R/'sources.json').read_text())['sources'])==6
checks['all_qa_checks_true']=json.loads((R/'qa-summary.json').read_text())['passed'] and all(json.loads((R/'qa-summary.json').read_text())['checks'].values())
checks['stl_hash_matches_qa']=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()==json.loads((R/'qa-summary.json').read_text())['stl_sha256']
checks['no_private_absolute_paths_in_text']=all(not any(t in p.read_text() for t in ['/'+'workspace/','/'+'root/','/'+'tmp/ntu']) for p in U.rglob('*') if p.is_file() and p.suffix in ['.py','.md','.json','.txt'])
report={'passed':all(checks.values()),'checks':checks,'relative_links':links};(R/'package-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));assert report['passed']
