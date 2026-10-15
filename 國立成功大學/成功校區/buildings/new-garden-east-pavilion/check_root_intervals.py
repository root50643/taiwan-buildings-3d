"""Complete original-mesh boundary and long-double winding checks for fixed roots.
Includes original short intervals, surface-to-inward offset, whole root intervals,
following air and next material entry, and both directions at fixed backing planes.
"""

import sys
sys.dont_write_bytecode=True
from pathlib import Path
import csv,gzip,hashlib,json,os,subprocess,tempfile
import numpy as np,trimesh
R=Path(__file__).resolve().parent
mesh=trimesh.load(R/'model.stl',process=False)
rows=json.load(gzip.open(R/'fixed-root-samples.json.gz','rt'))
from root_rules import classify
from original_rays import OriginalRays
ray=OriginalRays(mesh)
fixed=json.loads((R/'fixed-roots.json').read_text());strict=json.loads((R/'dense-short-chords.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if fixed['stl_sha256']!=sha(R/'model.stl') or fixed['detail_sha256']!=sha(R/'fixed-root-samples.json.gz'):raise RuntimeError('Fixed root input hash mismatch')
if fixed['raw_short_detail_sha256']!=sha(R/'dense-short-samples.json.gz') or strict['short_chords_sha256']!=sha(R/'dense-short-samples.json.gz'):raise RuntimeError('Raw short input hash mismatch')
raw=json.load(gzip.open(R/'dense-short-samples.json.gz','rt'));raw_by={(q['original_triangle_index'],q['sample_index']):q for q in raw}
seen=set()
for row in rows:
 q=row['original'];key=(q['original_triangle_index'],q['sample_index'])
 if key in seen or q!=raw_by.get(key):raise RuntimeError('Root evidence changed or duplicated original sample')
 seen.add(key);p=np.array(q['surface_point_mm']);n=np.array(q['original_outward_normal']);rule=classify(p,n)
 if rule is None:raise RuntimeError('Root outside supported source bounds')
 family,d,target,axis=rule;o=p-1e-5*n;L=(target-o[axis])/d[axis];anchor=o+d*L
 if family!=row['family'] or not np.array_equal(d,row['fixed_root_direction']) or not np.allclose(o,row['offset_point_mm'],atol=1e-12,rtol=0) or not np.allclose(anchor,row['anchor_point_mm'],atol=1e-12,rtol=0):raise RuntimeError('Root differs from fixed geometric rule')
 if row['inward_offset_mm']!=1e-5 or row['fixed_anchor_coordinate_axis']!=axis or row['fixed_anchor_coordinate_mm']!=target or abs(row['offset_to_anchor_length_mm']-L)>1e-12:raise RuntimeError('Root path scalars differ from fixed rule')
 for key,origin,direction in [('continuous_root',o,d),('anchor_positive_normal',anchor,n),('anchor_negative_normal',anchor,-n)]:
  v=row[key]
  if not np.allclose(v['origin_mm'],origin,atol=1e-12,rtol=0) or not np.array_equal(v['direction'],direction):raise RuntimeError('Interval ray differs from fixed rule')
  h=ray.hits(origin,direction);old=v['all_hits_mm_face']
  if len(h)!=len(old) or any(abs(a[0]-b[0])>1e-9 or a[1]!=b[1] for a,b in zip(h,old)):raise RuntimeError('Interval hits differ from current original triangles')
if seen!=set(raw_by) or len(rows)!=strict['under_0p8mm_count']:raise RuntimeError('Root sample coverage incomplete')
queries=[];query_roles=[];points=[];controls=[]
def point(row,role,p,expected):
 points.append(np.array(p,float));controls.append({'face':row['original']['original_triangle_index'],'sample':row['original']['sample_index'],'role':role,'expected_winding':expected})
def query(row,role,o,d,a,b,c):
 queries.append(list(o)+list(d)+[a,b,c,row['original']['original_triangle_index'],row['original']['sample_index']]);query_roles.append(role)
def check_ray(row,role,o,d,h,start=0.):
 if not h: raise RuntimeError('Missing material exit in '+role)
 # The original normal starts outside, so pass hits after the entry separately.
 end=h[0][0];nxt=h[1][0] if len(h)>1 else np.inf
 query(row,role,o,d,start,end,nxt)
 for f in [.01,.5,.99]:point(row,role+'_first_material',o+d*(start+(end-start)*f),1)
 delta=min(1e-5,(nxt-end)/4) if np.isfinite(nxt) else 1e-5
 point(row,role+'_immediately_after_exit_air',o+d*(end+delta),0)
 if np.isfinite(nxt):
  point(row,role+'_next_air_midpoint',o+d*((end+nxt)/2),0)
  gap2=(h[2][0]-nxt) if len(h)>2 else np.inf
  delta2=min(1e-5,gap2/4)
  point(row,role+'_next_material_reentry',o+d*(nxt+delta2),1)
 else:
  point(row,role+'_air_beyond_mesh_bounds',o+d*(end+mesh.extents.max()*2+10),0)
for row in rows:
 q=row['original'];p=np.array(q['surface_point_mm']);n=np.array(q['original_outward_normal']);eps=row['inward_offset_mm'];o=np.array(row['offset_point_mm']);d=np.array(row['fixed_root_direction']);anchor=np.array(row['anchor_point_mm']);L=row['offset_to_anchor_length_mm']
 query(row,'surface_to_offset',p,-n,0,eps,eps)
 for f in [.1,.5,.9]:point(row,'surface_to_offset_material',p-n*eps*f,1)
 point(row,'outside_original_surface_air',p+n*eps,0)
 for f in [.0,.25,.5,.75,1.]:point(row,'offset_to_fixed_anchor_material',o+d*L*f,1)
 nh=q['all_ray_intersections_mm_face'];check_ray(row,'original_short_normal',p+n*1e-6,-n,nh[1:],nh[0][0])
 for key in ['continuous_root','anchor_positive_normal','anchor_negative_normal']:
  v=row[key];check_ray(row,key,np.array(v['origin_mm']),np.array(v['direction']),v['all_hits_mm_face'])
with tempfile.TemporaryDirectory(prefix='ncku-fixed-roots-') as td:
 D=Path(td);mesh.triangles.astype('<f8').tofile(D/'triangles');np.array(queries,dtype='<f8').tofile(D/'queries');np.array(points,dtype='<f8').tofile(D/'points')
 for src,exe in [('all_boundary_screen.cpp','boundaries'),('winding_parallel.cpp','winding')]:
  subprocess.run(['g++','-O3','-fopenmp','-std=c++17',str(R/src),'-o',str(D/exe)],check=True)
 env={**os.environ,'OMP_NUM_THREADS':'1'}
 subprocess.run([str(D/'boundaries'),str(D/'triangles'),str(D/'queries'),str(D/'boundary.csv')],check=True,env=env)
 overlaps=list(csv.DictReader((D/'boundary.csv').open()))
 for q in overlaps:q['query_role']=query_roles[int(q['index'])]
 subprocess.run([str(D/'winding'),str(D/'triangles'),str(D/'points'),str(D/'winding.csv')],check=True,env=env)
 values=np.loadtxt(D/'winding.csv',delimiter=',')[:,1]
for c,p,w in zip(controls,points,values):c.update(point_mm=p.tolist(),winding=float(w),passed=bool(abs(w-c['expected_winding'])<1e-7))
checks={'all_1430_original_short_points_checked':len(rows)==1430,
        'every_complete_interval_and_surface_offset_screened':len(queries)==5*len(rows),
        'no_positive_length_triangle_boundary_overlap':not overlaps,
        'all_material_air_and_reentry_controls_pass':all(c['passed'] for c in controls)}
details={'query_rows':[[float(v) if np.isfinite(v) else None for v in q] for q in queries],
         'query_roles':query_roles,'null_endpoint_means_infinity':True,'boundary_overlaps':overlaps,'controls':controls}
with (R/'root-interval-details.json.gz').open('wb') as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0) as g:g.write(json.dumps(details,separators=(',',':')).encode())
out={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),
     'original_strict_passed':False,'original_triangle_count':len(mesh.faces),'sampled_short_points':len(rows),'complete_queries':len(queries),
     'boundary_overlap_count':len(overlaps),'winding_control_count':len(controls),'failed_controls':[q for q in controls if not q['passed']],
     'detail_file':'root-interval-details.json.gz','detail_sha256':hashlib.sha256((R/'root-interval-details.json.gz').read_bytes()).hexdigest(),
     'source_detail_sha256':hashlib.sha256((R/'fixed-root-samples.json.gz').read_bytes()).hexdigest(),
     'limits':'Bounded sampled root evidence only; strict original short-normal result remains false. All-direction wall thickness, slicing and physical printing remain unverified.'}
out['evidence_sources']={n:__import__('hashlib').sha256((R/n).read_bytes()).hexdigest() for n in ['check_root_intervals.py', 'root_rules.py', 'all_boundary_screen.cpp', 'winding_parallel.cpp', 'original_rays.py']}
(R/'root-intervals.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));raise SystemExit(0 if out['passed'] else 1)
