"""Run original checks without hiding strict failures. Exit nonzero pending exceptions."""
from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).resolve().parent
scripts=['check_raw_mesh.py','check_opposing_faces.py','check_component_detail.py','check_surface_chords.py','check_corner_backing.py','check_dense_transitions.py','check_dense_backing.py','check_low_roots.py','check_crown_roots.py','check_warning_families.py','check_true_corner_masks.py','check_window_piers.py','validate_model.py','check_render_rebuild.py','check_documentation.py']
rows=[]
for f in scripts:
 p=subprocess.run([sys.executable,f],cwd=R,capture_output=True,text=True)
 # Child traces use relative script names; sanitize temporary directory prefixes only in summary.
 err=p.stderr.replace(str(R)+'/','')
 rows.append({'script':f,'exit_code':p.returncode,'stderr_tail':err[-1200:]})
report={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'all_strict_checks_pass':all(x['exit_code']==0 for x in rows),'independent_exception_status':'pending','runs':rows,'limits':'Supplementary root evidence does not override strict false or authorize publication.'}
(R/'qa-summary.json').write_text(json.dumps(report,indent=2));print(report);raise SystemExit(0 if report['all_strict_checks_pass'] else 1)
