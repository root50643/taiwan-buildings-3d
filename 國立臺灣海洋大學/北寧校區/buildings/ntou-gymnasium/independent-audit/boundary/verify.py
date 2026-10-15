"""Original source reconstructed longdouble rays; exact rational line/triangle intervals; whole-mesh winding controls."""
from pathlib import Path
import json,csv,hashlib,numpy as np,subprocess,os,gzip,collections,platform
from fractions import Fraction as F
from config import *
assert hashlib.sha256(S.read_bytes()).hexdigest()==H
T=np.fromfile(W/'ntou-revision-dense-triangles.bin',dtype='<f8').reshape(-1,3,3);LT=T.astype(np.longdouble);E1=LT[:,1]-LT[:,0];E2=LT[:,2]-LT[:,0];NC=np.cross(E1,E2);N=NC/np.sqrt(np.einsum('ij,ij->i',NC,NC))[:,None]
weights=[['1/3']*3,['.98','.01','.01'],['.01','.98','.01'],['.01','.01','.98'],['.495','.495','.01'],['.01','.495','.495'],['.495','.01','.495'],['.49','.49','.02'],['.49','.02','.49'],['.02','.49','.49'],['.8','.1','.1'],['.1','.8','.1'],['.1','.1','.8'],['.2','.3','.5'],['.2','.5','.3']]
source=json.load(open(W/'ntou-revision-boundary-events-summary.json'));rawflags=json.load(open(W/'ntou-revision-boundary-rawflags.json'));flagidx={int(r['index'])for r in rawflags};refs=[];pts=[];rows=[];problems=[];max_quant=0.;rational_cache={}
def sub(a,b):return[x-y for x,y in zip(a,b)]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def det(a,b):return a[0]*b[1]-a[1]*b[0]
def fractri(i):
 if i not in rational_cache:rational_cache[i]=[[F(float(v))for v in row]for row in T[i]]
 return rational_cache[i]
def ld(x):return np.longdouble(x.numerator)/np.longdouble(x.denominator)
def rational_interval(p,d,fi):
 a,b,c=fractri(fi);u=sub(b,a);v=sub(c,a);n=cross(u,v);plane=dot(n,sub(p,a));parallel=dot(n,d)
 assert plane==0 and parallel==0,(fi,float(plane),float(parallel))
 axis=max(range(3),key=lambda k:abs(n[k]));keep=[k for k in range(3)if k!=axis];u=[u[k]for k in keep];v=[v[k]for k in keep];o=[p[k]-a[k]for k in keep];d=[d[k]for k in keep];den=det(u,v)
 b0=det(o,v)/den;b1=det(d,v)/den;c0=det(u,o)/den;c1=det(u,d)/den;coef=[(1-b0-c0,-b1-c1),(b0,b1),(c0,c1)];lo=None;hi=None
 for a,b in coef:
  if b>0:lo=max(lo,-a/b)if lo is not None else-a/b
  elif b<0:hi=min(hi,-a/b)if hi is not None else-a/b
  else:assert a>=0
 assert lo is not None and hi is not None and hi>lo
 return lo,hi,coef,axis

def add(p,**meta):
 global max_quant
 p=np.array(p,dtype=np.longdouble);quant=np.max(abs(p-p.astype(np.float64).astype(np.longdouble)));max_quant=max(max_quant,float(quant));refs.append(dict(index=len(pts),point_mm=p.astype(float).tolist(),**meta));pts.append(p.astype(float))
def direct_ray(o,d):
 pp=np.cross(np.broadcast_to(d,E2.shape),E2);de=np.einsum('ij,ij->i',E1,pp);valid=abs(de)>1e-24;inv=np.zeros(len(T),dtype=np.longdouble);inv[valid]=1/de[valid];ss=o-LT[:,0];u=inv*np.einsum('ij,ij->i',ss,pp);q=np.cross(ss,E1);v=inv*np.einsum('ij,j->i',q,d);t=inv*np.einsum('ij,ij->i',E2,q);ids=np.flatnonzero(valid&(u>=-1e-15)&(v>=-1e-15)&(u+v<=1+1e-15)&(t>1e-12));ids=ids[np.argsort(t[ids])];h=[]
 for fi in ids:
  rr=dict(original_face=int(fi),barycentric=[float(1-u[fi]-v[fi]),float(u[fi]),float(v[fi])],normal_dot_direction=float(N[fi]@d))
  if h and abs(float(t[fi])-h[-1]['t'])<1e-11:h[-1]['faces'].append(rr)
  else:h.append(dict(t=float(t[fi]),faces=[rr]))
 return h
