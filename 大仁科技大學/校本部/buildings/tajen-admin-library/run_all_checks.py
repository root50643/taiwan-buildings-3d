"""Reproduce author checks; local exceptions remain subject to independent review."""
from pathlib import Path
import argparse,subprocess,sys,json,hashlib,gzip
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--bind-existing',action='store_true');a=p.parse_args()
steps=['validate_model.py','check_thin_features.py','check_layer_components.py','check_detailed_components.py','check_dense_samples.py','summarize_dense_samples.py','check_backed_relief_roots.py','check_support_paths.py','check_warning_post.py','check_coplanar_original_faces.py']
if not a.bind_existing:
 for n in steps:
  print('RUN',n,flush=True);subprocess.run([sys.executable,str(R/n)],cwd=R,check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
h=sha(R/'model.stl');reports=['validation.json','thin-feature-check.json','layer-component-check.json','detailed-component-check.json','dense-sampling-binding.json','dense-summary.json','backed-relief-roots.json','support-paths.json','warning-post-check.json','coplanar-original-face-check.json']
for n in reports:
 j=json.loads((R/n).read_text())
 assert j.get('stl_sha256',h)==h,n
 assert j.get('passed',True),n
 assert all(j.get('checks',{}).values()),n
 assert (R/n).stat().st_mtime>=(R/'model.stl').stat().st_mtime,n
j=json.loads((R/'dense-sampling-binding.json').read_text());assert j['csv_gzip_sha256']==sha(R/'dense-samples.csv.gz')
x=hashlib.sha256()
with gzip.open(R/'dense-samples.csv.gz','rb') as f:
 while b:=f.read(1048576):x.update(b)
assert x.hexdigest()==j['raw_csv_sha256']
d=json.loads((R/'dense-summary.json').read_text());assert d['raw_control_screen_all_expected']
b=json.loads((R/'backed-relief-roots.json').read_text());assert sum(b['family_counts'].values())==d['short_first_segments_under_0p8mm']
files=steps+reports+['build_model.py','render_preview.py','model.stl','scene.blend','parameters.json','render-manifest.json','dense-samples.csv.gz','dense_ray.cpp']+['previews/'+q.name for q in sorted((R/'previews').glob('*.png'))]
out={'status':'author_hard_checks_pass_independent_exceptions_pending','passed':True,'stl_sha256':h,'mode':'bind_existing' if a.bind_existing else 'all_scripts_rerun','bound_files':{n:sha(R/n) for n in files},'exceptions_pending_independent_review':{'individual_opening_loss_over_one_percent':39,'source_backed_relief_short_original_normals':1054},'limitations':'Specific original normals and later air remain retained. Other-direction backing/root checks are not global normal wall thickness or physical print approval.'}
(R/'qa-binding.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='bound_files'},indent=2))
