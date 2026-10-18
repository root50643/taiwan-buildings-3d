"""Read-only baseline publication file/index scope; no working-tree mutation."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--package-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists():raise RuntimeError('Fresh report required')
 env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
 def git(*args):return subprocess.check_output(['git','-C',str(a.repo),'-c','core.quotepath=false',*args],env=env)
 base=git('rev-parse','6e68368').decode().strip();prefix=a.package_root.resolve().relative_to(a.repo.resolve()).as_posix()
 changed=git('diff','--name-only',base,'--').decode().splitlines()
 allowed={prefix+'/'+n for n in ['README.md','PUBLICATION.md','QA.md','source/validate_publication.py','models/v1/scene.blend','models/v2/scene.blend']}
 outside=[p for p in git('diff-tree','--no-commit-id','--name-only','-r',base).decode().splitlines() if not p.startswith(prefix+'/')]
 indexes=[]
 for name in outside:
  old=git('show',base+':'+name);current=(a.repo/name).read_bytes()
  indexes.append({'path':name,'original_sha256':sha(old),'current_sha256':sha(current),'byte_identical':old==current})
 historical=[]
 for name in git('ls-tree','-r','--name-only',base,'--',prefix+'/qa/publication-incremental').decode().splitlines():
  if not name.endswith('.json'):continue
  old=git('show',base+':'+name)
  try:r=json.loads(old)
  except ValueError:continue
  if isinstance(r.get('checks'),dict) and len(r['checks'])==13:
   current=(a.repo/name).read_bytes();historical.append({'path':name,'original_sha256':sha(old),'current_sha256':sha(current),
     'byte_identical':old==current,'original_check_count':len(r['checks']),'original_all_checks_true':all(v is True for v in r['checks'].values()),'original_passed':r.get('passed')})
 checks={'tracked_diff_exactly_six_declared_metadata_or_prose_files':set(changed)==allowed,
   'eight_publication_indexes_byte_identical':len(indexes)==8 and all(x['byte_identical'] for x in indexes),
   'initial_13_true_report_retained_unchanged':bool(historical) and all(x['byte_identical'] and x['original_all_checks_true'] for x in historical)}
 report={'passed':all(checks.values()),'checks':checks,'baseline_commit':base,'tracked_changed_paths':changed,'eight_index_bindings':indexes,
  'historical_reports':historical,'note':'The historical 13-true scanner did not inspect decompressed BLEND UI history. Its result is retained, while separate binary checks explicitly record before false/two findings and after true/zero. Untracked additions are new repair evidence and are not treated as baseline files.'}
 a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':report['passed'],'checks':checks,'index_count':len(indexes),'historical_report_count':len(historical)}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
