from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).resolve().parent
assert hashlib.sha256((R/'check_thin_features.py').read_bytes()).hexdigest()=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
rows=[]
for name in ['validate_model.py','check_raw_mesh.py','check_thin_features.py','check_all_layers.py','check_layer_components.py','check_recess_roots.py','summarize_component_losses.py','check_readme_views.py','check_preview_rebuild.py']:
 p=subprocess.run([sys.executable,str(R/name)],check=True,capture_output=True,text=True);rows.append(dict(script=name,exit_code=p.returncode));print(name,'PASS',flush=True)
for name in ['validation.json','raw-mesh-check.json','layer-component-check.json','recess-root-check.json','component-loss-summary.json','readme-view-check.json','preview-framing-check.json','preview-rebuild-check.json']:
 j=json.loads((R/name).read_text());assert j['passed'] and all(j['checks'].values()),name
j={'passed':True,'checks':{'all_scripts_exit_zero':True,'all_report_checks_true':True,'canonical_v3_sha_verified':True},'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'runs':rows}
(R/'all-checks.json').write_text(json.dumps(j,indent=2))
