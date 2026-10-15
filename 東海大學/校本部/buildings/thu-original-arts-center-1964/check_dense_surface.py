#!/usr/bin/env python3
"""Strict, finite original-triangle normal audit; never a global thickness proof.

All 10 interior barycentric samples of every actual raw binary-STL triangle.
The BVH only indexes triangles: no weld/repair/remesh/Manifold geometry is used.
Complete original-face-ID hit streams and positive-length coplanar intervals
are retained for every sample. Short/unclassified rows are never discarded.
Every short/flagged row receives whole-original-mesh solid-angle controls.
Use --screen-only for an explicitly incomplete, failing diagnostic iteration.
"""
from pathlib import Path
import argparse, collections, gzip, hashlib, json, lzma, os, shutil, struct, subprocess, time
from decimal import Decimal
import numpy as np
ROOT=Path(__file__).resolve().parent
WEIGHTS=np.array([[1/3]*3,[.98,.01,.01],[.01,.98,.01],[.01,.01,.98],[.495,.495,.01],[.01,.495,.495],[.495,.01,.495],[.49,.49,.02],[.49,.02,.49],[.02,.49,.49]])
LEGEND={1:'invalid original source face/normal',2:'missing or non-source entry',4:'missing/nonpositive first interval',8:'nonalternating or tangent original-face crossings',16:'positive-length coplanar boundary overlap in first material/next air',32:'independent oblique material/air parity control failed or unclassified',64:'first material interval below requested minimum',128:'whole-mesh solid-angle control failed or unclassified',256:'positive sub-tolerance boundary overlap; unclassified'}
CONTROL_ROLES=['before-entry','inside-near-entry','first-material-midpoint','after-first-exit','next-air-midpoint']
EXPECTED=[0,1,1,0,0]

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def gzopen(path):
 return gzip.GzipFile(filename='',fileobj=open(path,'wb'),mode='wb',mtime=0)

def raw(path):
 data=path.read_bytes()
 if len(data)<84:raise ValueError('not a complete binary STL')
 n=struct.unpack('<I',data[80:84])[0]
 if len(data)!=84+50*n:raise ValueError('binary STL triangle count/file length mismatch')
 rec=np.frombuffer(data,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('attribute','<u2')],offset=84,count=n)
 if not n:raise ValueError('empty STL')
 return rec

def topology(rec):
 t=rec['v'].astype(np.float64);sn=rec['n'].astype(np.float64);cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(cross,axis=1)
 vertices,inv=np.unique(t.reshape(-1,3),axis=0,return_inverse=True);faces=inv.reshape(-1,3);nv=len(vertices)
 edges=np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]);lo=np.minimum(edges[:,0],edges[:,1]);hi=np.maximum(edges[:,0],edges[:,1]);keys=lo.astype(np.uint64)*nv+hi
 uniq,idx,cnt=np.unique(keys,return_inverse=True,return_counts=True);oriented=np.bincount(idx,weights=np.where(edges[:,0]<edges[:,1],1,-1))
 cosine=np.divide(np.einsum('ij,ij->i',cross,sn),length*np.linalg.norm(sn,axis=1),out=np.full(len(t),np.nan),where=(length*np.linalg.norm(sn,axis=1))>0)
 r={'stored_normals_nonunit':int(np.sum(abs(np.linalg.norm(sn,axis=1)-1)>1e-6)),'stored_normal_max_unit_error':float(np.max(abs(np.linalg.norm(sn,axis=1)-1))),'stored_normal_min_geometric_cosine':float(np.nanmin(cosine)),'stored_normals_misaligned':int(np.sum(~np.isfinite(cosine)|(cosine<1-1e-6))),'raw_faces':len(t),'nonfinite_vertices_and_normals':int((~np.isfinite(t)).sum()+(~np.isfinite(sn)).sum()),'zero_area_faces':int(np.sum(length==0)),'stored_normals_nonpositive_dot':int(np.sum(np.einsum('ij,ij->i',cross,sn)<=0)),'duplicate_faces':int(len(faces)-len(np.unique(np.sort(faces,axis=1),axis=0))),'edge_incidence_not_two':int(np.sum(cnt!=2)),'edge_orientation_failures':int(np.sum(oriented!=0)),'signed_volume_mm3':float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6)}
 r['passed']=bool(all(r[k]==0 for k in ['stored_normals_nonunit','stored_normals_misaligned','nonfinite_vertices_and_normals','zero_area_faces','stored_normals_nonpositive_dot','duplicate_faces','edge_incidence_not_two','edge_orientation_failures'])and r['signed_volume_mm3']>0)
 return r

