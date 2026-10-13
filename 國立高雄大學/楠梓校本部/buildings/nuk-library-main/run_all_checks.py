"""Run all actual-file checks. Any nonzero subprocess or false check rejects release."""
from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).resolve().parent
for script in ['validate_model.py','check_valid_sections.py','thin_canonical_v2.py']:
 subprocess.run([sys.executable,str(R/script)],check=True,cwd=R)
reports={x:json.loads((R/x).read_text()) for x in ['validation.json','valid-sections.json','thin-feature-check.json']}
checks={name:bool(r.get('passed')) and bool(r.get('checks')) and all(r['checks'].values()) for name,r in reports.items()}
checks['stl_hash_matches_validation']=reports['validation.json']['stl_sha256']==hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()
r={'passed':all(checks.values()),'checks':checks,'physical_print_test':False,'actual_slicer_toolpath_test':False}
(R/'qa-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
raise SystemExit(0 if r['passed'] else 1)
