"""Full first-root and following interval screen against all original faces."""
from pathlib import Path
import tempfile,subprocess,os,json,gzip,csv,hashlib,numpy as np,trimesh
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',process=False)
with gzip.open(R/'curved-patch-roots.json.gz','rt') as f:rows=json.load(f)['rows']
queries=[]
for q in rows:
 h=q['root_all_hits'];queries.append(q['root_origin']+q['inward_root']+[0,h[0][0],h[1][0] if len(h)>1 else np.inf,q['face'],q['sample']])
with tempfile.TemporaryDirectory() as td:
 D=Path(td);m.triangles.astype('<f8').tofile(D/'tri');np.array(queries,dtype='<f8').tofile(D/'queries');subprocess.run(['g++','-O3','-fopenmp',str(R/'all_boundary_screen.cpp'),'-o',str(D/'screen')],check=True);subprocess.run([str(D/'screen'),str(D/'tri'),str(D/'queries'),str(D/'out.csv')],check=True,env={**os.environ,'OMP_NUM_THREADS':'4'});overlaps=list(csv.DictReader(open(D/'out.csv')))
report=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),root_rays=len(rows),original_triangles=len(m.faces),overlaps=overlaps,checks={'no_positive_length_original_boundary_in_first_root_or_next_interval':not overlaps},limits='Complete ray intervals at declared plane/parallel/endpoint tolerances; finite selected root directions, not global thickness. Root first-material controls remain in curved-patch-roots.json.gz.')
(R/'root-full-intervals.json').write_text(json.dumps(report,indent=2));print(report['checks']);raise SystemExit(0 if not overlaps else 1)
