"""Bound hard QA. Raw parity flags stay visible, resolved separately by all-triangle winding.
--bind-existing avoids repeating complete expensive sampling when all SHA-bound reports exist.
"""
from pathlib import Path
import json,hashlib,sys,subprocess,argparse
R=Path(__file__).resolve().parent;ap=argparse.ArgumentParser();ap.add_argument('--bind-existing',action='store_true');a=ap.parse_args();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();current=sha(R/'model.stl')
tasks={'validate_model.py':'validation.json','check_thin_features.py':'thin-feature-check.json','check_layer_components.py':'layer-component-check.json','check_detailed_components.py':'detailed-component-check.json','check_dense_samples.py':'dense-sampling-binding.json','summarize_dense_samples.py':'dense-summary.json','check_control_solid_angle.py':'control-solid-angle.json','check_short_roots.py':'short-root-summary.json','summarize_short_roots.py':'short-root-groups.json','check_support_paths.py':'support-paths.json'}
checks={};bindings={}
for script,report in tasks.items():
 if not a.bind_existing:subprocess.run([sys.executable,str(R/script)],cwd=R,check=True)
 p=R/report;j=json.loads(p.read_text());assert p.stat().st_mtime>=(R/'model.stl').stat().st_mtime
 if 'stl_sha256' in j:assert j['stl_sha256']==current
 assert j.get('passed',True) and all(j.get('checks',{}).values()),report
 bindings[report]={'script_sha256':sha(R/script),'report_sha256':sha(p),'stl_sha256':current};checks[report]=True
raw=json.loads((R/'dense-summary.json').read_text());resolved=json.loads((R/'control-solid-angle.json').read_text());flags={(x['face'],x['sample']) for x in raw['control_failures']};handled={(x['original_dense_sample']['face'],x['original_dense_sample']['sample']) for x in resolved['rows']};assert flags==handled and resolved['passed'];checks['every_raw_control_flag_resolved_without_erasure']=True
assert sha(R/'check_thin_features.py')=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
assert sha(R/'check_layer_components.py')=='365e437af0d3d6defc2f52adf3e8601ac3643a14e15e03c8c8610b10bb8061a5'
j={'stl_sha256':current,'passed':all(checks.values()),'checks':checks,'bindings':bindings,'raw_control_flags':len(flags),'independent_approval':'PENDING. Author hard QA and finite-direction roots do not approve original short normal segments or claim global wall thickness / physical print.'};(R/'qa-summary.json').write_text(json.dumps(j,indent=2));print('author hard QA bound; independent classification approval remains pending')
