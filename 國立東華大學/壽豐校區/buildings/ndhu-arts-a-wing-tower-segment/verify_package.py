from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parent
checks={};sha=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()
for fn in ['validation.json','contour-validity-check.json','thin-feature-check.json']:
 r=json.loads((R/fn).read_text());checks[fn+'_passed']=r['passed'] and all(r['checks'].values());checks[fn+'_current_stl']=r['stl_sha256']==sha
checks['required_files']=all((R/f).is_file() for f in ['README.md','build_model.py','requirements.txt','model.stl','scene.blend','sources.json','render_preview.py','validate_model.py','check_contour_validity.py','check_thin_features.py','thin_canonical_v3.py','model-info.json','previews/front.png','previews/rear.png','previews/top.png','previews/front-rear.png'])
links=re.findall(r'\]\(([^)]+)\)',(R/'README.md').read_text());checks['readme_local_links_exist']=all((R/l).exists() for l in links if not l.startswith(('http:','https:','#')))
report={'passed':all(checks.values()),'checks':checks,'stl_sha256':sha,'not_a_physical_print_test':True,'not_slicer_toolpaths':True}
(R/'package-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if report['passed'] else 1)