for ri,rec in enumerate(source['all_boundary_events']):
 i,fi,si=rec['index'],rec['face'],rec['sample'];tt=fractri(fi);p=[sum(tt[k][j]*F(weights[si][k])for k in range(3))for j in range(3)];raw=cross(sub(tt[1],tt[0]),sub(tt[2],tt[0]));d_raw=[-x for x in raw];rawlen=np.sqrt(sum(ld(x)**2 for x in raw))
 wld=[np.longdouble(1)/3 if x=='1/3'else np.longdouble(x)for x in weights[si]];p_ld=sum(LT[fi,k]*wld[k]for k in range(3));n=N[fi];o=p_ld+n*np.longdouble('1e-5');d=-n;h=direct_ray(o,d)
 assert len(h)>=2;a,b=h[0]['t'],h[1]['t'];c=h[2]['t']if len(h)>2 else None;delta=(b-a)-rec['first_span'];assert abs(delta)<1e-9
 rr=dict(index=i,face=fi,sample=si,weights=weights[si],dense_flag=i in flagidx,origin_mm=o.astype(float).tolist(),source_exact_rational_point_mm=list(map(str,p)),source_exact_rational_unnormalized_direction=list(map(str,d_raw)),direction=d.astype(float).tolist(),first_entry_mm=a,first_exit_mm=b,first_material_mm=b-a,next_event_mm=c,first_material_delta_from_all_rays_ld_mm=delta,first_material_delta_from_dense_mm=(b-a)-rec['raw_dense']['first_solid'],events=h,boundaries=[])
 add(o,ray_index=i,role='source_outside',expected_winding=0)
 add(p_ld-n*min(np.longdouble('1e-5'),np.longdouble(b-a)/4),ray_index=i,role='source_inside',expected_winding=1)
 for frac in ['.001','.01','.1','.25','.5','.75','.9','.99','.999']:add(o+d*(np.longdouble(a)+np.longdouble(b-a)*np.longdouble(frac)),ray_index=i,role='first_material',fraction=float(frac),expected_winding=1)
 for bi,q in enumerate(rec['raw_boundary_candidates']):
  bf=q['face'];lo,hi,coef,ax=rational_interval(p,d_raw,bf);tlo=ld(lo)*rawlen+np.longdouble('1e-5');thi=ld(hi)*rawlen+np.longdouble('1e-5');endpoint_delta=max(abs(float(tlo)-q['a']),abs(float(thi)-q['b']));assert endpoint_delta<1e-9
  assert float(tlo)>=b-1e-9,('first overlaps',i,bf,float(tlo),b)
  roles=[dict(role=bb['role'],clipped_a_mm=bb['lo'],clipped_b_mm=bb['hi'],length_mm=bb['length'])for bb in rec['boundaries']if bb['face']==bf]
  br=dict(boundary_index=bi,original_triangle=bf,original_triangle_vertices_mm=T[bf].tolist(),original_winding_normal=N[bf].astype(float).tolist(),exact_original_source_point_plane_residual_zero=True,exact_original_raw_direction_parallel=True,exact_lambda_a=str(lo),exact_lambda_b=str(hi),exact_lambda_definition='P + lambda * (-cross(source_edge1,source_edge2)); t_mm=lambda*norm(raw_source_cross)+1e-5',interval_a_mm=float(tlo),interval_b_mm=float(thi),interval_endpoint_delta_mm=endpoint_delta,roles=roles,classification='positive_length_original_surface_boundary_neither_air_nor_bulk',drop_axis=ax,stations=[])
  for fs in ['.01','.1','.25','.5','.75','.9','.99']:
   frac=F(fs);lam=lo+(hi-lo)*frac;point=[p[k]+d_raw[k]*lam for k in range(3)];bary=[u+v*lam for u,v in coef];assert min(bary)>=0;br['stations'].append(dict(fraction=float(frac),exact_lambda=str(lam),exact_barycentric=list(map(str,bary)),barycentric=list(map(float,bary)),t_mm=float(ld(lam)*rawlen+np.longdouble('1e-5'))));point_ld=np.array([ld(x)for x in point])
   for ep in ['1e-5','1e-6']:
    for sign in [-1,1]:add(point_ld+sign*N[bf]*np.longdouble(ep),ray_index=i,boundary_index=bi,original_triangle=bf,role='boundary_inward_side'if sign<0 else'boundary_outward_side',fraction=float(frac),offset_mm=float(ep),expected_winding=1 if sign<0 else 0)
  rr['boundaries'].append(br)
 # Classify the dense probe only geometrically, never interpreting on-surface winding.
 after=b+min(1e-5,(c-b)/2)if c else b+1e-5
 containing=[br['original_triangle']for br in rr['boundaries']if br['interval_a_mm']<after<br['interval_b_mm']]
 rr['reconstructed_after_probe_t_mm']=after;rr['after_probe_boundary_original_triangles']=containing
 if i in flagidx:assert containing,('flag not geometrically on positive interval',i)
 # Nonboundary gaps between first exit and next transverse event have true outside controls.
 end=c if c is not None else max([b+1]+[br['interval_b_mm']+1 for br in rr['boundaries']]);intervals=sorted((max(b,br['interval_a_mm']),min(end,br['interval_b_mm']))for br in rr['boundaries']if min(end,br['interval_b_mm'])>max(b,br['interval_a_mm']));cursor=b;gaps=[]
 for l,r in intervals:
  if l-cursor>1e-8:gaps.append((cursor,l))
  cursor=max(cursor,r)
 if end-cursor>1e-8:gaps.append((cursor,end))
 rr['first_after_nonboundary_gaps_mm']=gaps
 for gi,(l,r)in enumerate(gaps):
  for fs in ['.1','.5','.9']:add(o+d*(np.longdouble(l)+np.longdouble(r-l)*np.longdouble(fs)),ray_index=i,gap_index=gi,role='first_after_nonboundary',fraction=float(fs),expected_winding=0)
 rows.append(rr)
 if ri%20==0:print('PREPARED',ri,len(pts),flush=True)
