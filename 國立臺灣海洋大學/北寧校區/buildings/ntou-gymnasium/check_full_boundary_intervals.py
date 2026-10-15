"""Complete original-normal first/next interval screen, adapted from independent audit tooling.
Original reports retained; along-surface intervals are never reclassified as bulk air or wall.
"""
from pathlib import Path
import json,numpy as np,subprocess,os,csv,gzip,tempfile,hashlib,trimesh
R=Path(__file__).resolve().parent;tmp=tempfile.TemporaryDirectory();D=Path(tmp.name)
m=trimesh.load(R/'model.stl',process=False);T=m.triangles;TT=T.astype(np.longdouble);N=np.cross(TT[:,1]-TT[:,0],TT[:,2]-TT[:,0]);N/=np.linalg.norm(N,axis=1)[:,None]
W=np.array([[1/3]*3,[.98,.01,.01],[.01,.98,.01],[.01,.01,.98],[.495,.495,.01],[.01,.495,.495],[.495,.01,.495],[.49,.49,.02],[.49,.02,.49],[.02,.49,.49]])
with gzip.open(R/'dense-original.csv.gz','rt') as f:raw=list(csv.DictReader(f))
allq=[]
for q in raw:
 i=int(q['face']);j=int(q['sample']);p=W[j]@T[i];n=np.array(m.face_normals[i]);h=list(map(float,q['hits'].strip(';').split(';')));allq.append(list(p+n*1e-5)+list(-n)+[h[0],h[1],h[2] if len(h)>2 else np.inf,i,j])
allq=np.array(allq);allq.astype('<f8').tofile(D/'queries.bin');T.astype('<f8').tofile(D/'tri.bin')
for source,exe in [('all_boundary_screen.cpp','screen'),('strict_exact_source_intervals.cpp','strict'),('winding_parallel.cpp','wind')]:subprocess.run(['g++','-O3','-fopenmp','-std=c++17',str(R/source),'-o',str(D/exe)],check=True)
subprocess.run([str(D/'screen'),str(D/'tri.bin'),str(D/'queries.bin'),str(D/'overlaps.csv')],check=True,env={**os.environ,'OMP_NUM_THREADS':'4'})
with open(D/'overlaps.csv') as f:a=list(csv.DictReader(f))
with open(D/'overlaps.csv','rb') as f,gzip.open(R/'all-boundary-overlaps.csv.gz','wb') as g:g.write(f.read())
ids=np.array(sorted({int(x['index']) for x in a}));qs=allq[ids,:6].reshape(-1,2,3);qs.astype('<f8').tofile(D/'strictqueries.bin')
np.asarray(allq[ids,9:11],dtype='<i4').tofile(D/'exact-source-ids.bin')
subprocess.run([str(D/'strict'),str(D/'tri.bin'),str(D/'strictqueries.bin'),str(D/'strict.csv'),str(D/'exact-source-ids.bin')],check=True)
with gzip.open(R/'exact-source-boundary-events.txt.gz','wt') as f:f.write((D/'strict.csv').read_text())
def parse(line):
 hpart,bpart=line.split('|');hh=[]
 for val in hpart.split(';')[1:]:
  t,f,u,v,nd=map(float,val.split(','));rec={'face':int(f),'barycentric':[1-u-v,u,v],'nd':nd}
  if hh and abs(t-hh[-1]['t'])<1e-11:hh[-1]['faces'].append(rec)
  else:hh.append({'t':t,'faces':[rec]})
 bb=[]
 for val in bpart.strip().split(';')[1:]:
  aa,b,f,plane,nd=map(float,val.split(','));bb.append({'a':aa,'b':b,'face':int(f),'plane':plane,'nd':nd})
 return hh,bb
pts=[];refs=[];rows=[]
def add(r,role,p,expected,**extra):
 q={'index':len(pts),'face':r['face'],'sample':r['sample'],'role':role,'point_mm':np.array(p,float).tolist(),'expected_winding':expected,**extra};r['controls'].append(q);refs.append(q);pts.append(p)
