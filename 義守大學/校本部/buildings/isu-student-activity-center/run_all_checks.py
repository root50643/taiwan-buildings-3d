from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).parent
jobs=[('check_raw_mesh.py','raw-mesh-check.json'),('check_component_detail.py','component-detail.json'),('check_surface_chords.py','surface-chords.json'),('check_feature_roots.py','feature-roots.json'),('check_roof_normals.py','roof-normals.json'),('validate_model.py','validation.json'),('check_render_rebuild.py','render-manifest.json'),('check_documentation.py','documentation-check.json')]
rows=[]
for script,out in jobs:
 result=subprocess.run([sys.executable,str(R/script)],capture_output=True,text=True)
 assert result.returncode==0,(script,result.stdout[-2000:],result.stderr[-2000:])
 d=json.loads((R/out).read_text());assert d.get('passed') is True and all(d['checks'].values()),(script,d['checks']);assert d['stl_sha256']==hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()
 rows.append({'script':script,'report':out,'exit_code':result.returncode,'checks':d['checks'],'all_checks_true':True})
r={'passed':True,'checks':{'eight_programs_exit_zero':len(rows)==8,'all_report_checks_true':all(v['all_checks_true']for v in rows)},'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'reports':rows,'publication':'Author QA complete; independent reviewer and unified writer control publication.'};(R/'qa-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
