"""Rebuild in a clean temporary directory and compare exact STL SHA-256."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
p=Path(__file__).resolve().parent
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
original=sha(p/'model.stl')
with tempfile.TemporaryDirectory() as t:
 q=Path(t);shutil.copy2(p/'build_model.py',q/'build_model.py')
 subprocess.run([sys.executable,str(q/'build_model.py')],check=True)
 rebuilt=sha(q/'model.stl')
r={'passed':original==rebuilt,'original_stl_sha256':original,'rebuilt_stl_sha256':rebuilt,'method':'Independent clean-directory execution of the delivered source script; exact STL byte comparison.','python':sys.version}
(p/'rebuild_check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));raise SystemExit(0 if r['passed'] else 1)
