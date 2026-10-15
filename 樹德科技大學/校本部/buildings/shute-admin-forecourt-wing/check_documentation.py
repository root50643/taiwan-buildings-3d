"""Check current package references, source scope and unhidden diagnostics."""
from pathlib import Path
import re,json,hashlib
R=Path(__file__).resolve().parent;missing=[]
for name in ['README.md','QA.md']:
 for target in re.findall(r'\]\(([^)]+)\)',(R/name).read_text()):
  if '://' not in target and not target.startswith('#') and not (R/target).is_file():missing.append([name,target])
required=['build_model.py','requirements.txt','model.stl','scene.blend','render_preview.py','sources.json','validation.json','reproducibility.json','check_drum_root_intervals.py','drum-root-intervals.json','drum-relief-root-samples.json.gz','dense-original.csv.gz','dense-short-samples.json.gz','component-layer-details.json.gz']
missing += [['required',f]for f in required if not (R/f).is_file()]
a=json.loads((R/'sources.json').read_text());d=json.loads((R/'dense-short-chords.json').read_text());v=json.loads((R/'validation.json').read_text());text=(R/'README.md').read_text()
checks={'all_local_links_and_required_files_exist':not missing,'partial_scope_explicit':'局部' in text and a['scope_status']=='partial_exterior_only','raw_diagnostic_false_values_retained':d['passed'] is False and d['checks']['all_first_chords_ge_0p8mm'] is False,'diagnostic_count_matches_validation':d['under_0p8mm_count']==v['unresolved_unqualified_strict_diagnostics']['original_short_count'],'current_report_stl_binding':v['stl_sha256']==hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'physical_print_limit_explicit':'實體試印' in text and '不保證' in text,'core_public_sources_present':len(a['sources'])>=2 and all(x['url'].startswith('https://')for x in a['sources'])}
out={'passed':all(checks.values()),'checks':checks,'missing':missing,'stl_sha256':v['stl_sha256']};(R/'documentation-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(out);assert out['passed']
