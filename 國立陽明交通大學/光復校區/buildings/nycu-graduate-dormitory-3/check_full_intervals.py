"""Recompute exact-source short normal and fixed-root complete intervals in long double.
Retain full event lists, sweep parallel original triangles, and independently
check material/air with whole-original-mesh solid angle (not parity alone).
"""
from pathlib import Path
import json,gzip,hashlib,tempfile,subprocess,os
import numpy as np,trimesh
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',process=False);T=m.triangles
r=json.loads((R/'corner-roots.json').read_text());assert r['passed'];rows=json.load(gzip.open(R/r['witness_file'],'rt'))
W=np.array([[1/3]*3,[.98,.01,.01],[.01,.98,.01],[.01,.01,.98],[.495,.495,.01],[.01,.495,.495],[.495,.01,.495],[.49,.49,.02],[.49,.02,.49],[.02,.49,.49]],dtype=np.longdouble)
TT=T.astype(np.longdouble);NN=np.cross(TT[:,1]-TT[:,0],TT[:,2]-TT[:,0]);NN/=np.linalg.norm(NN,axis=1)[:,None]
def parse(line):
 a,b=line.split('|');hits=[];bounds=[]
 for v in a.split(';')[1:]:
  t,f,u,w,nd=map(float,v.split(','));e={'face':int(f),'barycentric':[1-u-w,u,w],'normal_dot':nd}
  if hits and abs(t-hits[-1]['t'])<1e-10:hits[-1]['events'].append(e)
  else:hits.append({'t':t,'events':[e]})
 for v in b.strip().split(';')[1:]:
  a,b,f,plane,nd=map(float,v.split(','));bounds.append({'a':a,'b':b,'face':int(f),'plane_residual':plane,'normal_dot':nd})
 return hits,bounds
points=[];controls=[];outrows=[]
def add(role,p,expect,bind):
 controls.append({'point_mm':np.array(p,dtype=float).tolist(),'expected_winding':expect,'role':role,**bind});points.append(p)
