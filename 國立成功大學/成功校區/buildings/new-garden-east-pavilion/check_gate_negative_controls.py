"""Adversarial immutable gate, stale-evidence and optimized exit-code controls.
Runs only on disposable copies; preserves this package's model and evidence.
The explicit bootstrap switch is author-only. The final recorded run uses the
ordinary frozen gate and requires a successful unmodified baseline first.
"""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
import argparse,gzip,hashlib,json,shutil,subprocess,tempfile,tarfile,io
from integrity_utils import sha,source_inventory,write_json,require
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--author-bootstrap',action='store_true');ap.add_argument('--evidence-dir',type=Path);args=ap.parse_args()
E=args.evidence_dir or Path(tempfile.mkdtemp(prefix='east-gate-preserved-'));E.mkdir(parents=True,exist_ok=True)
require(not E.resolve().is_relative_to(R),'Evidence directory must be outside the package')
mode=['--preflight','--check-inventory'] if args.author_bootstrap else []
def call(D,script,flags=()):
 return subprocess.run([sys.executable,*flags,str(D/script)],capture_output=True,text=True)
def gate(D):return subprocess.run([sys.executable,str(D/'validate_model.py'),*mode],capture_output=True,text=True)
def load_report(p):return json.loads(p.read_text())
def gz_write(p,rows):
 with p.open('wb') as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0) as g:g.write(json.dumps(rows,separators=(',',':')).encode())
base=gate(R);require(base.returncode==0 and json.loads(base.stdout)['passed'],'Unmodified gate baseline must pass')
rows=[]
def record(name,p,ok):
 (E/(name+'.stdout.txt')).write_text(p.stdout);(E/(name+'.stderr.txt')).write_text(p.stderr)
 current={f.relative_to(D).as_posix():f for f in D.rglob('*') if f.is_file()}
 changed=[n for n,f in current.items() if not (R/n).is_file() or sha(f)!=sha(R/n)]
 deleted=[f.relative_to(R).as_posix() for f in R.rglob('*') if f.is_file() and f.relative_to(R).as_posix() not in current]
 with tarfile.open(E/(name+'.changed-files.tar.gz'),'w:gz') as archive:
  for n in changed:archive.add(current[n],arcname=n)
 write_json(E/(name+'.json'),{'name':name,'returncode':p.returncode,'rejected':bool(ok),'changed_files':changed,'deleted_files':deleted,'base_stl_sha256':sha(R/'model.stl')})
 rows.append({'name':name,'rejected':bool(ok),'returncode':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr.encode()).hexdigest()})
with tempfile.TemporaryDirectory(prefix='east-qa-controls-') as temp:
 T=Path(temp)
 def fixture(name):
  D=T/name;shutil.copytree(R,D);return D
 mutations={
  'changed_preview':lambda D:(D/'previews/front.png').write_bytes((D/'previews/front.png').read_bytes()+b'mutated'),
  'private_readme_path':lambda D:(D/'README.md').write_text((D/'README.md').read_text()+'\n'+'/'+'workspace/'+'private/audit-secret\n'),
  'noop_checker':lambda D:(D/'check_raw_mesh.py').write_text('raise SystemExit(0)\n'),
  'extra_payload':lambda D:(D/'extra.txt').write_text('unexpected'),
  'missing_payload':lambda D:(D/'README.md').unlink(),
  'nested_manifest':lambda D:((D/'nested').mkdir(),(D/'nested/freeze-manifest.json').write_text('{}')),
  'nested_sums':lambda D:((D/'nested').mkdir(),(D/'nested/SHA256SUMS').write_text('extra')),
  'nested_privacy_report':lambda D:((D/'nested').mkdir(),(D/'nested/artifact-integrity.json').write_text('{}')),
  'missing_gate_controls':lambda D:(D/'gate-negative-controls.json').unlink(missing_ok=True),
 }
 for name,mutate in mutations.items():
  D=fixture(name);mutate(D)
  p=call(D,'validate_model.py') if name=='missing_gate_controls' else gate(D)
  record(name,p,p.returncode!=0 and json.loads(p.stdout)['passed'] is False)
 for name,kind in [('raw_short_modified','raw'),('fixed_root_modified','fixed'),('raw_short_omitted','omit')]:
  D=fixture(name);n='fixed-root-samples.json.gz' if kind=='fixed' else 'dense-short-samples.json.gz';q=json.load(gzip.open(D/n,'rt'))
  if kind=='omit':q.pop()
  elif kind=='fixed':q[0]['offset_point_mm'][0]+=.1
  else:q[0]['surface_point_mm'][0]+=.1
  gz_write(D/n,q);p=gate(D);record(name,p,p.returncode!=0 and json.loads(p.stdout)['passed'] is False)
  # Rehash the edited detail upstream. Numerical checkers still must reject it.
  report='fixed-roots.json' if kind=='fixed' else 'dense-short-chords.json';key='detail_sha256' if kind=='fixed' else 'short_chords_sha256'
  report_data=load_report(D/report);report_data[key]=sha(D/n);write_json(D/report,report_data)
  checker='check_root_intervals.py' if kind=='fixed' else 'check_fixed_roots.py'
  p=call(D,checker);record(name+'_rehash_direct_checker',p,p.returncode!=0 and ('RuntimeError' in p.stderr))
 D=fixture('stale_checker_reseal');(D/'check_raw_mesh.py').write_text((D/'check_raw_mesh.py').read_text()+'\n# changed after evidence\n')
 p=call(D,'seal_package.py');record('stale_checker_reseal',p,p.returncode!=0 and 'every_report_generator_source_is_current' in p.stderr and 'false' in p.stderr)
 D=fixture('optimized_zero_normal');data=bytearray((D/'model.stl').read_bytes());data[84:96]=b'\0'*12;(D/'model.stl').write_bytes(data)
 p=call(D,'check_raw_mesh.py',['-O']);q=load_report(D/'raw-mesh-check.json');record('optimized_zero_normal',p,p.returncode!=0 and q['passed'] is False and q['checks']['original_normals_unit'] is False)
 D=fixture('optimized_thin_root');shutil.copyfile(D/'negative-control-results/narrow_root.stl',D/'model.stl')
 p=call(D,'check_component_detail.py',['-O']);record('optimized_thin_root',p,p.returncode!=0 and (D/'first-layer-failure.json').exists() and 'vanishes or splits' in p.stderr)
 D=fixture('blender_identity_failure')
 (D/'change_identity.py').write_text("from pathlib import Path\nimport bpy,runpy\nnext(o for o in bpy.context.scene.objects if o.type=='MESH').location.x=1\nrunpy.run_path(str(Path(__file__).parent/'probe_scene.py'),run_name='__main__')\n")
 p=subprocess.run(['flock',str(Path(tempfile.gettempdir())/'ncku-render.lock'),'blender','--python-exit-code','1','-b',str(D/'scene.blend'),'--python',str(D/'change_identity.py')],capture_output=True,text=True)
 q=load_report(D/'scene-check.json');record('blender_identity_failure',p,p.returncode!=0 and q['passed'] is False and q['checks']['identity_transforms'] is False)
checks={q['name']:q['rejected'] for q in rows}
report={'passed':all(checks.values()),'checks':checks,'stl_sha256':sha(R/'model.stl'),'source_files':source_inventory(R),'tested_gate_mode':'explicit_author_bootstrap' if args.author_bootstrap else 'default_frozen_full_inventory','unmodified_baseline_passed':True,'controls':rows}
write_json(R/'gate-negative-controls.json',report);print(json.dumps(report,indent=2));require(report['passed'],'Adversarial gate control failed')
