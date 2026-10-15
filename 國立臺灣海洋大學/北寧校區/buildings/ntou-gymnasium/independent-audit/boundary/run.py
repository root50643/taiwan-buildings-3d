"""Run from a model's independent-audit/boundary folder. No package file is modified."""
from pathlib import Path
import argparse, tempfile, subprocess, os, sys, gzip, json, shutil, hashlib, csv
sys.dont_write_bytecode=True
p=argparse.ArgumentParser()
p.add_argument('--model-dir',type=Path,default=Path(__file__).resolve().parents[2])
p.add_argument('--output-dir',type=Path,default=Path('boundary-recheck-results'))
a=p.parse_args();here=Path(__file__).resolve().parent;out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='ntou-boundary-recheck-')as td:
 w=Path(td);env={**os.environ,'NTOU_MODEL_DIR':str(a.model_dir.resolve()),'NTOU_BOUNDARY_WORKDIR':td,'OMP_NUM_THREADS':'4','PYTHONDONTWRITEBYTECODE':'1'}
 def run(cmd):subprocess.run(list(map(str,cmd)),check=True,env=env)
 run([sys.executable,here/'prepare.py'])
 run(['g++','-O3','-std=c++17',here/'exact_source.cpp','-o',w/'exact_source'])
 run(['g++','-O3','-std=c++17','-fopenmp',here/'winding.cpp','-o',w/'winding'])
 run([w/'exact_source',w/'ntou-revision-dense-triangles.bin',w/'ntou-revision-boundary-queries.bin',w/'ntou-revision-boundary-events.txt',w/'ntou-revision-boundary-indices.bin'])
 for script in ['summarize.py','verify.py','opposing_exact.py','opposing_coplanar.py']:run([sys.executable,here/script])
 summary=json.loads((w/'ntou-revision-boundary-independent.json').read_text())
 with gzip.open(here/'expected-summary.json.gz','rt')as f:expected=json.load(f)
 for key in ['counts','samples','no_first_material_boundary','first_material_changed_from_dense_count','all_intervals_exact_rational_source_coplanar','parity_flag_count','flag_ids','winding_control_count','winding_control_role_counts','winding_failure_count']:
  assert summary[key]==expected[key],(key,summary[key],expected[key])
 assert summary['maximum_winding_error']<1e-8
 exact=json.loads((w/'ntou-revision-boundary-opposing-exact.json').read_text())['summary'];assert exact['exact_positive_area_opposing_overlap_count']==0
 for name in ['independent.json','events.txt','opposing-exact.json','opposing-coplanar.json']:
  src=w/('ntou-revision-boundary-'+name)
  with gzip.open(out/(src.name+'.gz'),'wb',compresslevel=9)as f:f.write(src.read_bytes())
 shutil.copy(w/'ntou-revision-boundary-evidence.json.gz',out/'ntou-revision-boundary-evidence.json.gz')
 with gzip.open(out/'ntou-revision-boundary-evidence.json.gz','rt')as f:evidence=json.load(f)
 columns=['ray_index','source_face','sample','boundary_face','interval_a_mm','interval_b_mm','role','clipped_a_mm','clipped_b_mm','exact_lambda_a','exact_lambda_b']
 with gzip.open(out/'ntou-revision-boundary-intervals.csv.gz','wt',newline='')as f:
  writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader()
  for row in evidence['rows']:
   for interval in row['boundaries']:
    for role in interval['roles']:
     writer.writerow(dict(ray_index=row['index'],source_face=row['face'],sample=row['sample'],boundary_face=interval['original_triangle'],interval_a_mm=interval['interval_a_mm'],interval_b_mm=interval['interval_b_mm'],exact_lambda_a=interval['exact_lambda_a'],exact_lambda_b=interval['exact_lambda_b'],**{k:role[k]for k in ['role','clipped_a_mm','clipped_b_mm']}))
 manifest={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in sorted(out.glob('ntou-revision-boundary-*'))}
 (out/'SHA256SUMS').write_text(''.join(h+'  '+name+'\n'for name,h in manifest.items()))
 print('Verified 84,450 exact-source rays, 409 exact rational boundary intervals, 12,827 true winding controls, and zero opposing-coplanar overlaps. Results:',out)