def parse(line):
 head,hit_text,bound_text=line.rstrip('\n').split('|')
 h=head.split(',');fi,si=map(int,h[:2]);p=np.array(h[2:5],float);n=np.array(h[5:8],float);valid=bool(int(h[8]));parity=np.array(h[9:],int).reshape(5,2)
 events=[]
 for text in hit_text.split(';'):
  if not text:continue
  t,face,u,v,nd=text.split(',');events.append({'t_mm':float(t),'t_mm_long_double':t,'face':int(face),'barycentric_uv':[float(u),float(v)],'normal_dot_ray':float(nd)})
 bounds=[]
 for text in bound_text.split(';'):
  if not text:continue
  a,b,face,plane,nd=text.split(',');bounds.append({'start_t_mm':float(a),'end_t_mm':float(b),'start_t_long_double':a,'end_t_long_double':b,'face':int(face),'plane_residual_mm':float(plane),'normal_dot_ray':float(nd)})
 groups=[]
 for event in events:
  if groups and abs(event['t_mm']-groups[-1]['t_mm'])<=1e-10:groups[-1]['events'].append(event)
  else:groups.append({'t_mm':event['t_mm'],'t_mm_long_double':event['t_mm_long_double'],'events':[event]})
 return fi,si,p,n,valid,parity,events,bounds,groups

def classify(parsed,minimum):
 fi,si,p,n,valid,parity,events,bounds,g=parsed;status=0;overlaps=[]
 if not valid:status|=1
 if not g or abs(g[0]['t_mm']-1e-5)>2e-9 or not any(h['face']==fi for h in g[0]['events']):status|=2
 a=g[0]['t_mm']if g else np.nan;b=g[1]['t_mm']if len(g)>1 else np.nan;c=g[2]['t_mm']if len(g)>2 else np.inf
 if not np.isfinite(b-a)or b<=a:status|=4
 if len(g)%2 or any(any((h['normal_dot_ray']>=-1e-12 if k%2==0 else h['normal_dot_ray']<=1e-12)for h in x['events'])for k,x in enumerate(g)):status|=8
 for bd in bounds:
  if len(g)<2:continue
  exact=[Decimal(x['t_mm_long_double'])for x in g[:3]]
  if len(exact)<3:exact.append(Decimal('Infinity'))
  for role,lo,hi in [('first-material',exact[0],exact[1]),('next-air',exact[1],exact[2])]:
   start=max(lo,Decimal(bd['start_t_long_double']));end=min(hi,Decimal(bd['end_t_long_double']))
   if end>start:
    overlaps.append({'role':role,'start_t_mm':float(start),'end_t_mm':float(end),'overlap_mm_long_double':str(end-start),'boundary_face':bd['face']})
    status|=16 if end-start>Decimal('1e-9')else 256
 if np.any(parity!=np.array(EXPECTED)[:,None]):status|=32
 if len(g)>1 and Decimal(g[1]['t_mm_long_double'])-Decimal(g[0]['t_mm_long_double'])<Decimal(str(minimum)):status|=64
 return status,a,b,c,overlaps

