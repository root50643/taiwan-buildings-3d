"""Fail-closed full QA; reads original geometry and never repairs it."""
from pathlib import Path
import hashlib,json,subprocess,sys,re
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
canonical={'check_thin_features.py':'059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915','check_layer_components.py':'365e437af0d3d6defc2f52adf3e8601ac3643a14e15e03c8c8610b10bb8061a5'}
assert all(sha(R/f)==h for f,h in canonical.items())
for f in ['validate_model.py','check_thin_features.py','check_all_layers.py','check_layer_components.py']:subprocess.run([sys.executable,str(R/f)],check=True,cwd=R)
v=json.loads((R/'validation.json').read_text());c=json.loads((R/'layer-component-check.json').read_text());a=json.loads((R/'layer-opening-check.json').read_text())
missing=[]
for root in [R,R.parents[1],R.parents[2]]:
 text=(root/'README.md').read_text()
 for pair in re.findall(r'\]\(([^)]+)\)|(?:src|href)="([^"]+)"',text):
  q=next(x for x in pair if x)
  if not q.startswith(('http:','https:','#')) and not (root/q).exists():missing.append(q)
leaks=[]
for p in list(R.rglob('*.json'))+list(R.rglob('*.md'))+list(R.rglob('*.py')):
 if p.name=='run_all_checks.py':continue
 if any(q in p.read_text() for q in ['/workspace/','/home/agent/','/tmp/']):leaks.append(p.name)
checks={'raw_mesh_rebuild_blend_png_agreement':v['passed'] and all(v['checks'].values()),'all_0_2mm_layers_valid':len(a['layers'])==c['sampled_layers'],'all_original_polygons_survive_no_split':c['passed'] and all(c['checks'].values()),'canonical_scripts_unchanged':True,'readme_links_exist':not missing,'no_private_paths_in_public_text':not leaks}
report={'passed':all(checks.values()),'checks':checks,'dimensions_mm':v['dimensions_mm'],'stl_sha256':sha(R/'model.stl'),'surface_shells':v['surface_shells'],'bad_vertex_links':v['bad_vertex_links'],'sampled_layers':c['sampled_layers'],'original_polygon_tests':len(c['original_component_checks']),'eroded_failures':sum(x['eroded_components']!=1 for x in c['original_component_checks']),'opened_failures':sum(x['opened_components']!=1 for x in c['original_component_checks']),'maximum_opening_loss_fraction':c['maximum_opening_loss_fraction'],'layers_over_one_percent_opening_loss':c['layers_over_one_percent_opening_loss'],'canonical_scripts':canonical,'missing_links':missing,'private_path_leaks':leaks,'status':'author_frozen_v1_pending_independent_review','limitations':['非全面最小壁厚、非工具路徑或實體試印。','曲殼懸挑與十架搬運仍須實際切片判斷。','17.6m總高及角落牆線是有界照片假設。']}
(R/'qa-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));assert report['passed']
(R/'SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(R))+'\n' for p in sorted(R.rglob('*')) if p.is_file() and p.name!='SHA256SUMS'))