np.array(pts,dtype='<f8').tofile(W/'ntou-revision-boundary-winding-points.bin');print('WINDING',len(pts),flush=True)
subprocess.run([str(W/'winding'),W/'ntou-revision-dense-triangles.bin',W/'ntou-revision-boundary-winding-points.bin',W/'ntou-revision-boundary-winding.csv'],check=True,env={**os.environ,'OMP_NUM_THREADS':'4'})
vals=np.loadtxt(W/'ntou-revision-boundary-winding.csv',delimiter=',')[:,1]
for r,val in zip(refs,vals):
 r['winding']=float(val);r['absolute_error']=abs(val-r['expected_winding'])
 if r['absolute_error']>1e-8:problems.append(r)
counts={}
for label,pred in [('author_same_10_points',lambda r:r['sample']<10),('additional_5_points',lambda r:r['sample']>=10),('all_15_points',lambda r:True)]:
 rs=[r for r in rows if pred(r)];counts[label]=dict(total_sample_rays=5630*(10 if label=='author_same_10_points'else 5 if label=='additional_5_points'else 15),boundary_rays=len(rs),boundary_triangle_intervals=sum(len(r['boundaries'])for r in rs),first_boundary_rays=0,first_after_boundary_rays=sum(any(role['role']=='after'for q in r['boundaries']for role in q['roles'])for r in rs),first_after_triangle_intervals=sum(role['role']=='after'for r in rs for q in r['boundaries']for role in q['roles']),farther_boundary_rays=sum(any(role['role']=='later'for q in r['boundaries']for role in q['roles'])for r in rs),farther_triangle_intervals=sum(role['role']=='later'for r in rs for q in r['boundaries']for role in q['roles']),parity_flags=sum(r['dense_flag']for r in rs))