def controls(p,n,a,b,c):
 if not(np.isfinite(a)and np.isfinite(b)and b>a):return []
 gap=c-b if np.isfinite(c)else 1.0
 if gap<=0:return []
 o=p+n*1e-5;d=-n;ts=[a-min(1e-5,a/2),a+min(1e-5,(b-a)/4),(a+b)/2,b+min(1e-5,gap/4),b+gap/2]
 return [{'role':r,'point_mm':(o+d*t).tolist(),'expected_winding':ex}for r,ex,t in zip(CONTROL_ROLES,EXPECTED,ts)]

def compile_helper(name,out,omp=False):
 exe=out/name;source=ROOT/(name+'.cpp');cmd=['g++','-O3','-std=c++17']+(['-fopenmp']if omp else[])+[str(source),'-o',str(exe)]
 subprocess.run(cmd,check=True);return exe

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,default=ROOT/'output');ap.add_argument('--stl',type=Path);ap.add_argument('--min-thickness',type=float,default=.8);ap.add_argument('--normal-mode',choices=['geometric','stored'],default='geometric');ap.add_argument('--threads',type=int,default=4);ap.add_argument('--face-limit',type=int);ap.add_argument('--screen-only',action='store_true');ap.add_argument('--reuse-events',action='store_true');args=ap.parse_args()
 out=args.out.resolve();out.mkdir(parents=True,exist_ok=True);stl=(args.stl or out/'model.stl').resolve();started=time.time();stl_sha=sha(stl);rec=raw(stl);top=topology(rec);nf=len(rec);limit=min(nf,args.face_limit)if args.face_limit else nf
 work=out/'dense-work';work.mkdir(exist_ok=True);tri=rec['v'].astype('<f8');sn=rec['n'].astype('<f8');tri.tofile(work/'triangles.bin');sn.tofile(work/'stored-normals.bin')
 source={'stl_sha256':stl_sha,'faces':nf,'normal_mode':args.normal_mode,'face_limit':limit,'samples_per_face':10,'barycentric_weights':WEIGHTS.tolist(),'direct_triangle_bytes_sha256':sha(work/'triangles.bin'),'helper_sha256':sha(ROOT/'dense_original.cpp')}
 manifest=out/'dense-source.json';eventsfile=out/'dense-events.txt.gz'
 if args.reuse_events and (out/'dense-events.txt.xz').exists():eventsfile=out/'dense-events.txt.xz'
 event_opener=lzma.open if eventsfile.suffix=='.xz'else gzip.open
 if args.reuse_events:
  if not manifest.exists()or json.loads(manifest.read_text())!=source or not eventsfile.exists():raise ValueError('Cannot reuse events: original STL/mode/face count/helper identity changed')
 else:
  manifest.write_text(json.dumps(source,indent=2)+'\n');exe=compile_helper('dense_original',work)
  subprocess.run([str(exe),str(work/'triangles.bin'),str(work/'stored-normals.bin'),str(work/'events.txt'),str(limit),args.normal_mode],check=True)
  with open(work/'events.txt','rb')as f,gzopen(eventsfile)as g:shutil.copyfileobj(f,g)
  (work/'events.txt').unlink()
 print('Strict dense events retained; classifying every row.',flush=True)
 ns=limit*10;status=np.zeros(ns,dtype=np.uint16);first=np.full(ns,np.nan);entry=np.full(ns,np.nan);exit_=np.full(ns,np.nan);nextentry=np.full(ns,np.nan);hitcount=np.zeros(ns,dtype=np.uint32);boundcount=np.zeros(ns,dtype=np.uint32)
 flags=[];seen=np.zeros(ns,dtype=bool);reasoncounts=collections.Counter();allpoints=[]
 with event_opener(eventsfile,'rt')as f:
  for line in f:
   parsed=parse(line);fi,si,p,n,valid,parity,events,bounds,groups=parsed;k=fi*10+si
   if not(0<=fi<limit and 0<=si<10)or seen[k]:raise ValueError('Duplicate/out-of-range original sample identity')
   seen[k]=True;s,a,b,c,overlaps=classify(parsed,args.min_thickness);status[k]=s;entry[k]=a;exit_[k]=b;nextentry[k]=c;first[k]=b-a;hitcount[k]=len(events);boundcount[k]=len(bounds)
   if s:
    cs=controls(p,n,a,b,c);control_start=len(allpoints);allpoints.extend(x['point_mm']for x in cs)
    row={'face':fi,'sample':si,'point_mm':p.tolist(),'normal':n.tolist(),'status_before_winding':s,'first_material_mm':None if not np.isfinite(b-a)else b-a,'first_interval_t_mm':[None if not np.isfinite(x)else x for x in [a,b]],'next_air_interval_t_mm':[None if not np.isfinite(x)else x for x in [b,c]],'next_air_unbounded':bool(np.isinf(c)),'all_events':events,'all_coplanar_boundary_intervals':bounds,'boundary_overlaps':overlaps,'independent_parity_controls':parity.tolist(),'solid_angle_controls':cs,'control_start':control_start};flags.append(row)
 if not np.all(seen):raise ValueError('Missing original sample identities')
 winding_done=not flags;winding_bad=0;winding_max=0.;winding_count=0
 # Preserve intermediate diagnostics before costly independent checks; incomplete is never a pass.
 def write_flags():
  with gzopen(out/'dense-flagged-intervals.jsonl.gz')as f:
   for q in flags:f.write((json.dumps(q,separators=(',',':'),allow_nan=False)+'\n').encode())
 write_flags()
 if flags and not args.screen_only:
  print(f'{len(flags)} short/flagged samples; {len(allpoints)} independent whole-mesh solid-angle controls.',flush=True)
  np.array(allpoints,dtype='<f8').reshape(-1,3).tofile(work/'winding-points.bin');exe=compile_helper('dense_winding_parallel',work,True)
  subprocess.run([str(exe),str(work/'triangles.bin'),str(work/'winding-points.bin'),str(work/'winding.csv')],check=True,env={**os.environ,'OMP_NUM_THREADS':str(max(1,args.threads))})
  values=np.loadtxt(work/'winding.csv',delimiter=',',ndmin=2)[:,1]if allpoints else np.empty(0)
  if len(values)!=len(allpoints):raise ValueError('Independent winding result count mismatch')
  winding_count=len(values)
  for q in flags:
   good=bool(q['solid_angle_controls'])
   for j,c in enumerate(q['solid_angle_controls']):
    val=float(values[q['control_start']+j]);err=abs(val-c['expected_winding']);c.update({'winding':val if np.isfinite(val)else None,'passed':bool(np.isfinite(val)and err<1e-7)});good&=c['passed'];winding_max=max(winding_max,err if np.isfinite(err)else float('inf'));winding_bad+=not c['passed']
   q['independent_solid_angle_passed']=good
   if not good:status[q['face']*10+q['sample']]|=128
  winding_done=True;write_flags()
 for bit,label in LEGEND.items():reasoncounts[label]=int(np.sum((status&bit)!=0))
 for q in flags:q['final_status']=int(status[q['face']*10+q['sample']])
 write_flags()
 np.savez_compressed(out/'dense-intervals.npz',face=np.repeat(np.arange(limit,dtype=np.uint32),10),sample=np.tile(np.arange(10,dtype=np.uint8),limit),barycentric_weights=WEIGHTS,entry_t_mm=entry,first_exit_t_mm=exit_,next_entry_t_mm=nextentry,first_material_mm=first,next_air_mm=nextentry-exit_,status=status,raw_hit_count=hitcount,positive_length_coplanar_count=boundcount)
 finite=first[np.isfinite(first)];order=np.argsort(np.where(np.isfinite(first),first,np.inf))[:30]
 checks={'all_original_faces_ten_samples':bool(limit==nf and np.all(seen)),'raw_topology_and_stored_orientation':top['passed'],'all_complete_interval_and_material_air_screens':bool(np.all((status&np.uint16(0xFFFF^64))==0)),'all_first_material_intervals_at_least_minimum':bool(np.all(np.isfinite(first))and np.all((status&64)==0)),'every_flagged_short_sample_independently_winding_checked':bool(winding_done),'all_independent_winding_controls_pass':bool(winding_done and winding_bad==0 and all(q.get('independent_solid_angle_passed',False)for q in flags)),'source_stl_unchanged':sha(stl)==stl_sha}
 summary={'stl_sha256':stl_sha,'source_stl':stl.name,'passed':all(checks.values()),'checks':checks,'method':'Direct original-triangle BVH; long-double source barycentric reconstruction and triangle predicates; every raw positive hit with face ID retained; projected positive-length coplanar boundary intervals; alternating original oriented crossings; two oblique parity rays at five material/air control points per sample; whole-original-mesh compensated solid-angle winding at all five points for every short/flagged sample. No repairs, masks, exemptions, or substituted root chords.','normal_mode':args.normal_mode,'normal_definition':'Unit cross product of exact original float32 triangle vertices, computed in long double; stored STL normal orientation independently checked.'if args.normal_mode=='geometric'else'Unit-normalized stored raw STL normals; triangle orientation predicates use original geometric cross products.','limits':'Finite surface sample audit, not a mathematical global minimum-thickness certificate. Unbounded next-air spans have no next hit; their two controls lie within 1mm after exit.','minimum_required_mm':args.min_thickness,'minimum_first_material_mm':float(finite.min())if len(finite)else None,'raw_faces':nf,'audited_faces':limit,'samples':ns,'samples_per_raw_face':10,'raw_hit_records':int(hitcount.sum()),'positive_length_coplanar_intervals':int(boundcount.sum()),'flagged_or_short_samples':len(flags),'status_bits':LEGEND,'reason_counts':reasoncounts,'topology':top,'whole_mesh_solid_angle_controls':winding_count,'maximum_winding_error':winding_max if np.isfinite(winding_max)else None,'winding_pending':bool(flags and not winding_done),'ten_sample_weights':WEIGHTS.tolist(),'tolerances':{'origin_offset_mm':1e-5,'hit_group_mm':1e-10,'entry_offset_error_mm':2e-9,'barycentric_tolerance':1e-15,'coplanar_plane_mm':1e-10,'coplanar_dot':1e-12,'minimum_positive_boundary_overlap_mm':1e-9,'winding_error':1e-7,'minimum_thickness_allowance_mm':0},'smallest_samples':[{'face':int(k//10),'sample':int(k%10),'first_material_mm':float(first[k])if np.isfinite(first[k])else None,'status':int(status[k])}for k in order],'artifacts':{p.name:{'sha256':sha(p),'bytes':p.stat().st_size}for p in [manifest,eventsfile,out/'dense-intervals.npz',out/'dense-flagged-intervals.jsonl.gz']},'elapsed_seconds':time.time()-started}
 stream_hash=hashlib.sha256();stream_bytes=0
 with event_opener(eventsfile,'rb')as f:
  for block in iter(lambda:f.read(1024*1024),b''):stream_hash.update(block);stream_bytes+=len(block)
 summary['complete_event_stream']={'artifact':eventsfile.name,'codec':'xz / LZMA2'if eventsfile.suffix=='.xz'else'gzip','uncompressed_sha256':stream_hash.hexdigest(),'uncompressed_bytes':stream_bytes,'numerical_text_rewritten':False}
 (out/'dense-audit.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n');print(json.dumps({k:summary[k]for k in ['passed','checks','minimum_first_material_mm','samples','flagged_or_short_samples','reason_counts','whole_mesh_solid_angle_controls','winding_pending','elapsed_seconds']},indent=2),flush=True)
 return 0 if summary['passed']else 1
if __name__=='__main__':raise SystemExit(main())