for k,(ix,q,line) in enumerate(zip(ids,qs,(D/'strict.csv').read_text().splitlines())):
 o,d=q;h,bb=parse(line);start,end=h[0]['t'],h[1]['t'];after=h[2]['t']if len(h)>2 else np.inf;dense=allq[ix];r={'face':int(dense[9]),'sample':int(dense[10]),'dense_index':int(ix),'origin_mm':o.tolist(),'direction':d.tolist(),'strict_events':h,'first_geometric_span_mm':end-start,'next_geometric_interval_t_mm':[end,None if np.isinf(after)else after],'dense_vs_strict_first_end_delta_mm':[start-dense[6],end-dense[7]],'positive_length_boundary_intervals':[],'controls':[]}
 for x in bb:
  aa=max(x['a'],end);b=min(x['b'],after)
  if b-aa<=1e-9:continue
  f=x['face'];ax=int(np.argmax(abs(N[f])));axes=[i for i in range(3)if i!=ax];tri=TT[f];e1=tri[1,axes]-tri[0,axes];e2=tri[2,axes]-tri[0,axes];cross=lambda a,b:a[0]*b[1]-a[1]*b[0];den=cross(e1,e2);interval={**x,'clipped_a':aa,'clipped_b':b,'length_mm':b-aa,'station_geometry':[]}
  for frac in [.1,.5,.9]:
   t=aa+(b-aa)*frac;p=o+d*t;s=p[axes].astype(np.longdouble)-tri[0,axes];u=cross(s,e2)/den;v=cross(e1,s)/den;bar=[float(1-u-v),float(u),float(v)];interval['station_geometry'].append({'fraction':frac,'barycentric':bar,'plane_distance_mm':float(abs((p.astype(np.longdouble)-tri[0])@N[f]))});add(r,'on_original_boundary',p,None,boundary_face=f,interval_fraction=frac)
   for eps in [1e-6,1e-5,1e-4]:
    for sign in [-1,1]:add(r,'boundary_side_offset',p+np.array(N[f],float)*eps*sign,1 if sign<0 else 0,boundary_face=f,interval_fraction=frac,normal_offset_mm=eps*sign)
  r['positive_length_boundary_intervals'].append(interval)
 # Whole first segment and open subdivisions of reported after interval, retain no boundary as bulk.
 for frac in [.01,.1,.25,.5,.75,.9,.99]:add(r,'first_segment',o+d*(start+(end-start)*frac),1,fraction=frac)
 add(r,'before_source',o+d*(start-1e-5),0)
 breaks=sorted(set([end]+[x['clipped_a']for x in r['positive_length_boundary_intervals']]+[x['clipped_b']for x in r['positive_length_boundary_intervals']]+([after]if np.isfinite(after)else [])))
 if not np.isfinite(after):breaks.append(max(breaks)+1)
 r['next_interval_partition']=[]
 for aa,b in zip(breaks,breaks[1:]):
  if b-aa<1e-9:continue
  mid=(aa+b)/2;on=[x['face']for x in r['positive_length_boundary_intervals']if x['clipped_a']-1e-10<mid<x['clipped_b']+1e-10];role='boundary'if on else'air';r['next_interval_partition'].append({'a':aa,'b':b,'classification':role,'boundary_faces':on})
  if not on:
   for frac in [.1,.5,.9]:add(r,'open_after_subinterval',o+d*(aa+(b-aa)*frac),0,interval=[aa,b],fraction=frac)
 # open interval just beyond the boundary union does not presume air if followed by a genuine entry.
 rows.append(r)
np.array(pts).tofile(D/'controls.bin');subprocess.run([str(D/'wind'),str(D/'tri.bin'),str(D/'controls.bin'),str(D/'winding.csv')],check=True,env={**os.environ,'OMP_NUM_THREADS':'4'})
w=np.loadtxt(D/'winding.csv',delimiter=',')[:,1];bad=[]
for r in rows:
 for c in r['controls']:
  c['winding']=float(w[c['index']]);ex=c['expected_winding'];c['passed']=None if ex is None else abs(c['winding']-ex)<1e-7
  if c['passed']is False:bad.append(c)
 r['all_nonboundary_controls_passed']=all(c['passed']is not False for c in r['controls']);r['all_boundary_station_barycentric_strictly_interior']=all(min(s['barycentric'])>1e-8 for x in r['positive_length_boundary_intervals']for s in x['station_geometry'])
out={'total_screened_dense_rays':len(allq),'positive_length_first_segment_boundary_ray_count':len({int(x['index']) for x in a if int(x['role'])==0}),'positive_length_after_interval_boundary_ray_count':len(rows),'boundary_triangle_interval_count':sum(len(r['positive_length_boundary_intervals'])for r in rows),'control_count':len(pts),'off_boundary_failed_controls':bad,'all_nonboundary_controls_passed':not bad,'rows':rows,'method':'Every saved original-normal sample screened against every original STL triangle using long-double plane/parallel tests and projected finite-triangle clipping. First geometric segment and complete next interval screened, including infinity after terminal exit. Strict origins are recomputed from original face and exact long-double barycentric weights, including centroid 1/3, rather than reusing float64 rounded origin. Candidate tolerances: |normal dot direction| < 1e-12, |plane residual| < 1e-10 mm; open endpoint exclusion 1e-10 mm and overlap length >1e-9 mm. Screen candidates then traced using independent long-double strict original-triangle ray tool; every clipped boundary triangle checked at 10/50/90 percent with exact-plane/barycentric tests and +/- 1e-6/1e-5/1e-4 mm original-normal offsets. Winding uses all original STL triangles, atan2l, compensated sum. Points on boundaries have undefined material/air winding; their numerical outputs are retained only as diagnostic. No bulk thickness inferred from along-boundary lengths.','no_exception_approved':True};out.update(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest());
with gzip.open(R/'boundary-witnesses.json.gz','wt') as f:json.dump(out,f);print({k:v for k,v in out.items()if k not in ['rows','method','off_boundary_failed_controls']},'FAILED',len(bad),flush=True)

assert out["all_nonboundary_controls_passed"]
