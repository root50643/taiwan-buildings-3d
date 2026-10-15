"""Screen each complete first-root/next interval against every original triangle.
Retain complete original intersections and add all-triangle solid-angle controls.
"""
from pathlib import Path
import tempfile,subprocess,os,json,gzip,csv,hashlib
import numpy as np,trimesh
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',process=False)
rows=json.load(gzip.open(R/'drum-relief-root-samples.json.gz','rt'));queries=[];pts=[];controls=[]
for q in rows:
 p=np.array(q['surface_point_mm']);d=np.array(q['fixed_root_direction']);o=p+d*1e-5;h=q['all_root_hits_mm_face'];end=h[0][0];nxt=h[1][0] if len(h)>1 else np.inf
 queries.append(list(o)+list(d)+[0,end,nxt,q['original_triangle_index'],q['sample_index']])
 for f in [.01,.25,.5,.75,.99]:
  pts.append(o+d*(end*f));controls.append({'face':q['original_triangle_index'],'sample':q['sample_index'],'role':'first_root_material','fraction':f,'expected_winding':1})
 delta=min(1e-5,(nxt-end)/4) if np.isfinite(nxt) else 1e-5
 pts.append(o+d*(end+delta));controls.append({'face':q['original_triangle_index'],'sample':q['sample_index'],'role':'after_first_root_exit_air','offset_after_exit_mm':delta,'expected_winding':0})
with tempfile.TemporaryDirectory(prefix='shute-root-intervals-') as td:
 D=Path(td);m.triangles.astype('<f8').tofile(D/'tri');np.array(queries,dtype='<f8').tofile(D/'queries');np.array(pts,dtype='<f8').tofile(D/'points')
 for src,exe in [('all_boundary_screen.cpp','screen'),('winding_parallel.cpp','wind')]:subprocess.run(['g++','-O3','-fopenmp','-std=c++17',str(R/src),'-o',str(D/exe)],check=True)
 env={**os.environ,'OMP_NUM_THREADS':'1'}
 subprocess.run([str(D/'screen'),str(D/'tri'),str(D/'queries'),str(D/'overlaps.csv')],check=True,env=env)
 overlaps=list(csv.DictReader(open(D/'overlaps.csv')))
 subprocess.run([str(D/'wind'),str(D/'tri'),str(D/'points'),str(D/'winding.csv')],check=True,env=env)
 values=np.loadtxt(D/'winding.csv',delimiter=',')[:,1]
for c,p,w in zip(controls,pts,values):c.update(point_mm=p.tolist(),winding=float(w),passed=bool(abs(w-c['expected_winding'])<1e-7))
checks={'every_short_sample_root_screened':len(queries)==len(rows),'no_positive_length_original_boundary_in_first_root_or_next_interval':not overlaps,'all_full_first_root_material_controls_pass':all(c['passed']for c in controls if c['role']=='first_root_material'),'all_after_root_exit_controls_are_air':all(c['passed']for c in controls if c['role']=='after_first_root_exit_air')}
details={'queries':[[float(v) if np.isfinite(v) else None for v in q]for q in queries],'null_next_interval_endpoint_means_infinity':True,'overlaps':overlaps,'controls':controls}
with (R/'drum-root-interval-details.json.gz').open('wb') as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0) as g:g.write(json.dumps(details,separators=(',',':')).encode())
out={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'root_rays':len(rows),'original_triangles':len(m.faces),'complete_root_and_next_boundary_overlap_count':len(overlaps),'winding_controls':len(controls),'failed_controls':[c for c in controls if not c['passed']],'detail_file':'drum-root-interval-details.json.gz','detail_sha256':hashlib.sha256((R/'drum-root-interval-details.json.gz').read_bytes()).hexdigest(),'method':'Every nominated original root ray screened against every original triangle over its complete first-root and next interval (including infinity). Same long-double finite-plane clipping and tolerances as the full original-normal screen. Five first-root stations including midpoint and just-after-exit are tested with all-triangle compensated long-double solid-angle winding.','limits':'Evidence for finite selected roots only, not global wall thickness or a print guarantee.'}
(R/'drum-root-intervals.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert out['passed']
