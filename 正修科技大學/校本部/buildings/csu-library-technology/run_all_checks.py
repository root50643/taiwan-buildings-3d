"""Run all strict checks, retaining real exit codes and false checks.
Specific exception approval is separate; no failed test is relabelled successful.
"""
from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).resolve().parent
scripts=['check_raw_mesh.py','validate_model.py','check_component_detail.py','check_surface_chords.py','check_corner_backing.py','check_support_roots.py','check_warning_families.py','check_render_rebuild.py','check_documentation.py']
rows=[]
for name in scripts:
 p=subprocess.run([sys.executable,str(R/name)],cwd=R,capture_output=True,text=True)
 tail=(p.stdout+p.stderr)[-5000:].replace(str(R),'.')
 rows.append(dict(script=name,exit_code=p.returncode,output_tail=tail));print(name,p.returncode,flush=True)
a=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),strict_all_exit_zero=all(v['exit_code']==0 for v in rows),specific_exception_status='pending independent review and root decision',results=rows,limits='Strict failures are preserved. Evidence checks do not waive per-polygon opening loss or original-normal short first chords.')
(R/'qa-summary.json').write_text(json.dumps(a,ensure_ascii=False,indent=2));raise SystemExit(0 if a['strict_all_exit_zero']else 1)
