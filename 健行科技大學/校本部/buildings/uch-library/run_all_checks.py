"""Run every check without converting strict failures into passes. Exit1 remains pending review."""
from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).parent
scripts=['check_raw_mesh.py','check_component_detail.py','check_surface_chords.py','check_curved_glazing_edges.py','check_support_roots.py','check_warning_families.py','validate_model.py','check_render_rebuild.py','check_documentation.py']
rows=[]
for name in scripts:
 p=subprocess.run([sys.executable,str(R/name)],capture_output=True,text=True)
 rows.append({'script':name,'exit_code':p.returncode,'stdout_tail':p.stdout[-1000:],'stderr_tail':p.stderr[-1200:]})
 print(name,p.returncode,flush=True)
report={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'all_strict_checks_pass':all(x['exit_code']==0 for x in rows),'independent_exception_status':'pending','checks':rows}
(R/'qa-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(0 if report['all_strict_checks_pass'] else 1)
