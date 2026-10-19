from pathlib import Path
import hashlib,json,re,urllib.parse
R=Path(__file__).resolve().parent
checks={};bad=[];link_count=0
for p in R.rglob('*.md'):
 for s in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if '://' in s or s.startswith('#') or s.startswith('mailto:'):continue
  target=s.split('#')[0];q=p.parent/urllib.parse.unquote(target);link_count+=1
  if not q.exists():bad.append(str(p.relative_to(R))+': '+s)
checks['all_relative_links_exist']=not bad
sha_bad=[];sha_count=0
for manifest in R.rglob('SHA256SUMS'):
 for line in manifest.read_text().splitlines():
  digest,name=line.split('  ',1);p=manifest.parent/name;sha_count+=1
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:sha_bad.append(p.relative_to(R).as_posix())
checks['all_sha256_entries_match']=not sha_bad
new_package=R/'神農校總區/buildings/niu-cultivation-hall-restored'
packages=sorted(p for p in R.glob('*/buildings/*') if p.is_dir())
legacy=[p for p in packages if p!=new_package]
models=[]
for p in legacy:
 q=json.loads((p/'qa-summary.json').read_text());v=json.loads((p/'validation.json').read_text());l=json.loads((p/'layer-check.json').read_text());digest=hashlib.sha256((p/'model.stl').read_bytes()).hexdigest()
 models.append({'name':p.name,'passed':q['passed'] and all(q['checks'].values()) and v['passed'] and all(v['checks'].values()) and l['passed'] and all(l['checks'].values()) and digest==q['stl_sha256']==v['stl_sha256'],'stl_sha256':digest})
checks['legacy_five_model_reports_pass']=len(models)==5 and all(m['passed'] for m in models)
checks['six_packages_present']=len(packages)==6 and new_package.is_dir()
current=json.loads((new_package/'qa/scene-check.json').read_text())
provenance=json.loads((new_package/'qa/publication/provenance.json').read_text())
pixels=json.loads((new_package/'qa/publication/clean-scene-pixels.json').read_text())
stl_digest=hashlib.sha256((new_package/'models/v1/model.stl').read_bytes()).hexdigest()
scene_digest=hashlib.sha256((new_package/'models/v1/scene.blend').read_bytes()).hexdigest()
checks['new_fixed_STL_and_cleaned_scene_bindings_match']=(stl_digest=='0827a741ec86c047708d5698c540d353a223347f25a1d883256b236bf495b70c'==current['actual_stl_sha256']==provenance['model_sha256'] and scene_digest==current['scene_sha256']==provenance['scene_metadata_cleanup']['published_scene_sha256'] and current['passed'] and pixels['all_equal'])
models.append({'name':new_package.name,'stl_sha256':stl_digest,'scene_sha256':scene_digest,'integrity_checks_passed':checks['new_fixed_STL_and_cleaned_scene_bindings_match'],'manufacturing_decision':'Independent fixed-STL CONDITIONAL GO; no physical print or support-removal test'})
checks['no_private_or_source_images']=not any('qa-private' in str(p) or p.suffix.lower() in ['.pdf','.jpg','.jpeg','.blend1'] for p in R.rglob('*') if p.is_file())
preservation=json.loads((R/'previous-model-preservation.json').read_text())
checks['previous_building_files_unchanged']=all((R/f['path']).is_file() and hashlib.sha256((R/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in preservation['files'])
checks['canonical_v3_legacy_five_models']=all(hashlib.sha256((p/'check_thin_features.py').read_bytes()).hexdigest()=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915' for p in legacy)
checks['legacy_five_saved_blend_matches_report_hash']=all(hashlib.sha256((p/'scene.blend').read_bytes()).hexdigest()==json.loads((p/'qa-summary.json').read_text())['blend_sha256'] for p in legacy)
report={'passed' :all(checks.values()),'checks':checks,'relative_links_checked':link_count,'checksum_entries_checked':sha_count,'bad_links':bad,'bad_checksums':sha_bad,'models':models,'scope':'Six packages: original five legacy reports preserved, one new package with fixed STL conditional GO. This checks package integrity/report bindings, not physical manufacturing success. School and national scope remain incomplete.'}
print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if report['passed'] else 1)
