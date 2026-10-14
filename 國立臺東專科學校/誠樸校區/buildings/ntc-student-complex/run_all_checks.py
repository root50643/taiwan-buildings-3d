"""Fail-closed QA runner. No input STL repair. Rewrites reports, not geometry."""
from pathlib import Path
import hashlib,json,subprocess,sys,re
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
canonical={'check_thin_features.py':'059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915','check_layer_components.py':'365e437af0d3d6defc2f52adf3e8601ac3643a14e15e03c8c8610b10bb8061a5'}
assert all(sha(R/f)==s for f,s in canonical.items()),'canonical scripts changed'
for f in ['validate_model.py','check_thin_features.py','check_all_layers.py','check_layer_components.py','check_open_spaces.py']:
 subprocess.run([sys.executable,str(R/f)],check=True,cwd=R)
v=json.loads((R/'validation.json').read_text());c=json.loads((R/'layer-component-check.json').read_text());o=json.loads((R/'open-space-check.json').read_text());t=json.loads((R/'thin-feature-check.json').read_text());a=json.loads((R/'layer-opening-check.json').read_text())
checks={'raw_mesh_and_source_blend_png_agreement':v['passed'],'all_0_2mm_layers_valid':len(a['layers'])==c['sampled_layers'],'every_original_polygon_survives_without_split':c['passed'] and all(c['checks'].values()),'open_spaces_rays':o['passed'],'canonical_validator_hashes':True,'no_thin_feature_exceptions':not json.loads((R/'thin-feature-review.json').read_text())['exceptions']}
# Local links in all three READMEs, including both images of the same building.
missing=[]
for root in [R,R.parents[1],R.parents[2]]:
 text=(root/'README.md').read_text()
 targets=re.findall(r'\]\(([^)]+)\)|src="([^"]+)"',text)
 for pair in targets:
  q=next(x for x in pair if x)
  if not q.startswith(('http:','https:','#')) and not (root/q).exists():missing.append(q)
checks['readme_relative_links_exist']=not missing
# Output metadata must not contain private absolute filesystem paths.
leaks=[]
for p in list(R.rglob('*.json'))+list(R.rglob('*.py'))+list(R.rglob('*.md')):
 if p.name=='run_all_checks.py':continue
 text=p.read_text()
 if any(q in text for q in ['/workspace/','/home/agent/','/tmp/']):leaks.append(p.name)
checks['no_private_paths_in_public_text_metadata']=not leaks
report={'passed':all(checks.values()),'checks':checks,'stl_sha256':sha(R/'model.stl'),'dimensions_mm':v['dimensions_mm'],'raw_surface_shells':v['surface_shells'],'bad_vertex_links':v['bad_vertex_links'],'layers_0_2mm':c['sampled_layers'],'original_polygon_tests':len(c['original_component_checks']),'eroded_splits_or_disappearances':sum(q['eroded_components']!=1 for q in c['original_component_checks']),'opened_splits_or_disappearances':sum(q['opened_components']!=1 for q in c['original_component_checks']),'maximum_opening_loss_fraction':c['maximum_opening_loss_fraction'],'layers_over_one_percent_opening_loss':c['layers_over_one_percent_opening_loss'],'independent_png_agreement':v['independent_png_agreement'],'canonical_scripts':canonical,'missing_links':missing,'private_path_leaks':leaks,'freeze_status':json.loads((R/'freeze-record.json').read_text())['status'] if (R/'freeze-record.json').exists() else 'pending_visual_review','limitations':['Not an actual slicer toolpath or physical print test.','All floor/roof heights are inferred; four-level completion-era body, not a 2026 legal-floor classification.','Round-window tower position unverified; circle omitted rather than invented.']}
(R/'qa-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2));assert report['passed']
# Self-omitting checksum manifest; includes every deliverable and report.
(R/'SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(R))+'\n' for p in sorted(R.rglob('*')) if p.is_file() and p.name!='SHA256SUMS'))
