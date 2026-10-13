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
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:sha_bad.append(str(p))
checks['all_sha256_entries_match']=not sha_bad
models=[]
for p in R.glob('*/buildings/*'):
 q=json.loads((p/'qa-summary.json').read_text());v=json.loads((p/'validation.json').read_text());l=json.loads((p/'layer-check.json').read_text());digest=hashlib.sha256((p/'model.stl').read_bytes()).hexdigest()
 models.append({'name':p.name,'passed':q['passed'] and all(q['checks'].values()) and v['passed'] and all(v['checks'].values()) and l['passed'] and all(l['checks'].values()) and digest==q['stl_sha256']==v['stl_sha256'],'stl_sha256':digest})
checks['all_model_checks_true']=len(models)==5 and all(m['passed'] for m in models)
checks['no_private_or_source_images']=not any('qa-private' in str(p) or p.suffix.lower() in ['.pdf','.jpg','.jpeg','.blend1'] for p in R.rglob('*') if p.is_file())
preservation=json.loads((R/'previous-model-preservation.json').read_text())
checks['previous_building_files_unchanged']=all((R/f['path']).is_file() and hashlib.sha256((R/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in preservation['files'])
checks['canonical_v3_all_models']=all(hashlib.sha256((p/'check_thin_features.py').read_bytes()).hexdigest()=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915' for p in R.glob('*/buildings/*'))
checks['saved_blend_matches_report_hash']=all(hashlib.sha256((p/'scene.blend').read_bytes()).hexdigest()==json.loads((p/'qa-summary.json').read_text())['blend_sha256'] for p in R.glob('*/buildings/*'))
report={'passed' :all(checks.values()),'checks':checks,'relative_links_checked':link_count,'checksum_entries_checked':sha_count,'bad_links':bad,'bad_checksums':sha_bad,'models':models,'scope':'5 cumulative original models; 2 new in increment02; school and national scope incomplete.'}
print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if report['passed'] else 1)