summary=dict(stl_sha256=H,original_triangles=len(T),samples=source['samples'],sample_weights=weights,counts=counts,no_first_material_boundary=True,first_material_changed_from_dense_count=source['changed_first_events'],first_material_boundary_ray_max_delta_from_dense_mm=max(abs(r['first_material_delta_from_dense_mm'])for r in rows),maximum_rational_interval_endpoint_delta_mm=max(q['interval_endpoint_delta_mm']for r in rows for q in r['boundaries']),all_intervals_exact_rational_source_coplanar=True,parity_flag_count=len(flagidx),all_flags_after_probe_geometrically_on_positive_original_boundary=True,flag_ids=[[r['face'],r['sample']]for r in rows if r['dense_flag']],winding_control_count=len(refs),winding_control_role_counts=dict(collections.Counter(r['role']for r in refs)),maximum_winding_error=max(r['absolute_error']for r in refs),maximum_point_double_serialization_error_mm=max_quant,winding_failure_count=len(problems),all_nonboundary_winding_controls_passed=not problems,source_sha_unchanged=hashlib.sha256(S.read_bytes()).hexdigest()==H,method='Every original triangle has the same 15 barycentric weights. All 84,450 source origins/directions reconstructed in long double directly from the original face and weights; CSV positions never establish line geometry. Full original-triangle BVH intersection scan retains transverse hits and every positive-length coplanar candidate over the complete forward ray. For every one of 409 candidate intervals, exact Fraction arithmetic on the original binary STL float32 coordinates, exact rational sample weights and unnormalized original source cross product proves zero plane residual and zero parallel dot product, then solves all affine barycentric inequalities to give exact rational line-parameter endpoints. All 110 boundary rays independently brute-recast against original triangles in NumPy longdouble. Seven interior stations per interval and offsets 1e-5 and 1e-6 mm along both sides of each original triangle winding normal are evaluated by complete original-mesh longdouble compensated solid-angle sum. Each boundary ray has source outside/inside and nine first-material controls. All available nonboundary gaps before the next transverse event have three outside controls. On-surface winding is not interpreted as 0 or 1, and no boundary interval is added to bulk material.',limits='Full finite sample coverage, not a continuous/global thickness or self-intersection theorem. Candidate discovery uses |unit normal dot ray|<1e-12 and |plane distance|<1e-10 mm; all discovered intervals are then exactly certified rational coplanar. Positive intervals retained above 1e-10 mm, event grouping tolerance 1e-11 mm. Independent recast det cutoff1e-24, barycentric tolerance1e-15. Winding side stations are finite; 1e-8 winding-error threshold. Source float32 coordinates untouched, no repair, merge, round, weld, simplify, or geometry changes. No exception or printability approval.',software=dict(numpy=np.__version__,longdouble_storage_bits=np.finfo(np.longdouble).bits,longdouble_mantissa_bits=np.finfo(np.longdouble).nmant,longdouble_epsilon=str(np.finfo(np.longdouble).eps),platform=platform.platform()),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),exact_cpp_sha256=hashlib.sha256((O/'exact_source.cpp').read_bytes()).hexdigest(),winding_cpp_sha256=hashlib.sha256((O/'winding.cpp').read_bytes()).hexdigest(),winding_executable_sha256=hashlib.sha256((W/'winding').read_bytes()).hexdigest())
Path(W/'ntou-revision-boundary-independent.json').write_text(json.dumps(summary,indent=2))
with gzip.open(W/'ntou-revision-boundary-evidence.json.gz','wt',compresslevel=9)as f:json.dump(dict(summary=summary,rows=rows,raw_dense_flags=rawflags,winding_controls=refs,failures=problems),f,separators=(',',':'),allow_nan=False)
print(json.dumps(summary,indent=2));assert not problems
