from pathlib import Path
import argparse,subprocess,sys,shutil,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output-dir',required=True);args=p.parse_args()
dst=Path(args.output_dir).resolve();(dst/'source').mkdir(parents=True,exist_ok=True);(dst/'models/v1').mkdir(parents=True,exist_ok=True)
shutil.copy2(ROOT/'parameters.json',dst/'parameters.json');shutil.copy2(ROOT/'source/build_model.py',dst/'source/build_model.py')
r=subprocess.run([sys.executable,str(dst/'source/build_model.py')],capture_output=True)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
checks={n:{'candidate_sha256':sha(ROOT/'models/v1'/n),'rebuilt_sha256':sha(dst/'models/v1'/n),'exact_bytes_equal':(ROOT/'models/v1'/n).read_bytes()==(dst/'models/v1'/n).read_bytes()} for n in ['model.stl','model.obj']} if r.returncode==0 else {}
result={'returncode':r.returncode,'files':checks};(dst/'rebuild-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(0 if checks and all(x['exact_bytes_equal'] for x in checks.values()) else 1)
