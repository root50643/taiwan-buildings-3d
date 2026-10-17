#!/usr/bin/env python3
"""Conservative exact diagnosis of selected ORIGINAL face-normal sample rays.

Does not change, waive or replace the numerical checker's strict_passed result.
Uses exact binary32 coordinates and rational barycentric weights. Parameter t
starts at the original surface point and follows the unnormalised inward face
normal; this is the ideal intended geometric ray, not a bitwise replay of rounded C++ arithmetic.
All forward triangle contacts, including coplanar intervals, are enumerated.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json,math,struct,sys,time
from fractions import Fraction as F
from pathlib import Path

WEIGHTS=[((1,1,1),3),((98,1,1),100),((1,98,1),100),((1,1,98),100),
         ((495,495,10),1000),((10,495,495),1000),((495,10,495),1000),
         ((49,49,2),100),((49,2,49),100),((2,49,49),100)]
def require(c,m):
 if not c:raise RuntimeError(m)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ratio(x):return str(x.numerator) if x.denominator==1 else f'{x.numerator}/{x.denominator}'
def reduce_vector(v):
 g=math.gcd(*v);require(g!=0,'Zero direction/triangle normal');return tuple(x//g for x in v)
def reduce_point(o,q):
 g=math.gcd(q,*o);return tuple(x//g for x in o),q//g

def load(path):
 raw=Path(path).read_bytes();require(len(raw)>=84,'Truncated STL');n=struct.unpack_from('<I',raw,80)[0]
 require(n>0 and len(raw)==84+50*n,'Invalid STL length/count');ts=[]
 for i in range(n):
  vals=struct.unpack_from('<12fH',raw,84+50*i);require(all(math.isfinite(v) for v in vals[:12]),'Nonfinite STL')
  ts.append(tuple(tuple(vals[3+3*j:6+3*j]) for j in range(3)))
 den=max(v.as_integer_ratio()[1] for t in ts for p in t for v in p)
 ints=[tuple(tuple(v.as_integer_ratio()[0]*(den//v.as_integer_ratio()[1]) for v in p) for p in t) for t in ts]
 return raw,ints,den

class Triangle:
 def __init__(self,p):
  self.p=p;self.n=reduce_vector(cross(sub(p[1],p[0]),sub(p[2],p[0])));self.c=dot(self.n,p[0])
  self.lo=tuple(min(x[k] for x in p) for k in range(3));self.hi=tuple(max(x[k] for x in p) for k in range(3))
  self.edge=[]
  for k in range(3):
   w=cross(self.n,sub(p[(k+1)%3],p[k]));self.edge.append((w,dot(w,p[k])))
 def contact(self,o,q,d):
  a=self.c*q-dot(self.n,o);b=dot(self.n,d)*q
  if b:
   t=F(a,b)
   if t<0:return None
   vals=[dot(w,o)*t.denominator+dot(w,d)*q*t.numerator-c*q*t.denominator for w,c in self.edge]
   if min(vals)<0:return None
   return {'lo':t,'hi':t,'coplanar':False,'edge_contact':min(vals)==0,'direction':1 if b>0 else -1}
  if a:return None
  lo,hi=F(0),None
  for w,c in self.edge:
   alpha=dot(w,o)-c*q;beta=dot(w,d)*q
   if beta>0:lo=max(lo,F(-alpha,beta))
   elif beta<0:hi=F(-alpha,beta) if hi is None else min(hi,F(-alpha,beta))
   elif alpha<0:return None
  if hi is None:raise RuntimeError('Bounded nondegenerate triangle generated unbounded coplanar interval')
  if lo>hi:return None
  return {'lo':lo,'hi':hi,'coplanar':True,'edge_contact':True,'direction':0}

class Node:
 def __init__(self,triangles,ids):
  self.lo=tuple(min(triangles[i].lo[k] for i in ids) for k in range(3));self.hi=tuple(max(triangles[i].hi[k] for i in ids) for k in range(3))
  self.ids=None;self.left=None;self.right=None
  if len(ids)<=8:self.ids=ids
  else:
   axis=max(range(3),key=lambda k:self.hi[k]-self.lo[k]);ids.sort(key=lambda i:(sum(p[axis] for p in triangles[i].p),i));m=len(ids)//2
   self.left=Node(triangles,ids[:m]);self.right=Node(triangles,ids[m:])
 def hit(self,o,q,d):
  lo,hi=F(0),None
  for k in range(3):
   if not d[k]:
    if o[k]<self.lo[k]*q or o[k]>self.hi[k]*q:return False
   else:
    a,b=F(self.lo[k]*q-o[k],q*d[k]),F(self.hi[k]*q-o[k],q*d[k])
    if a>b:a,b=b,a
    lo=max(lo,a);hi=b if hi is None else min(hi,b)
    if lo>hi:return False
  return True

class Mesh:
 def __init__(self,triangles,den):
  self.ts=[Triangle(t) for t in triangles];self.den=den;self.tree=Node(self.ts,list(range(len(self.ts))))
 def contacts(self,o,q,d):
  result=[];stack=[self.tree]
  while stack:
   node=stack.pop()
   if not node.hit(o,q,d):continue
   if node.ids is None:stack.extend([node.right,node.left]);continue
   for i in node.ids:
    contact=self.ts[i].contact(o,q,d)
    if contact is not None:result.append(dict(contact,face=i))
  return sorted(result,key=lambda h:(h['lo'],h['hi'],h['face']))
 def status(self,o,q):
  """Exact parity along a reproducibly chosen generic ray, no edge hit allowed."""
  for k in range(1,65):
   d=(1,k,k*k+1);hits=self.contacts(o,q,d)
   if any(h['lo']==0 for h in hits):return 'boundary',{'direction':d,'attempt':k,'boundary_faces':[h['face'] for h in hits if h['lo']==0]}
   if any(h['coplanar'] or h['edge_contact'] for h in hits):continue
   if len({h['lo'] for h in hits})!=len(hits):raise RuntimeError('Coincident distinct triangle-interior parity events')
   inside=len(hits)%2==1
   expected=[(1 if inside else -1)*((-1)**i) for i in range(len(hits))]
   require([h['direction'] for h in hits]==expected,'Generic exact parity crossings do not alternate with the directed mesh')
   return ('inside' if inside else 'outside'),{'direction':d,'attempt':k,'crossing_faces':[h['face'] for h in hits], 'crossing_t':[ratio(h['lo']) for h in hits]}
  raise RuntimeError('No nondegenerate parity direction among 64 deterministic trials; remains unresolved')
 def diagnose(self,face,sample):
  require(0<=face<len(self.ts) and 0<=sample<10,'Invalid original face/sample')
  t=self.ts[face];weights,w=WEIGHTS[sample];o=tuple(sum(weights[i]*t.p[i][k] for i in range(3)) for k in range(3));o,q=reduce_point(o,w)
  d=tuple(-x for x in t.n);hits=self.contacts(o,q,d)
  require(any(h['face']==face and h['lo']==0 and h['hi']==0 and h['direction']==-1 and not h['edge_contact'] for h in hits),'Original source triangle missing or sample not strictly interior')
  breaks=sorted({F(0)}|{h[v] for h in hits for v in ('lo','hi')});require(len(breaks)>1,'No forward surface exit')
  intervals=[]
  for low,high in zip(breaks,breaks[1:]):
   mid=(low+high)/2;po=tuple(o[k]*mid.denominator+d[k]*q*mid.numerator for k in range(3));po,pq=reduce_point(po,q*mid.denominator)
   state,proof=self.status(po,pq)
   intervals.append({'lo':ratio(low),'hi':ratio(high),'state':state,'midpoint_parity_witness':proof})
  after=breaks[-1]+1;po=tuple(o[k]*after.denominator+d[k]*q*after.numerator for k in range(3));po,pq=reduce_point(po,q*after.denominator)
  state,proof=self.status(po,pq);require(state=='outside','Ray after last exact triangle event is not outside')
  intervals.append({'lo':ratio(breaks[-1]),'hi':None,'state':state,'midpoint_parity_witness':proof})
  require(intervals[0]['state']=='inside','Original inward face-normal ray does not immediately enter interior')
  # Conservative first chord stops at the first strictly-positive surface contact,
  # even if the ray only tangentially touches a later surface before re-entering.
  exit_t=breaks[1];squared=exit_t*exit_t*dot(d,d)/F(self.den*self.den)
  outward=self.contacts(o,q,tuple(-x for x in d));positive_out=[h['lo'] for h in outward if h['lo']>0]
  outward_clear=all(v*v*dot(d,d)/F(self.den*self.den)>F(1,10**10) for v in positive_out)
  require(not any(h['hi']>0 and h['lo']==0 for h in outward),'Outward ray begins along another surface')
  contacts=[{'face':h['face'],'t0':ratio(h['lo']),'t1':ratio(h['hi']),'coplanar_interval':h['coplanar'],'edge_or_vertex_contact':h['edge_contact'],'directed_crossing':h['direction']} for h in hits]
  return {'original_face_index':face,'sample_index':sample,'source_barycentric_numerators':list(weights),'source_barycentric_denominator':w,
   'source_point_original_units_exact':[ratio(F(x,q*self.den)) for x in o],
   'inward_direction_integer_lattice':list(d),'lattice_denominator':str(self.den),
   'all_forward_original_triangle_contacts':contacts,'classified_open_intervals':intervals,
   'conservative_first_surface_chord_squared_mm2_exact':ratio(squared),
   'conservative_first_surface_chord_mm_approx':math.sqrt(float(squared)),
   'conservative_first_surface_chord_ge_0p8mm':squared>=F(16,25),
   'outward_origin_offset_1e_minus5mm_has_no_intervening_surface':outward_clear,
   'exact_classification_completed':True,
   'scope':'Surface-origin normal half-line and all its original-triangle contacts. Original numerical flags/strict state remain unchanged; exact parity witnesses classify each open interval, not a global thickness proof.'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--stl',type=Path,required=True);ap.add_argument('--flags',type=Path,required=True);ap.add_argument('--expected-sha256',required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--limit',type=int);args=ap.parse_args()
 require(not args.out.exists(),'Output exists; never overwrite evidence');args.out.mkdir(parents=True)
 report={'completed':False,'all_selected_rays_exactly_classified':False,'original_numerical_strict_passed_unchanged':False,'source_sha256':sha(__file__),'stl_sha256':sha(args.stl),'flags_sha256':sha(args.flags),'optimization_level':sys.flags.optimize,'scope':'Diagnosis only. Original strict flag/report files are never edited.'};start=time.time();rows=[]
 try:
  require(report['stl_sha256']==args.expected_sha256,'STL hash mismatch');raw,triangles,den=load(args.stl);mesh=Mesh(triangles,den)
  flags=json.load(gzip.open(args.flags));seen=set()
  selected=flags if args.limit is None else flags[:args.limit]
  for f in selected:
   key=(f['original_face_index'],f['sample_index']);require(key not in seen,'Duplicate input sample');seen.add(key)
   try:row=mesh.diagnose(*key)
   except Exception as e:row={'original_face_index':key[0],'sample_index':key[1],'exact_classification_completed':False,'error_type':type(e).__name__,'error':str(e)}
   row['original_numerical_reasons']=f['reasons'];rows.append(row)
   print(json.dumps({'done':len(rows),'total':len(selected),'face':key[0],'sample':key[1],'exact_completed':row['exact_classification_completed']}),flush=True)
  with (args.out/'exact-ray-details.jsonl.gz').open('wb') as handle:
   with gzip.GzipFile(filename='',fileobj=handle,mode='wb',mtime=0) as z:
    for row in rows:z.write((json.dumps(row,separators=(',',':'),allow_nan=False)+'\n').encode())
  report.update(completed=True,total_flagged_samples=len(flags),selected_samples=len(rows),all_flagged_samples_selected=len(rows)==len(flags),
   all_selected_rays_exactly_classified=all(r['exact_classification_completed'] for r in rows),
   all_selected_first_chords_ge_0p8mm=all(r.get('conservative_first_surface_chord_ge_0p8mm') is True for r in rows),
   all_selected_outward_offsets_clear=all(r.get('outward_origin_offset_1e_minus5mm_has_no_intervening_surface') is True for r in rows),
   detail_file='exact-ray-details.jsonl.gz',detail_sha256=sha(args.out/'exact-ray-details.jsonl.gz'))
  require(sha(args.stl)==report['stl_sha256'] and sha(args.flags)==report['flags_sha256'],'Original input changed during diagnosis')
 except Exception as e:report.update(completed=False,all_selected_rays_exactly_classified=False,all_selected_first_chords_ge_0p8mm=False,all_selected_outward_offsets_clear=False,error_type=type(e).__name__,error=str(e))
 report['elapsed_seconds']=time.time()-start;(args.out/'exact-ray-summary.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 return 0 if report['completed'] and report['all_selected_rays_exactly_classified'] and 'error' not in report else 1
if __name__=='__main__':raise SystemExit(main())
