"""Re-run all independent digital checks on the unmodified delivered model."""
from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).resolve().parent
checks=[('check_raw_mesh.py','raw-mesh-check.json'),('check_thin_features.py','thin-feature-check.json'),('check_layer_components.py','layer-component-check.json'),('validate_model.py','validation.json'),('check_preview_rebuild.py','preview-rebuild-check.json'),('check_readme_views.py','readme-view-check.json'),('inspect-hcu-roots-verify.py','inspect-hcu-roots-summary.json')]
rows=[]
for script,report in checks:
 p=subprocess.run([sys.executable,str(R/script)],capture_output=True,text=True)
 if script=='check_thin_features.py':
  original=json.loads((R/report).read_text()); rows0=original.get('layers',[])
  c={'canonical_source_sha_matches':hashlib.sha256((R/script).read_bytes()).hexdigest()=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915','canonical_exit_zero':p.returncode==0,'reported_samples_complete':len(rows0)==original.get('sampled_layers') and len(rows0)>0}
  report='canonical-script-check.json';(R/report).write_text(json.dumps({'passed':all(c.values()),'checks':c,'source_report':'thin-feature-check.json','note':'Canonical v3 report has no passed field; its unchanged assertions are verified by exit code and exact approved script SHA. The 0.2mm per-original-Polygon checks are separate.'},indent=2))
 data=json.loads((R/report).read_text()) if (R/report).exists() else {}
 ok=p.returncode==0 and data.get('passed')is True and all(data.get('checks',{}).values())
 rows.append({'script':script,'report':report,'exit_code':p.returncode,'passed':ok})
 print(script,p.returncode,ok,flush=True)
 if not ok:print(p.stdout,p.stderr)
passed=all(q['passed']for q in rows)
summary={'passed':passed,'ready_for_independent_review':passed,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'checks':{q['script']:q['passed']for q in rows},'runs':rows,'limitations':'Digital finite-sample checks, not physical print validation or a continuous global minimum-wall proof.'}
(R/'all-checks.json').write_text(json.dumps(summary,indent=2));raise SystemExit(0 if passed else 1)
