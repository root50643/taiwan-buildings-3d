"""Run all original checks; preserve strict failures and normalized trace output.
Nonzero strict statuses are not converted to passes. Independent review is required.
"""
from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).resolve().parent
names=['check_raw_mesh.py','check_opposing_faces.py','check_component_detail.py','check_true_corner_masks.py','check_dense_surface.py','check_dense_backing.py','check_vertex_roots.py','check_short_winding.py','check_all_after_boundaries.py','check_boundary_interval.py','check_designated_roots.py','check_warning_families.py','validate_model.py','check_render_rebuild.py','check_documentation.py']
rows=[]
for name in names:
 p=subprocess.run([sys.executable,name],cwd=R,capture_output=True,text=True);out=(p.stdout+p.stderr).replace(str(R),'[MODEL_DIR]');rows.append(dict(script=name,exit_code=p.returncode,output=out));print(name,p.returncode,flush=True)
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),all_automatic_checks_pass=all(q['exit_code']==0 for q in rows),independent_review='PENDING: no author approval of warnings',commands=rows)
(R/'qa-summary.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));raise SystemExit(0 if r['all_automatic_checks_pass']else 1)
