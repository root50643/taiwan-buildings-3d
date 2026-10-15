"""Reproduce all strict outputs; pending exceptions never convert exit1 into pass."""
from pathlib import Path
import subprocess,sys,json,hashlib,os
sys.dont_write_bytecode=True
os.environ["PYTHONDONTWRITEBYTECODE"]="1"
R=Path(__file__).resolve().parent
scripts=['check_raw_mesh.py','check_opposing_faces.py','check_component_detail.py','check_true_corner_masks.py','check_dense_surface.py','check_flag_winding.py','check_all_after_boundaries.py','check_full_boundary_intervals.py','check_designated_roots.py','validate_model.py','check_render_rebuild.py','check_documentation.py']
rows=[]
for s in scripts:
 p=subprocess.run([sys.executable,str(R/s)],cwd=R,capture_output=True,text=True)
 output=(p.stdout+p.stderr).replace(str(R),'.')
 rows.append(dict(script=s,exit_code=p.returncode,output=output));print(s,p.returncode,flush=True)
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),strict_all_exit_zero=all(q['exit_code']==0 for q in rows),independent_exception_status='pending; author cannot approve',runs=rows)
(R/'qa-summary.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));raise SystemExit(0 if r['strict_all_exit_zero'] else 1)
