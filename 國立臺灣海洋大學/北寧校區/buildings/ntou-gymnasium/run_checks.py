from pathlib import Path
import os,sys,subprocess,json,hashlib
R=Path(__file__).resolve().parent
names=['check_raw_mesh','check_opposing_faces','check_component_detail','check_true_corner_masks','check_dense_surface','check_dense_backing','check_vertex_roots','check_curved_patch_roots','check_root_full_intervals','check_flag_winding','check_full_boundary_intervals','check_flag_boundaries','check_designated_roots','validate_model','check_render_rebuild','check_documentation']
rows=[]
for name in names:
 p=subprocess.run([sys.executable,'-B',str(R/(name+'.py'))],cwd=R,capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 tail=(p.stdout+'\n'+p.stderr)[-1800:].replace(str(R),'MODEL_DIR')
 rows.append(dict(script=name+'.py',exit_code=p.returncode,strict_passed=p.returncode==0,output_tail=tail));print(name,p.returncode,flush=True)
o=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),all_strict_checks_passed=all(q['strict_passed']for q in rows),independent_exception_status='pending',checks=rows,limits='Expected strict failures are preserved. Supplementary local roots and boundary classifications do not constitute author-approved exceptions. Surface winding values are diagnostics, never bulk air proof.')
(R/'qa-summary.json').write_text(json.dumps(o,indent=2));raise SystemExit(0 if o['all_strict_checks_passed']else 1)
