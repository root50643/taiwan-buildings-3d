"""Rebuild in a temporary directory and compare exact STL/OBJ hashes.
Run from this package: python rebuild_check.py
"""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,shutil
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='nhri-research-rebuild-') as tmp:
    work=Path(tmp);shutil.copy2(HERE/'build_model.py',work/'build_model.py')
    result=subprocess.run([sys.executable,str(work/'build_model.py')],text=True,capture_output=True,check=True)
    files={name:{'delivered_sha256':sha(HERE/name),'rebuilt_sha256':sha(work/name),'identical':sha(HERE/name)==sha(work/name)} for name in ['model.stl','model.obj']}
report={'passed':all(x['identical'] for x in files.values()),'python':sys.version,'files':files,'rebuild_stdout':result.stdout}
(HERE/'rebuild-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(0 if report['passed'] else 1)