with tempfile.TemporaryDirectory()as td:
 D=Path(td);T.astype('<f8').tofile(D/'tri.bin')
 subprocess.run(['g++','-O3','-std=c++17',str(R/'strict_exact_source_intervals.cpp'),'-o',str(D/'strict')],check=True)
 subprocess.run(['g++','-O3','-fopenmp','-std=c++17',str(R/'winding_parallel.cpp'),'-o',str(D/'winding')],check=True)
 ids=np.array([[x['original_triangle_index'],x['sample_index']]for x in rows],dtype='<i4');ids.tofile(D/'ids.bin')
 for mode in ['normal','root']:
  qs=[]
  for q in rows:
   p=np.array(q['surface_point_mm']);n=np.array(q['original_outward_normal']);d=-n if mode=='normal' else np.array(q['fixed_root_direction']);o=p+n*1e-5 if mode=='normal' else p-d*1e-6;qs.append([o,d])
  np.array(qs,dtype='<f8').tofile(D/'query.bin')
  cmd=[str(D/'strict'),str(D/'tri.bin'),str(D/'query.bin'),str(D/'events.txt'),str(D/'ids.bin')]
  if mode=='root':cmd+=['root']
  subprocess.run(cmd,check=True)
  for q,line in zip(rows,(D/'events.txt').read_text().splitlines()):
   fi=q['original_triangle_index'];si=q['sample_index'];p=W[si]@TT[fi];d=-NN[fi] if mode=='normal' else np.array(q['fixed_root_direction'],dtype=np.longdouble);d/=np.linalg.norm(d);o=p+NN[fi]*np.longdouble('0.00001') if mode=='normal' else p-d*np.longdouble('0.000001');h,b=parse(line);assert len(h)>=2
   lo,hi=h[0]['t'],h[1]['t'];nxt=h[2]['t']if len(h)>2 else None
   overlaps=[]
   for x in b:
    for role,a,z in [('first-material',lo,hi),('next-air',hi,nxt if nxt is not None else float('inf'))]:
     aa=max(a+1e-10,x['a']);zz=min(z-1e-10,x['b'])
     if zz-aa>1e-9:overlaps.append({'role':role,'a':aa,'b':zz,'boundary':x})
   saved=q['original_first_material_mm']if mode=='normal'else q['continuous_root_first_material_mm'];entry=1e-5 if mode=='normal'else 1e-6
   checks={'entry_at_declared_offset':abs(lo-entry)<2e-7,'first_interval_matches_retained_original':abs(hi-lo-saved)<2e-5,'source_entry_inward':all(x['normal_dot']<0 for x in h[0]['events']),'first_exit_outward':all(x['normal_dot']>0 for x in h[1]['events']),'next_entry_inward_if_present':nxt is None or all(x['normal_dot']<0 for x in h[2]['events']),'no_positive_length_original_boundary_in_first_or_next_interval':not overlaps,'root_interval_ge_0p8_or_original_normal_retained':mode=='normal' or hi-lo>=.8}
   bind={'face':fi,'sample':si,'mode':mode}
   for frac in [.01,.1,.25,.5,.75,.9,.99]:add('first-material-fraction-'+str(frac),o+d*(lo+(hi-lo)*frac),1,bind)
   add('before-entry',o+d*(lo-1e-6),0,bind)
   for frac in [.001,.01,.1,.5,.9,.99]:add('next-air-fraction-'+str(frac),o+d*(hi+((nxt-hi) if nxt is not None else 1.0)*frac),0,bind)
   outrows.append({**bind,'source_point_mm':np.array(p,float).tolist(),'origin_mm':np.array(o,float).tolist(),'direction':np.array(d,float).tolist(),'first_interval_mm':[lo,hi],'next_air_interval_mm':[hi,nxt],'all_strict_events':h,'all_parallel_triangle_intervals':b,'boundary_overlaps':overlaps,'checks':checks,'passed':all(checks.values())})
 # Cross-check every earlier parity point using independent whole-mesh winding.
 for q in rows:
  for c in q['controls']:add('original-witness-'+c['role'],c['point_mm'],1 if c['expected_material'] else 0,{'face':q['original_triangle_index'],'sample':q['sample_index'],'mode':'witness'})
 np.array(points,dtype='<f8').tofile(D/'points.bin')
 subprocess.run([str(D/'winding'),str(D/'tri.bin'),str(D/'points.bin'),str(D/'winding.csv')],check=True,env={**os.environ,'OMP_NUM_THREADS':'1'})
 values=np.loadtxt(D/'winding.csv',delimiter=',')[:,1]
 for c,v in zip(controls,values):c['winding']=float(v);c['passed']=bool(abs(v-c['expected_winding'])<1e-7)
checks={'every_corner_has_original_and_root_interval':len(outrows)==2*len(rows),'all_complete_interval_checks':all(x['passed']for x in outrows),'all_independent_whole_mesh_material_air_points':all(x['passed']for x in controls)}
detail={'intervals':outrows,'whole_mesh_controls':controls}
with (R/'full-interval-details.json.gz').open('wb')as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0)as g:g.write(json.dumps(detail,separators=(',',':')).encode())
out={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'passed':all(checks.values()),'checks':checks,'corner_witnesses':len(rows),'strict_intervals':len(outrows),'whole_mesh_point_controls':len(controls),'maximum_winding_error':max(abs(x['winding']-x['expected_winding'])for x in controls),'failed_interval_checks':[x for x in outrows if not x['passed']],'failed_point_controls':[x for x in controls if not x['passed']],'detail_file':'full-interval-details.json.gz','detail_sha256':hashlib.sha256((R/'full-interval-details.json.gz').read_bytes()).hexdigest(),'method':'Long-double exact original-face barycentric source reconstruction and BVH original-triangle ray events plus projected coplanar triangle intervals. Complete first material/next air spans, original inward/outward events, all stored controls and whole-mesh compensated solid-angle winding. Finite four-corner qualification, not global wall thickness.'}
(R/'full-interval-check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert out['passed']
