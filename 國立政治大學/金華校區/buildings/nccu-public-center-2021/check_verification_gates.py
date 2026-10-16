"""Prove that a Blender Python exception produces a nonzero tool exit."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
R=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='nccu-blender-exit-') as td:
    p=Path(td)/'intentional_failure.py';p.write_text("raise RuntimeError('Expected verification control failure')\n")
    r=subprocess.run(['blender','-b','-t','1','--python-exit-code','1','--python',str(p)],capture_output=True,text=True)
checks={'blender_exception_nonzero':r.returncode!=0,'expected_exception_seen':'Expected verification control failure' in r.stdout+r.stderr}
out={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'returncode':r.returncode,'command_flags':['-b','-t','1','--python-exit-code','1']}
(R/'verification-gates.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));raise SystemExit(0 if out['passed'] else 1)
